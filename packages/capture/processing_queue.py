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

    def process(self, scope, project, *, extractor_factory=None, limit=1):
        if type(limit) is not int or not 1<=limit<=10:
            raise ContractError('invalid_request','One to ten sources per explicit worker pass required.')
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
            if item['status']!='Waiting for model':continue
            # Inspect grants before constructing a transport. No model activation from text.
            with self.core.read_snapshot():
                self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
                source=self.sources._source(project,item['source_id'])
                grants=[g for g in self.sources._rows(project,'conversation_dispatch_authorized')
                        if g['source']==source['id'] and g['sha256']==source['sha256']
                        and g['actor']==scope.principal_id and g['authority_revision']==self.core.authority.revision()
                        and g['expires_at']>time.time()]
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
