"""Owner-only POSIX SQLite files; not encryption or protection from the OS owner."""
import os,stat
from pathlib import Path

def restrict_sqlite_files(path):
    if os.name!='posix':return
    for name in (str(path),str(path)+'-wal',str(path)+'-shm',str(path)+'-journal'):
        try:fd=os.open(name,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
        except FileNotFoundError:continue
        try:
            mode=os.fstat(fd).st_mode
            if not stat.S_ISREG(mode):raise OSError('Unsafe storage file.')
            os.fchmod(fd,stat.S_IMODE(mode)&0o600)
        finally:os.close(fd)
