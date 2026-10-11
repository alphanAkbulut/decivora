"""P0 read-only observation of one explicitly selected file, never a directory scan.

Caller selects a root/path and expected content hash. This is not production IAM,
Git history verification, or task acceptance. POSIX no-follow/openat is required.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat


def observe(root, relative_path, expected_sha256, *, max_bytes=131072):
    if not isinstance(expected_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise ValueError('expected SHA256 required')
    if type(max_bytes) is not int or not 1 <= max_bytes <= 131072:
        raise ValueError('invalid byte ceiling')
    if not isinstance(relative_path, str) or not relative_path or '\\' in relative_path or '\0' in relative_path:
        raise ValueError('invalid selected path')
    parts = relative_path.split('/')
    if any(p in ('', '.', '..') for p in parts) or len(parts) > 32:
        raise ValueError('relative path must stay inside selected root')
    selected = Path(root)
    if not selected.is_absolute():
        raise ValueError('explicit absolute root required')
    result = dict(observer='local-file-p0-1', selected_root=str(selected), path=relative_path,
        expected_sha256=expected_sha256, observed_sha256=None, bytes_read=None,
        status='unknown', reason=None, task_verified=False, canonical_mutations=0,
        model_calls=0, remote_upload_verified=False, authority='caller_selected_not_authenticated')
    if not hasattr(os, 'O_NOFOLLOW') or os.open not in os.supports_dir_fd:
        result['reason'] = 'unsupported_safe_open'
        return result
    handles = []
    try:
        # No-follow each directory component: traversal cannot follow a swapped symlink.
        fd = os.open(selected, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(fd)
        for component in parts[:-1]:
            fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            handles.append(fd)
        parent_fd = fd
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
        handles.append(fd)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            result['reason'] = 'not_regular_file'
            return result
        if before.st_size > max_bytes:
            result['reason'] = 'byte_limit'
            return result
        data = bytearray()
        while len(data) <= max_bytes:
            block = os.read(fd, min(16384, max_bytes + 1 - len(data)))
            if not block:
                break
            data.extend(block)
        after = os.fstat(fd)
        signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        try:
            current = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
        except OSError:
            result['reason'] = 'changed_during_read'
            return result
        if len(data) > max_bytes:
            result['reason'] = 'byte_limit'
        elif signature(before) != signature(after) or signature(after) != signature(current) or len(data) != after.st_size:
            result['reason'] = 'changed_during_read'
        else:
            actual = hashlib.sha256(data).hexdigest()
            result.update(observed_sha256=actual, bytes_read=len(data),
                status='observed_match' if actual == expected_sha256 else 'mismatch',
                file_identity=dict(device=after.st_dev, inode=after.st_ino,
                                   mtime_ns=after.st_mtime_ns, size=after.st_size))
    except FileNotFoundError:
        result.update(status='missing', reason='selected_file_or_root_missing')
    except PermissionError:
        result['reason'] = 'permission_denied'
    except OSError:
        result['reason'] = 'unsafe_or_unavailable_path'
    finally:
        for fd in reversed(handles):
            os.close(fd)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--path', required=True)
    p.add_argument('--expected-sha256', required=True)
    args = p.parse_args()
    print(json.dumps(observe(args.root, args.path, args.expected_sha256), indent=2))
