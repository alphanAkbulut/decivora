import json
import os
import sqlite3
from pathlib import Path
from unittest.mock import patch
from helpers import SpikeCase, user, assistant, write_jsonl
from spike0.hook import run, recover_receipts
from spike0.extract import extract, extract_with_coverage
from spike0.pipeline import process_session, catch_up
from spike0.reconcile import Index, reconcile


class TestAuditRegressions(SpikeCase):
    def test_shared_transport_id_different_sources(self):
        a, b = self.mkdir('source-a'), self.mkdir('source-b')
        self.bind((a, 'project-a'), (b, 'project-b'))
        files = [os.path.join(self.tmp, n) for n in ('a.jsonl', 'b.jsonl')]
        for path, cwd, uid in zip(files, (a, b), ('ua', 'ub')):
            write_jsonl(path, [user(uid, 'shared', cwd, 'Karar: ayrı kaynak mesajı kaydedilsin.')])
            run(dict(hook_event_name='SessionStart', session_id='shared', cwd=cwd,
                     transcript_path=path, source='startup'))
        self.assertEqual({r['project'] for r in self.q('SELECT project FROM messages')},
                         {'project-a', 'project-b'})
        self.assertEqual(len(self.q('SELECT * FROM sessions')), 2)

    def test_full_answer_not_prefix(self):
        cwd = self.mkdir('p'); self.bind((cwd, 'p'))
        prefix = 'Aynı cevap başlangıcı yalnız test içindir. ' * 5
        path = os.path.join(self.tmp, 't.jsonl')
        write_jsonl(path, [assistant('old', 's', cwd, prefix + 'ESKİ')])
        run(dict(hook_event_name='Stop', session_id='s', cwd=cwd, transcript_path=path,
                 last_assistant_message=prefix+'YENİ'))
        self.assertEqual(self.q('SELECT present FROM transcript_checks')[0]['present'], 0)

    def test_negation_is_not_duplicate(self):
        cwd = self.mkdir('p'); self.bind((cwd, 'p'))
        base = 'Karar: uzun yaşayan proje görev karar kanıt kayıtları ve kullanıcı tercihleri için SQLite depolama kullanacağız.'
        path = os.path.join(self.tmp, 't.jsonl')
        write_jsonl(path, [user('u1', 's', cwd, base), user('u2', 's', cwd, base.replace('kullanacağız','kullanmayacağız'))])
        self.register('s', path, cwd); process_session(self.conn, 's')
        self.assertEqual(self.q('SELECT recon FROM candidates ORDER BY id')[1]['recon'], 'review_conflict')

    def test_short_answers_preserved_unmatched(self):
        cwd = self.mkdir('p'); self.bind((cwd, 'p'))
        path = os.path.join(self.tmp,'t.jsonl')
        write_jsonl(path,[user('u1','s',cwd,'A'),user('u2','s',cwd,'evet')])
        self.register('s',path,cwd); process_session(self.conn,'s')
        self.assertEqual([r['text'] for r in self.q('SELECT text FROM answer_candidates ORDER BY message_id')],['A','evet'])
        self.assertEqual({r['association'] for r in self.q('SELECT association FROM answer_candidates')},{'unmatched'})

    def test_limited_extraction_visible(self):
        text = '\n'.join('Karar: %d numaralı farklı kayıt üretilecek.'%i for i in range(12))
        rows, coverage = extract_with_coverage('user',text)
        self.assertEqual((len(rows),coverage),(8,'limited'))

    def test_short_claim_and_multi_meaning(self):
        self.assertEqual(extract('assistant','done')[0]['type'],'impl_claim')
        types = {r['type'] for r in extract('assistant','Karar: bu işi tamamlandı olarak işaretledim.')}
        self.assertEqual(types,{'decision','impl_claim'})

    def test_failed_receipt_recovered_without_prompt_text(self):
        cwd=self.mkdir('p'); self.bind((cwd,'p'))
        path=os.path.join(self.tmp,'t.jsonl'); write_jsonl(path,[user('u1','s',cwd,'Karar: kayıt korunacak.')])
        payload=dict(hook_event_name='UserPromptSubmit',session_id='s',cwd=cwd,
                     transcript_path=path,prompt='PRIVATE SYNTHETIC PROMPT')
        with patch('spike0.hook._run',side_effect=sqlite3.OperationalError('synthetic locked')):
            with self.assertRaises(sqlite3.OperationalError): run(payload)
        files=list(Path(self.data,'receipts').glob('*.json'))
        self.assertEqual(len(files),1)
        self.assertNotIn('PRIVATE SYNTHETIC PROMPT',files[0].read_text())
        self.assertEqual(recover_receipts(),1)
        self.assertEqual(len(self.q('SELECT * FROM messages')),1)
        self.assertEqual(recover_receipts(),0)

    def test_delayed_write_without_session_end(self):
        cwd=self.mkdir('p'); self.bind((cwd,'p'))
        path=os.path.join(self.tmp,'t.jsonl');write_jsonl(path,[])
        self.register('s',path,cwd)
        original_sleep=__import__('time').sleep
        written=[]
        def later(delay):
            if not written:
                write_jsonl(path,[user('u1','s',cwd,'Karar: geciken kayıt yakalanacak.')]);written.append(True)
            original_sleep(delay)
        with patch('spike0.pipeline.time.sleep',side_effect=later): catch_up(self.conn,.11,.05)
        self.assertEqual(len(self.q('SELECT * FROM messages')),1)
        self.assertEqual(len(self.q('SELECT * FROM events')),0)
