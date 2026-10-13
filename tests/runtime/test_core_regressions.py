"""Critical regression cases for the existing local/manual workspace profile."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from packages.domain.project_binding import SessionKey
from packages.domain.source_event import ContractError,validate_source_event
from packages.storage.project_store import canonical,digest
from packages.storage.workspace import Workspace

ROOT=Path(__file__).resolve().parents[2]

class CriticalCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'core.sqlite'
        self.core=Workspace(self.path,'workspace',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority
        a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2'}),active=True,base_revision=1)
        self.owner=a.issue_scope('owner')
        for p in ('p1','p2'):self.core.create_project(self.owner,p,p)
        self.key=SessionKey('manual','account','session_fixture','epoch')
        self.event=validate_source_event(dict(json.loads((ROOT/'examples/runtime/source-event.json').read_text()),project_id='p1'))
        self.body=dict(type='Task',title='Test',description='Synthetic source')

    def assert_code(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)

    def plan(self):return self.core.plan(self.owner,'p1','change',[dict(op='create',id='a',body=self.body)])

    def archive(self,value,revision):self.core.update_project(self.owner,'p1',base_revision=revision,name='p1',archived=value)

    def narrow(self,project):
        a=self.core.authority
        a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({project}),writable=frozenset({project}),active=True,base_revision=a.revision())
        self.owner=a.issue_scope('owner')

    def test_archive_blocks_new_and_preapproved_changes(self):
        plan=self.plan();approval=self.core.approve(self.owner,plan)
        self.archive(True,1)
        self.assert_code('project_archived',self.plan)
        self.assert_code('project_archived',lambda:self.core.approve(self.owner,plan))
        self.assert_code('project_archived',lambda:self.core.apply(self.owner,plan,approval))
        self.assertEqual(self.core.records(self.owner,'p1')['records'],[])
        self.archive(False,2)
        self.assert_code('stale_base',lambda:self.core.apply(self.owner,plan,approval))
        fresh=self.plan();self.core.apply(self.owner,fresh,self.core.approve(self.owner,fresh))

    def test_archive_keeps_receipt_but_fences_worker_after_reopening(self):
        self.core.bind(self.owner,self.key,'p1',0)
        receipt=self.core.receive(self.owner,self.key,self.event,1)
        lease=self.core.lease(self.owner,'p1',now=0)
        self.archive(True,1)
        self.assert_code('project_archived',lambda:self.core.lease(self.owner,'p1',now=1))
        self.assert_code('project_archived',lambda:self.core.finish(self.owner,lease,{},now=1))
        self.assertEqual(self.core.source(self.owner,receipt['seq'])['project'],'p1')
        self.archive(False,2)
        self.assert_code('stale_lease',lambda:self.core.finish(self.owner,lease,{},now=2))
        fresh=self.core.lease(self.owner,'p1',now=2)
        self.core.finish(self.owner,fresh,{},now=3)
        self.assertTrue(self.core.frontier(self.owner,self.key,'p1')['complete'])

    def test_authority_refresh_cannot_reauthorize_old_worker_lease(self):
        self.core.bind(self.owner,self.key,'p1',0);self.core.receive(self.owner,self.key,self.event,1)
        lease=self.core.lease(self.owner,'p1',now=0)
        self.narrow('p1')
        self.assert_code('stale_lease',lambda:self.core.finish(self.owner,lease,{},now=1))
        fresh=self.core.lease(self.owner,'p1',now=31)
        self.core.finish(self.owner,fresh,{},now=32)

    def test_quarantine_source_and_frontier_respect_claimed_project_acl(self):
        receipt=self.core.receive(self.owner,self.key,self.event,1)
        self.narrow('p2')
        self.assert_code('forbidden',lambda:self.core.source(self.owner,receipt['seq']))
        self.assert_code('forbidden',lambda:self.core.frontier(self.owner,self.key,'p2'))

    def test_mismatch_quarantine_also_respects_pinned_binding_acl(self):
        self.core.bind(self.owner,self.key,'p2',0)
        receipt=self.core.receive(self.owner,self.key,self.event,1)
        self.narrow('p1')
        self.assert_code('forbidden',lambda:self.core.source(self.owner,receipt['seq']))
        self.assert_code('forbidden',lambda:self.core.frontier(self.owner,self.key,'p1'))

    def test_backup_cannot_copy_project_created_after_authorized_snapshot(self):
        self.core.db.execute('PRAGMA journal_mode=WAL')
        with Workspace(self.path,'workspace') as other:
            original=self.core.scope;changed=False
            def race(scope,project=None,**kwargs):
                nonlocal changed
                original(scope,project,**kwargs)
                if project=='p2' and not changed:
                    changed=True;a=other.authority
                    a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p1','p2','p3'}),writable=frozenset({'p1','p2','p3'}),active=True,base_revision=a.revision())
                    other.create_project(a.issue_scope('owner'),'p3','Not authorized by original scope')
            target=Path(self.temp.name)/'backup.sqlite'
            with patch.object(self.core,'scope',race):manifest=self.core.backup(self.owner,target)
            self.assertTrue(changed)
            self.assertEqual(set(manifest['projection_digests']),{'p1','p2'})
            with sqlite3.connect(target) as db:self.assertEqual(db.execute('SELECT count(*) FROM projects').fetchone()[0],2)

    def test_replay_rejects_version_gap_and_keeps_previous_projection(self):
        plan=self.plan();result=self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
        before=self.core.projection_digest(self.owner,'p1');rid=result['temp_ids']['a']
        op=dict(op='update',id=rid,base_version=9,body=self.body)
        self.core.db.execute('INSERT INTO events(workspace,project,stream,version,kind,payload) VALUES (?,?,?,?,?,?)',('workspace','p1',rid,10,'update',canonical(op)))
        self.assert_code('unsupported_event',lambda:self.core.replay(self.owner,'p1'))
        self.assertEqual(self.core.projection_digest(self.owner,'p1'),before)

    def test_replay_does_not_silently_accept_update_of_missing_record(self):
        op=dict(op='update',id='missing',base_version=1,body=self.body)
        self.core.db.execute('INSERT INTO events(workspace,project,stream,version,kind,payload) VALUES (?,?,?,?,?,?)',('workspace','p1','missing',2,'update',canonical(op)))
        self.assert_code('unsupported_event',lambda:self.core.replay(self.owner,'p1'))

    def test_restore_rejects_projection_inconsistent_with_canonical_events(self):
        plan=self.plan();self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
        # Deliberate physical corruption fixture: self-consistent manifest alone is insufficient.
        self.core.db.execute('UPDATE records SET body=?',(canonical(dict(self.body,title='Corrupted projection')),))
        backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        target=Path(self.temp.name)/'restored.sqlite'
        self.assert_code('backup_invalid',lambda:Workspace.restore(backup,target,manifest))
        self.assertFalse(target.exists());self.assertFalse(Path(str(target)+'-wal').exists())
        self.assertTrue(backup.exists())

    def test_failed_restore_closes_connection_and_preserves_existing_target(self):
        backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        target=Path(self.temp.name)/'restored.sqlite'
        original=Workspace.projection_digest;closed=Workspace.close;calls=[]
        def fail(core,*args):raise RuntimeError('Injected read failure')
        def closing(core):calls.append(core);closed(core)
        with patch.object(Workspace,'projection_digest',fail),patch.object(Workspace,'close',closing):
            with self.assertRaises(RuntimeError):Workspace.restore(backup,target,manifest)
        self.assertEqual(len(calls),1);self.assertFalse(target.exists())
        target.write_text('Keep existing user data')
        with self.assertRaises(FileExistsError):Workspace.restore(backup,target,manifest)
        self.assertEqual(target.read_text(),'Keep existing user data')

    def test_backup_checks_quarantine_acl_even_without_registered_project(self):
        a=self.core.authority
        a.replace_grant(self.owner,'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2','p3'}),active=True,base_revision=a.revision())
        self.owner=a.issue_scope('owner')
        self.core.receive(self.owner,self.key,replace(self.event,project_id='p3'),1)
        target=Path(self.temp.name)/'forbidden.sqlite'
        self.assert_code('forbidden',lambda:self.core.backup(self.owner,target))
        self.assertFalse(target.exists())

    def test_backup_rejects_pending_write_transaction_instead_of_hanging(self):
        target=Path(self.temp.name)/'pending.sqlite'
        with self.core.transaction():
            self.assert_code('backup_busy',lambda:self.core.backup(self.owner,target))
        self.assertFalse(target.exists())

    def test_failed_backup_connection_removes_new_partial_file(self):
        target=Path(self.temp.name)/'failed.sqlite'
        with patch('packages.storage.workspace.sqlite3.connect',side_effect=sqlite3.OperationalError('Injected open failure')):
            with self.assertRaises(sqlite3.OperationalError):self.core.backup(self.owner,target)
        self.assertFalse(target.exists())

    def test_readonly_project_backup_can_restore_without_granting_write(self):
        a=self.core.authority
        a.replace_grant(self.owner,'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1'}),active=True,base_revision=a.revision())
        self.owner=a.issue_scope('owner')
        backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.temp.name)/'restore.sqlite',manifest) as restored:
            owner=restored.authority.issue_scope('owner')
            self.assertEqual(restored.records(owner,'p2')['records'],[])
            self.assert_code('forbidden',lambda:restored.plan(owner,'p2','forbidden',[dict(op='create',id='a',body=self.body)]))

if __name__=='__main__':unittest.main()
