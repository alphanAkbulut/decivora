#!/usr/bin/env python3
# spike0-hook (kurulum/kaldirma bu dosya adini isaret olarak kullanir)
import os
import sys

try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from spike0.hook import main
    rc = main()
except BaseException:  # ne olursa olsun oturumu bozma, stdout'a yazma
    rc = 0
sys.exit(0 if rc is None else rc)
