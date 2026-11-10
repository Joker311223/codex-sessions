import importlib.machinery,importlib.util,os,tempfile,unittest,sqlite3
from pathlib import Path
from unittest.mock import patch
loader=importlib.machinery.SourceFileLoader('picker',str(Path(__file__).resolve().parents[1]/'codex-sessions'))
spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_rpc_unicode_name_and_preferred_display(self):
  with tempfile.TemporaryDirectory() as directory:
   home=Path(directory)
   stub=home/'codex'
   stub.write_text('''#!/usr/bin/env python3
import sys,json,os
from pathlib import Path
for line in sys.stdin:
 request=json.loads(line)
 if request.get('method')=='initialize': print(json.dumps({'id':request['id'],'result':{}}),flush=True)
 elif request.get('method')=='thread/name/set':
  Path(os.environ['CODEX_HOME'],'request.json').write_text(json.dumps(request['params'],ensure_ascii=False))
  print(json.dumps({'id':request['id'],'result':{}}),flush=True)
''');stub.chmod(0o755)
   with patch.dict(os.environ,{'PATH':str(home)+os.pathsep+os.environ['PATH']}):
    m.rename_session(home,'00000000-0000-4000-8000-000000000001','新的项目标题')
   import json
   self.assertEqual(json.loads((home/'request.json').read_text())['name'],'新的项目标题')
   with sqlite3.connect(home/'state_5.sqlite') as db:
    db.execute('CREATE TABLE threads(id TEXT,title TEXT,name TEXT,cwd TEXT,updated_at INTEGER,archived INTEGER,source TEXT)')
    db.execute("INSERT INTO threads VALUES('id','原始标题','新的项目标题','/tmp',1,0,'cli')")
   self.assertEqual(m.load_sessions(home)[0]['title'],'新的项目标题')
 def test_invalid_name_does_not_launch_a_process(self):
  with patch.object(m.subprocess,'Popen') as start:
   for name in ['', 'x'*201, 'a\nb']:
    with self.assertRaises(ValueError):m.rename_session(Path('/tmp'),'00000000-0000-4000-8000-000000000001',name)
   start.assert_not_called()
if __name__ == '__main__':
    unittest.main()
