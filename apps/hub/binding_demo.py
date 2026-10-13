"""Fixed synthetic T05a demonstration, in-memory and without external access."""
from dataclasses import replace

from packages.domain.project_binding import AccessScope, ProjectRegistry, SessionKey
from packages.domain.source_event import ContractError, FORMAT, validate_source_event


def run_demo():
    registry = ProjectRegistry('workspace_demo')
    owner = AccessScope('workspace_demo', 'owner_demo', frozenset({'p1', 'p2'}), frozenset({'p1', 'p2'}))
    reader = AccessScope('workspace_demo', 'reader_demo', frozenset({'p1'}), frozenset())
    registry.create(owner, 'p1', 'Aynı isim')
    registry.create(owner, 'p2', 'Aynı isim')
    key = SessionKey('manual', 'account_demo', 'session_demo', 'epoch_demo')
    event = validate_source_event(dict(format=FORMAT, event_id='event_demo', project_id='p1',
        session_id=key.session_id, source_revision=1, actor_type='human', text='Sentetik kaynak.', synthetic=True))
    unbound = registry.resolve(owner, key, event, binding_revision=1)
    registry.bind(owner, key, 'p1', base_revision=0)
    initial = registry.resolve(reader, key, event, binding_revision=1)
    registry.bind(owner, key, 'p2', base_revision=1)
    historical = registry.resolve(owner, key, event, binding_revision=1)
    mismatched = registry.resolve(owner, key, event, binding_revision=2)
    current = registry.resolve(owner, key, replace(event, project_id='p2'), binding_revision=2)
    try:
        registry.get(reader, 'p2')
    except ContractError as error:
        denied = error.code
    else:
        raise RuntimeError('Expected cross-project denial failed.')
    return dict(status='passed_synthetic_binding_demo', storage='in_memory',
        principal_source='fixed_fixture_not_authentication', same_name_distinct_ids=True,
        unbound=unbound.reason, initial=initial.project_id, historical=historical.project_id,
        new_binding_old_source=mismatched.reason, current=current.project_id,
        cross_project_read=denied, durable_receipt=False, human_approval=False,
        source_capture=False, canonical_mutations=0, model_dispatches=0)
