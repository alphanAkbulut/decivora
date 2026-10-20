"""Source outbox and bounded worker using existing exact model/data/budget grants.

Capture never grants model access. Started-without-finished work is unknown and
is never retried by this worker. Legacy sources remain discoverable read-only.
"""
import time
from collections import Counter
from packages.capture.conversations import ConversationService
from packages.domain.source_event import ContractError


class ConversationQueue:
    def __init__(self, core):
        self.core=core; self.sources=ConversationService(core)

    def view(self, scope, project):
        with self.core.read_snapshot():
            self.core.scope(scope,project); self.core.active(scope,project)
            from packages.capture.source_pages import queue_summary,SOURCE_CAPACITY
            summary=queue_summary(self.core,project)
            for row in summary['items']:row.pop('seq',None)
            return dict(**summary,background_worker_active=False,automatic_dispatch=False,
                        capacity=SOURCE_CAPACITY,scope='selected_project',coverage='saved_sources_only')

    def process(self, scope, project, *, extractor_factory=None, limit=1, source_ids=None, grant_ids=None):
        if type(limit) is not int or not 1<=limit<=10:
            raise ContractError('invalid_request','One to ten sources per explicit worker pass required.')
        if source_ids is not None:
            from packages.domain.project_binding import identifier
            if type(source_ids) is not list or len(source_ids)>1000:raise ContractError('invalid_request','Bounded selected-source allowlist required.')
            for value in source_ids:identifier(value)
            if len(set(source_ids))!=len(source_ids):raise ContractError('invalid_request','Unique selected sources required.')
            source_ids=set(source_ids)
        if grant_ids is not None:
            from packages.domain.project_binding import identifier
            if type(grant_ids) is not list or not 1<=len(grant_ids)<=10 or len(set(grant_ids))!=len(grant_ids):
                raise ContractError('invalid_request','One to ten unique exact grant identifiers required.')
            for value in grant_ids:identifier(value)
            grant_ids=set(grant_ids)
        with self.core.read_snapshot():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            snapshot=self.view(scope,project)
        outcomes=[]; attempted=0
        if extractor_factory is None:
            return dict(attempted=0,outcomes=[],status='Waiting for model',queue=snapshot)
        from packages.capture.source_pages import queue_rows,SOURCE_CAPACITY
        with self.core.read_snapshot():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            pending=queue_rows(self.core,project,pending_only=True,limit=SOURCE_CAPACITY)
        for item in pending:
            if source_ids is not None and item['source_id'] not in source_ids:continue
            if item['status']!='Waiting for model':continue
            # Inspect grants before constructing a transport. No model activation from text.
            with self.core.read_snapshot():
                self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
                source=self.sources._source(project,item['source_id'])
                grants=[g for g in self.sources._rows(project,'conversation_dispatch_authorized')
                        if g['source']==source['id'] and g['sha256']==source['sha256']
                        and g['actor']==scope.principal_id and g['authority_revision']==self.core.authority.revision()
                        and g['expires_at']>time.time() and (grant_ids is None or g['id'] in grant_ids)]
            if not grants:continue
            extractor=extractor_factory(source,grants[-1])
            if extractor is None:continue
            attempted+=1
            try:
                result=self.sources.analyze(scope,project,source['id'],extractor)
                outcomes.append(dict(source_id=source['id'],status=result['status']))
            except ContractError as error:
                # No provider error text or source content in queue diagnostics.
                outcomes.append(dict(source_id=source['id'],status='Stopped',code=error.code))
                break
            # Unknown usage, failed contract or overrun blocks further dispatch in this pass.
            if result.get('status')!='Ready for review' or result.get('budget_status') in ('unknown','overrun'):break
            if attempted>=limit:break
        return dict(attempted=attempted,outcomes=outcomes,status='Pass finished' if attempted else 'Waiting for grant',
                    queue=self.view(scope,project))
