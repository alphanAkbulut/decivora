"""Authorized read-only dialogue lineage; not a second transcript or error log.

Messages remain in the existing redacted source store. No provider calls, raw
model responses, reasoning, approvals or canonical mutations are generated.
"""
from packages.capture.conversations import ConversationService
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.domain.task_workflow import TaskWorkflowService


class DialogueTraceService:
    def __init__(self, core):
        self.core = core

    def view(self, scope, project, *, source_ids):
        if (type(source_ids) is not list or not 1 <= len(source_ids) <= 25 or
                any(type(s) is not str for s in source_ids) or len(set(source_ids)) != len(source_ids)):
            raise ContractError('invalid_request', 'Select one to twenty-five unique sources.')
        for source_id in source_ids:
            identifier(source_id)
        with self.core.read_snapshot():
            self.core.scope(scope, project)
            sources = ConversationService(self.core)
            applications = sources._related(project, 'conversation_candidates_applied', source_ids)
            entries = []
            for source_id in source_ids:
                item = sources.view(scope, project, source_id=source_id)['imports'][0]
                source = item['source']; capture = source.get('capture', {})
                links = []
                for receipt in applications:
                    if receipt['source'] != source_id:
                        continue
                    for candidate, record in receipt['result']['temp_ids'].items():
                        links.append(dict(candidate_id=candidate, record_id=record, action='created'))
                    for attached in receipt.get('attached', []):
                        for match in attached['matches']:
                            if match['relation'] == 'exact_duplicate':
                                links.append(dict(candidate_id=attached['candidate'], record_id=match['record_id'], action='source_attached'))
                statuses = []
                for proposal in item['status_changes']:
                    current = TaskWorkflowService(self.core).view(scope, project, proposal['task_id'])
                    statuses.append(dict(proposal_id=proposal['id'], task_id=proposal['task_id'],
                        reported_stage=proposal['stage'], current_stage=current['stage'],
                        review_state=proposal['state'], stale=proposal['stale'],
                        verification_passed=current['verification']['passed'],
                        review_history=proposal['history']))
                analysis = item['analysis'] or {}
                entries.append(dict(source_id=source_id, source_sha256=source['sha256'],
                    source_kind=source['source_kind'], capture_id=capture.get('id'),
                    thread_id=capture.get('thread_id'), turn_id=capture.get('turn_id'),
                    item_id=capture.get('item_id'), observed_actor=capture.get('observed_actor'),
                    received_at=source['received_at'], text_excerpt=source['text'][:256],
                    text_truncated=len(source['text'])>256,
                    analysis_status=item['status'], context_sha256=analysis.get('context_sha256'),
                    candidate_ids=[c['id'] for c in item['candidates']],
                    record_links=links, status_proposals=statuses))
            return dict(entries=entries, order='caller_selected_not_proven_conversation_chronology',
                source_subset=True, model_calls=0, canonical_mutations=0,
                full_dialogue_capture_verified=False)
