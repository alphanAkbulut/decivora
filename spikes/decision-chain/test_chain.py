import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from chain import Chain, applicability, digest, read_target


class TestChain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.chain = Chain(self.root/'chain.db')
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.chain.close)
        self.send('seed',dict(decision='markdown',active=['markdown','security'],
            tasks={'sync':dict(expr='markdown',status='todo'),
                   'export':dict(expr={'any':['markdown','sqlite']},status='todo'),
                   'combined':dict(expr={'all':['markdown','security']},status='todo'),
                   'watch':dict(expr=None,status='todo')},criteria=['migration','rollback']))

    def send(self, command, payload, actor='human', key=None, base=None):
        state=self.chain.snapshot()
        return self.chain.dispatch(command,payload,actor,
                                   state['revision'] if base is None else base,
                                   key or str(state['revision'])+'-'+command)

    def decide(self):
        self.send('ask',dict(question_id='Q_STORE',option_revision=1,
                            source_session='first',options={'A':'markdown','B':'sqlite'}))
        self.send('answer',dict(question_id='Q_STORE',option_revision=1,option='B',
                               source_session='later'))

    def expected(self, criteria=None):
        content=b'new SQLite migration document'
        target=self.root/'bundle.md';target.write_bytes(content)
        payload=dict(artifact_revision=2,ref='fixture-ref-2',path='bundle.md',
                     sha256=__import__('hashlib').sha256(content).hexdigest())
        self.send('expect',payload)
        self.send('observe',read_target(target,2,'fixture-ref-2','bundle.md'),'observer')

    def test_late_answer_and_impact_without_auto_closure(self):
        self.decide()
        state=self.chain.snapshot();self.assertEqual(state['decision'],'sqlite')
        self.assertEqual({v['status'] for v in state['tasks'].values()},{'todo'})
        self.assertEqual(self.chain.preview()['impact'],dict(sync='obsolete_candidate',
            export='retained',combined='obsolete_candidate',watch='review_unknown'))

    def test_agent_cannot_approve(self):
        self.send('ask',dict(question_id='Q',option_revision=1,options={'A':'sqlite'}))
        rev=self.chain.snapshot()['revision']
        with self.assertRaises(PermissionError):
            self.send('answer',dict(question_id='Q',option_revision=1,option='A'),'agent')
        self.assertEqual(self.chain.snapshot()['revision'],rev)

    def test_stale_and_unmatched_answer(self):
        self.send('ask',dict(question_id='Q',option_revision=2,options={'A':'sqlite'}))
        for q,r in [('Q',1),('OTHER',2)]:
            with self.assertRaises(ValueError):self.send('answer',dict(question_id=q,option_revision=r,option='A'))
        self.assertEqual(self.chain.snapshot()['question']['state'],'pending')

    def test_retry_and_conflicting_key(self):
        p=dict(question_id='Q',option_revision=1,options={'A':'sqlite'})
        rev=self.chain.snapshot()['revision']
        a=self.send('ask',p,key='same',base=rev)
        b=self.send('ask',p,key='same',base=rev)
        self.assertEqual(a,b)
        with self.assertRaises(ValueError):self.send('ask',dict(p,option_revision=2),key='same',base=rev)

    def test_explicit_impact_and_or_retention(self):
        self.decide(); preview=self.chain.preview()
        self.send('impact',dict(preview_digest=preview['preview_digest'],
             actions={'sync':'obsolete','export':'retained','combined':'review','watch':'review'}))
        self.assertEqual(self.chain.snapshot()['tasks']['sync']['status'],'obsolete')
        self.assertEqual(self.chain.snapshot()['tasks']['export']['status'],'retained')

    def test_stale_graph_preview(self):
        self.decide();preview=self.chain.preview()
        self.send('add_reason',dict(task='sync',expr={'any':['markdown','sqlite']}))
        with self.assertRaises(ValueError):
            self.send('impact',dict(preview_digest=preview['preview_digest'],actions={'sync':'obsolete'}))

    def test_three_valued_logic(self):
        self.assertIs(applicability({'any':[None,'sqlite']},['sqlite']),True)
        self.assertIs(applicability({'all':[None,'markdown']},['sqlite']),False)
        self.assertIsNone(applicability({'all':[None,'sqlite']},['sqlite']))

    def test_partial_acceptance_not_verified(self):
        self.expected()
        self.send('verify',dict(artifact_revision=2,criteria={'rollback':'passed'}),'verifier')
        self.assertFalse(self.chain.snapshot()['verified'])

    def test_all_pass_then_failure_reopens(self):
        self.expected()
        self.send('verify',dict(artifact_revision=2,criteria={'rollback':'passed','migration':'passed'}),'verifier')
        self.assertTrue(self.chain.snapshot()['verified'])
        self.send('verify',dict(artifact_revision=2,criteria={'migration':'failed'}),'verifier')
        self.assertFalse(self.chain.snapshot()['verified'])

    def test_old_ref_not_current(self):
        self.expected()
        self.send('observe',read_target(self.root/'bundle.md',2,'old-ref','bundle.md'),'observer')
        self.send('verify',dict(artifact_revision=2,criteria={'rollback':'passed','migration':'passed'}),'verifier')
        self.assertEqual(self.chain.snapshot()['observation']['status'],'stale')
        self.assertFalse(self.chain.snapshot()['verified'])

    def test_revision_change_invalidates_evidence(self):
        self.expected()
        self.send('verify',dict(artifact_revision=2,criteria={'rollback':'passed','migration':'passed'}),'verifier')
        a=dict(self.chain.snapshot()['artifact'],artifact_revision=3,ref='new-ref')
        self.send('expect',a)
        self.assertFalse(self.chain.snapshot()['verified'])
        with self.assertRaises(ValueError):
            self.send('verify',dict(artifact_revision=2,criteria={'rollback':'passed'}),'verifier')

    def test_missing_and_denied_distinct(self):
        self.assertEqual(read_target(self.root/'absent',2,'r','p')['availability'],'missing')
        with patch('chain.Path.read_bytes',side_effect=PermissionError):
            self.assertEqual(read_target(self.root/'x',2,'r','p')['availability'],'unknown')

    def test_backup_restore_projection(self):
        self.decide();before=digest(self.chain.snapshot())
        self.assertEqual(self.chain.backup(self.root/'backup.db'),before)
        restored=Chain(self.root/'backup.db')
        try:self.assertEqual(digest(restored.snapshot()),before)
        finally:restored.close()

    def test_append_only_guards(self):
        with self.assertRaises(sqlite3.IntegrityError):self.chain.conn.execute('DELETE FROM events')
        with self.assertRaises(sqlite3.IntegrityError):self.chain.conn.execute("UPDATE events SET payload='{}'")
        self.assertEqual(self.chain.snapshot()['revision'],1)

    def test_empty_ac_not_auto_pass(self):
        c=Chain(self.root/'empty.db')
        try:
            c.dispatch('seed',dict(criteria=[]),'human',0,'seed')
            a=dict(artifact_revision=2,ref='r',path='p',sha256='fixture')
            c.dispatch('expect',a,'human',1,'expect')
            c.dispatch('observe',dict(a,availability='read'),'observer',2,'observe')
            c.dispatch('verify',dict(artifact_revision=2,criteria={}), 'verifier',3,'verify')
            self.assertFalse(c.snapshot()['verified'])
        finally:c.close()
