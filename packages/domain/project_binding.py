"""T05 deterministic project/session binding core.

AccessScope is supplied by the trusted caller, not parsed from source text.
This in-memory component is not a login service or durable event store.
"""
from dataclasses import dataclass
import re

from .source_event import ContractError, ID_PATTERN, validate_source_event
from dataclasses import asdict


def identifier(value):
    if type(value) is not str or re.fullmatch(ID_PATTERN, value) is None:
        raise ContractError('invalid_identity', 'Invalid bounded identifier.')
    return value


@dataclass(frozen=True, slots=True)
class AccessScope:
    workspace_id: str
    principal_id: str
    readable_projects: frozenset[str]
    writable_projects: frozenset[str]

    def __post_init__(self):
        identifier(self.workspace_id)
        identifier(self.principal_id)
        for group in (self.readable_projects, self.writable_projects):
            if type(group) is not frozenset:
                raise ContractError('invalid_scope', 'Access scope must be immutable.')
            for project_id in group:
                identifier(project_id)


@dataclass(frozen=True, slots=True)
class SessionKey:
    provider: str
    account_id: str
    session_id: str
    source_epoch: str

    def __post_init__(self):
        for value in (self.provider, self.account_id, self.session_id, self.source_epoch):
            identifier(value)


@dataclass(frozen=True, slots=True)
class Project:
    project_id: str
    name: str
    revision: int
    archived: bool = False


@dataclass(frozen=True, slots=True)
class Binding:
    key: SessionKey
    project_id: str
    revision: int
    bound_by: str


@dataclass(frozen=True, slots=True)
class Resolution:
    status: str
    reason: str
    project_id: str | None = None
    binding_revision: int | None = None


class ProjectRegistry:
    """Single-caller in-memory state; no persistence/concurrent transaction guarantee."""
    def __init__(self, workspace_id):
        self.workspace_id = identifier(workspace_id)
        self._projects = {}
        self._bindings = {}

    def _scope(self, scope, project_id=None, write=False):
        if type(scope) is not AccessScope or scope.workspace_id != self.workspace_id:
            raise ContractError('forbidden', 'Operation is outside the authorized scope.')
        if project_id is not None:
            identifier(project_id)
            allowed = scope.writable_projects if write else scope.readable_projects
            if project_id not in allowed:
                raise ContractError('forbidden', 'Operation is outside the authorized scope.')

    @staticmethod
    def _name(name):
        if type(name) is not str or not name.strip() or len(name) > 256:
            raise ContractError('invalid_name', 'Project name is missing or too long.')
        try:
            name.encode('utf-8')
        except UnicodeError:
            raise ContractError('invalid_name', 'Project name must be valid Unicode.') from None
        return name

    def create(self, scope, project_id, name):
        self._scope(scope, project_id, write=True)
        name = self._name(name)
        if project_id in self._projects:
            raise ContractError('project_conflict', 'Project identity is already registered.')
        project = Project(project_id, name, 1)
        self._projects[project_id] = project
        return project

    def get(self, scope, project_id):
        self._scope(scope, project_id)
        if project_id not in self._projects:
            raise ContractError('project_unavailable', 'Selected project is unavailable.')
        return self._projects[project_id]

    def list(self, scope):
        self._scope(scope)
        return tuple(self._projects[key] for key in sorted(self._projects)
                     if key in scope.readable_projects)

    def update(self, scope, project_id, *, base_revision, name=None, archived=None):
        self._scope(scope, project_id, write=True)
        previous = self._projects.get(project_id)
        if previous is None:
            raise ContractError('project_unavailable', 'Selected project is unavailable.')
        if type(base_revision) is not int or base_revision != previous.revision:
            raise ContractError('stale_base', 'Project revision changed; refresh before updating.')
        if archived is not None and type(archived) is not bool:
            raise ContractError('invalid_state', 'Archived state must be boolean.')
        project = Project(project_id, previous.name if name is None else self._name(name),
                          previous.revision + 1, previous.archived if archived is None else archived)
        self._projects[project_id] = project
        return project

    def bind(self, scope, key, project_id, *, base_revision):
        self._scope(scope, project_id, write=True)
        if type(key) is not SessionKey:
            raise ContractError('invalid_session', 'Explicit source session key required.')
        project = self._projects.get(project_id)
        if project is None or project.archived:
            raise ContractError('project_unavailable', 'Selected project is unavailable.')
        history = self._bindings.get(key, ())
        current_revision = history[-1].revision if history else 0
        if type(base_revision) is not int or base_revision != current_revision:
            raise ContractError('stale_binding', 'Binding revision changed; refresh before binding.')
        # Moving a session requires authority over its previous project as well.
        if history:
            self._scope(scope, history[-1].project_id, write=True)
        binding = Binding(key, project_id, current_revision + 1, scope.principal_id)
        self._bindings[key] = (*history, binding)
        return binding

    def history(self, scope, key):
        self._scope(scope)
        if type(key) is not SessionKey:
            raise ContractError('invalid_session', 'Explicit source session key required.')
        history = self._bindings.get(key, ())
        # Do not leak even the existence of revisions from another project.
        for binding in history:
            self._scope(scope, binding.project_id)
        return history

    def resolve(self, scope, key, event, *, binding_revision):
        self._scope(scope)
        if type(key) is not SessionKey:
            raise ContractError('invalid_session', 'Explicit source session key required.')
        # Revalidate even directly constructed dataclass instances.
        try:
            event = validate_source_event(asdict(event))
        except (TypeError, AttributeError):
            raise ContractError('invalid_input', 'Validated source event required.') from None
        self._scope(scope, event.project_id)
        if key.session_id != event.session_id:
            return Resolution('quarantined', 'session_mismatch')
        if type(binding_revision) is not int or binding_revision < 1:
            return Resolution('quarantined', 'binding_revision_required')
        history = self._bindings.get(key, ())
        if not history:
            return Resolution('quarantined', 'project_unbound')
        # Explicit revision, never newest timestamp/name or a fallback to current binding.
        binding = next((b for b in history if b.revision == binding_revision), None)
        if binding is None:
            return Resolution('quarantined', 'binding_revision_unknown')
        self._scope(scope, binding.project_id)
        if event.project_id != binding.project_id:
            return Resolution('quarantined', 'project_mismatch')
        project = self._projects[binding.project_id]
        if project.archived:
            return Resolution('quarantined', 'project_archived')
        return Resolution('bound', 'explicit_binding', binding.project_id, binding.revision)
