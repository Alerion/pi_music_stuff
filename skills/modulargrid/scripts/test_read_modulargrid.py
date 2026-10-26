"""Offline synthetic fixtures: no private rack data and no network requests."""
import json
import sys
import unittest

sys.dont_write_bytecode = True
from read_modulargrid import parse_module, parse_rack, validate_url

URL = "https://modulargrid.net/e/racks/view/123"


def fixture(ids=("10", "11"), count=2, rack_id="123"):
    # Two separate instances of the same model; never deduplicate by model ID.
    modules = [{"id": "7", "name": "Test & VCO", "slug": "test-vco", "te": "8",
                "Vendor": {"name": "Maker"},
                "ModulesRack": {"id": id_, "row": "1", "col": str(col)}}
               for id_, col in zip(ids, (9, 1))]
    payload = {"rack": {"Rack": {"id": rack_id, "name": "Test", "rows": "1", "te": "84"},
                        "Module": modules}}
    return f'<span id="qtyModules">{count}</span><script data-mg-json="rtd" type="application/json">{json.dumps(payload)}</script>'


class ReaderTests(unittest.TestCase):
    def test_preserves_instances_and_sorts(self):
        result = parse_rack(fixture(), URL)
        self.assertEqual([m["instance_id"] for m in result["modules"]], ["11", "10"])
        self.assertEqual([m["module_id"] for m in result["modules"]], ["7", "7"])
        self.assertEqual(result["modules"][0]["url"], "https://modulargrid.net/e/test-vco")

    def test_missing_data_and_count_mismatch(self):
        for html in ("<h1>Login</h1>", fixture(count=3), fixture(ids=(), count=0)):
            with self.subTest(html=html), self.assertRaises(ValueError):
                parse_rack(html, URL)

    def test_wrong_rack_and_duplicate_instance(self):
        for html in (fixture(rack_id="999"), fixture(ids=("10", "10"))):
            with self.subTest(html=html), self.assertRaises(ValueError):
                parse_rack(html, URL)

    def test_url_validation(self):
        for url in ("http://modulargrid.net/e/racks/view/123",
                    "https://modulargrid.net.evil.test/e/racks/view/123",
                    "https://modulargrid.net/e/racks/view/123?x=1"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url, "rack")

    def test_extracts_only_module_details(self):
        html = ('<div id="module-details"><p>Dual <strong>VCO</strong> &amp; LFO<br>Two channels</p>'
                '<a href="https://maker.test/manual">Manual</a></div><p>Marketplace and prices</p>')
        result = parse_module(html, "https://modulargrid.net/e/test-vco")
        self.assertIn("VCO & LFO", result["description"])
        self.assertNotIn("Marketplace", result["description"])
        self.assertEqual(result["description_links"], ["https://maker.test/manual"])

    def test_rejects_missing_module_description(self):
        with self.assertRaises(ValueError):
            parse_module("<p>Blocked</p>", "https://modulargrid.net/e/test-vco")


if __name__ == "__main__":
    unittest.main()
