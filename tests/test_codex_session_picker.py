import importlib.machinery
import importlib.util
from pathlib import Path
import shlex
import sqlite3
import tempfile
import unittest

loader = importlib.machinery.SourceFileLoader('picker', str(Path(__file__).resolve().parents[1]/'codex-sessions'))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        with sqlite3.connect(self.home/'state_5.sqlite') as db:
            db.execute('CREATE TABLE threads(id TEXT, title TEXT, cwd TEXT, updated_at INTEGER, archived INTEGER, source TEXT)')
            for index, (archived, source) in enumerate([(0,'cli'),(1,'cli'),(0,'vscode'),(0,'exec'),(0,'subAgent')], 1):
                db.execute('INSERT INTO threads VALUES(?,?,?,?,?,?)', (f'00000000-0000-4000-8000-{index:012}', '测试 '+str(index), '/tmp/path with space/$(no-execution)', index, archived, source))
    def tearDown(self):
        self.tmp.cleanup()
    def test_default_sources_and_archive_filter(self):
        rows=m.load_sessions(self.home)
        self.assertEqual([r['source'] for r in rows], ['vscode','cli'])
        self.assertTrue(all(not r['archived'] for r in rows))
    def test_including_archive_and_cli_only(self):
        rows=m.load_sessions(self.home, archived=True, cli_only=True)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['archived'],1)
    def test_command_shell_quoting_and_archived_prefix(self):
        rows=m.load_sessions(self.home, archived=True, cli_only=True)
        normal=m.resume_command(rows[1])
        self.assertEqual(shlex.split(normal),['codex','resume',rows[1]['id'],'--cd',rows[1]['cwd']])
        self.assertTrue(m.resume_command(rows[0]).startswith('codex unarchive '+rows[0]['id']+' && '))
    def test_read_only_and_control_character_display(self):
        path=self.home/'state_5.sqlite'
        original=path.read_bytes()
        m.load_sessions(self.home, archived=True)
        self.assertEqual(original,path.read_bytes())
        self.assertEqual(m.clean('标题\x1b\n'), '标题  ')
        self.assertEqual(m.clip('中文ABC',5),'中文A')

if __name__ == '__main__':
    unittest.main()
