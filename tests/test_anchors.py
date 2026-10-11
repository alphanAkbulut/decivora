import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('anchors',Path(__file__).resolve().parents[1]/'scripts/check_anchors.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class TestAnchors(unittest.TestCase):
    def test_unicode_duplicates_and_fences(self):
        self.assertEqual(module.anchors('# Karar — geçmiş\n# Karar — geçmiş\n```\n# Fake\n```'),
                         {'karar--geçmiş','karar--geçmiş-1'})

    def test_missing_same_page_and_cross_file_fragment(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'a.md').write_text('# A\n[bad](#missing)\n[bad](b.md#missing)\n[good](b.md#başlık)')
            (root/'b.md').write_text('# Başlık')
            n,errors=module.check(root);self.assertEqual((n,len(errors)),(3,2))

    def test_explicit_id(self):
        self.assertIn('custom',module.anchors('<a id="custom"></a>'))
