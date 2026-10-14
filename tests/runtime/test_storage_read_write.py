"""Local service WAL startup and reader/writer isolation, with real HTTP/SQLite."""
from pathlib import Path
import json,shutil,sqlite3,tempfile,threading,unittest
from urllib.request import Request,urlopen
from apps.local_ui.server import make_server,LocalApp
from packages.storage.workspace import Workspace

class LocalReadWriteTests(unittest.TestCase):
    def test_backup_includes_uncheckpointed_wal_and_restores_offline(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'app.sqlite';app=LocalApp(path)
            with app.core() as core:
                owner=core.authority.issue_scope('local_owner')
                core.db.execute('PRAGMA wal_autocheckpoint=0')
                plan=core.plan(owner,'personal','wal_task',[dict(op='create',id='t',body=dict(type='Task',title='WAL-only task',description='Synthetic'))])
                core.apply(owner,plan,core.approve(owner,plan))
                self.assertGreater(Path(str(path)+'-wal').stat().st_size,0)
                # A bare main-file copy misses the commit; SQLite backup must not.
                main_only=Path(folder)/'unsafe-main-only.sqlite'
                shutil.copyfile(path,main_only)
                with sqlite3.connect(main_only) as copied:
                    self.assertEqual(copied.execute('SELECT count(*) FROM records').fetchone()[0],0)
                projection=core.projection_digest(owner,'personal')
                event_count=core.db.execute('SELECT count(*) FROM events').fetchone()[0]
                backup=Path(folder)/'backup.sqlite';manifest=core.backup(owner,backup)
                with Workspace.restore(backup,Path(folder)/'restored.sqlite',manifest) as restored:
                    scope=restored.authority.issue_scope('local_owner')
                    self.assertEqual(restored.projection_digest(scope,'personal'),projection)
                    self.assertEqual(restored.db.execute('SELECT count(*) FROM events').fetchone()[0],event_count)
                    self.assertEqual(manifest['external_dispatches'],0)

    def test_startup_enables_wal_and_preserves_existing_workspace(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'app.sqlite';app=LocalApp(path)
            app.command(dict(action='create_task',title='Preserved task',description='Synthetic scope'))
            before=app.state()
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute('PRAGMA journal_mode').fetchone()[0],'wal')
                db.execute('PRAGMA journal_mode=DELETE')
            reopened=LocalApp(path)
            self.assertEqual(reopened.storage_journal_mode,'wal')
            self.assertEqual(reopened.state()['snapshot'],before['snapshot'])
            self.assertEqual(reopened.state()['tasks'],before['tasks'])

    def test_old_read_snapshot_does_not_block_http_read_or_committed_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'app.sqlite';server=make_server(path);app=server.app
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            reader=sqlite3.connect(path,isolation_level=None);reader.execute('BEGIN')
            self.assertEqual(reader.execute('SELECT count(*) FROM records').fetchone()[0],0)
            initialized=threading.Event();writer_done=threading.Event();errors=[]
            original_core=app.core
            def delayed_core():
                core=original_core();initialized.set()
                if not writer_done.wait(4):core.close();raise AssertionError('Writer could not finish with old reader held')
                return core
            app.core=delayed_core
            def writer():
                if not initialized.wait(4):errors.append('Reader not initialized');return
                try:
                    # Use the original core path to avoid waiting on ourselves.
                    with original_core() as core:
                        owner=core.authority.issue_scope('local_owner')
                        plan=core.plan(owner,'personal','concurrent', [dict(op='create',id='t',body=dict(type='Task',title='Concurrent task',description='Synthetic commit'))])
                        core.apply(owner,plan,core.approve(owner,plan))
                except Exception as error:errors.append(type(error).__name__)
                finally:writer_done.set()
            worker=threading.Thread(target=writer);worker.start()
            try:
                with urlopen(Request(server.origin+'/api/state',headers={'Cookie':'decivora_session='+app.cookie}),timeout=6) as response:
                    self.assertEqual(response.status,200);state=json.loads(response.read())
                self.assertEqual(errors,[]);self.assertEqual(len(state['tasks']),1)
                # Existing snapshot still sees pre-write data; a new request sees the commit.
                self.assertEqual(reader.execute('SELECT count(*) FROM records').fetchone()[0],0)
                self.assertNotEqual(state['tasks'][0]['lane'],'Done')
            finally:
                reader.execute('ROLLBACK');reader.close();writer_done.set();worker.join(5)
                server.shutdown();server.server_close();thread.join(3)

if __name__=='__main__':unittest.main()
