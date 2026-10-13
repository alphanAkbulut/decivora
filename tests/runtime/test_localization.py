"""Catalog completeness and source/translation boundaries; no provider needed."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class LocalizationTests(unittest.TestCase):
    def setUp(self):
        source=(ROOT/'apps/local_ui/locales.js').read_text()
        self.catalogs=json.loads(source.split('window.DecivoraCatalogs = ',1)[1].rstrip().removesuffix(';'))
    def test_all_locales_have_complete_nonempty_messages_and_matching_placeholders(self):
        self.assertEqual(set(self.catalogs),{'en','tr','es','pt-BR','ar'})
        for code,catalog in self.catalogs.items():
            self.assertEqual(set(catalog),set(self.catalogs['en']),code)
            for key,value in catalog.items():
                self.assertTrue(value.strip(),(code,key))
                self.assertEqual(set(re.findall(r'\{\w+\}',value)),set(re.findall(r'\{\w+\}',self.catalogs['en'][key])),(code,key))
    def test_declared_ui_keys_resolve_and_language_layer_has_no_network(self):
        from html.parser import HTMLParser
        catalogs=self.catalogs
        class Keys(HTMLParser):
            def handle_starttag(self,tag,attrs):
                for name,value in attrs:
                    if name.startswith('data-i18n'):assert value in catalogs['en'],value
        Keys().feed((ROOT/'apps/local_ui/index.html').read_text())
        app=(ROOT/'apps/local_ui/app.js').read_text()
        for key in re.findall(r't\("([^"]+)"',app):self.assertIn(key,self.catalogs['en'])
        layer=(ROOT/'apps/local_ui/i18n.js').read_text()
        self.assertNotRegex(layer,r'\b(fetch|XMLHttpRequest|WebSocket)\s*\(')
