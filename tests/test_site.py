from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.anchors = []
        self.assets = []
        self.images = []
        self.commands = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            href = attrs.get('href', '')
            if href.startswith('#') and len(href) > 1:
                self.anchors.append(href[1:])
        if tag == 'img':
            self.images.append(attrs)
            self.assets.append(attrs['src'])
        if tag == 'script' and 'src' in attrs:
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon'):
            self.assets.append(attrs['href'])
        if 'data-copy' in attrs:
            self.commands.append(attrs['data-copy'])


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.page = Page()
        self.page.feed((ROOT / 'docs/index.html').read_text())

    def test_navigation_and_assets(self):
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
        for anchor in self.page.anchors:
            self.assertIn(anchor, self.page.ids)
        for asset in self.page.assets:
            self.assertTrue((ROOT / 'docs' / asset).is_file(), asset)
        self.assertTrue((ROOT / 'docs/.nojekyll').exists())

    def test_screenshot_has_accessible_privacy_description(self):
        self.assertTrue(self.page.images)
        for image in self.page.images:
            self.assertIn('脱敏', image.get('alt', ''))
            self.assertNotIn('clipboard-', image['src'])
        self.assertTrue(all('clipboard-' not in str(p) for p in (ROOT / 'docs').rglob('*')))

    def test_copyable_commands_match_installation(self):
        self.assertIn('codex-sessions --archived', self.page.commands)
        self.assertIn('git clone https://github.com/Joker311223/codex-sessions.git\ncd codex-sessions\n./install.sh', self.page.commands)


if __name__ == '__main__':
    unittest.main()
