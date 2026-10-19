#!/usr/bin/env python3
"""Interactive local credential setup; no network call and no key in arguments/logs."""
import argparse
import getpass
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DEFAULT = ROOT.parent / 'decivora-local-data' / 'secrets' / 'openai-api-key'


def save_key(path, value):
    if not value.startswith('sk-') or not 20 <= len(value) <= 512 or any(c.isspace() for c in value):
        raise ValueError('Anahtar biçimi geçersiz; anahtar görüntülenmedi.')
    path = Path(path)
    # Refuse repository-contained credentials, including ignored directories.
    if path.resolve().is_relative_to(ROOT):
        raise ValueError('Anahtar repo dışında saklanmalı.')
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.parent.lstat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or
            stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError('Yalnız kullanıcıya açık özel klasör gerekli.')
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'w') as handle:
        handle.write(value + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, default=DEFAULT)
    parser.add_argument('--status', action='store_true')
    args = parser.parse_args()
    if args.status:
        from packages.capture.openai_transport import read_key
        try:
            read_key(args.path)
        except FileNotFoundError:
            print('API anahtarı henüz kaydedilmedi. Ağ çağrısı yapılmadı.')
            return 1
        print('Özel yerel anahtar dosyası hazır. API erişimi/bakiye doğrulanmadı; ağ çağrısı yapılmadı.')
        return 0
    if not sys.stdin.isatty():
        print('Gizli giriş için bu yardımcıyı kendi Terminal pencerende çalıştır.')
        return 1
    if args.path.exists() or args.path.is_symlink():
        print('Anahtar dosyası zaten var; üzerine yazılmadı. --status ile kontrol edebilirsin.')
        return 1
    print('OpenAI anahtarını buraya yapıştır. Yazdıkların görünmeyecek; sohbete gönderme.')
    value = getpass.getpass('API key: ')
    try:
        save_key(args.path, value.strip())
    finally:
        value = None
    print('Kaydedildi: ' + str(args.path))
    print('Dosya repo dışında, yalnız senin kullanıcına açık; şifreli kasa değildir. API çağrısı yapılmadı.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print('Kurulum tamamlanmadı: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
