import importlib.machinery,importlib.util,json,tempfile,time,unittest
from pathlib import Path
loader=importlib.machinery.SourceFileLoader('picker',str(Path(__file__).resolve().parents[1]/'codex-sessions'))
spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.home=Path(self.tmp.name);self.now=time.time()
  self.rows=[{'id':name,'rollout_path':str(self.home/(name+'.jsonl'))} for name in ['a','b']]
  for row in self.rows:Path(row['rollout_path']).write_text('')
  self.tracker=m.ExecutionFollower();self.tracker.watermark=self.now
  self.assertIsNone(self.tracker.poll(self.rows))
 def tearDown(self):self.tmp.cleanup()
 def event(self,name,kind,at):
  row=next(r for r in self.rows if r['id']==name)
  event={'timestamp':m.datetime.datetime.fromtimestamp(at,m.datetime.timezone.utc).isoformat(),'type':'event_msg','payload':{'type':kind,'started_at':at if kind=='task_started' else at-10,'completed_at':at if kind=='task_complete' else None}}
  with open(row['rollout_path'],'a') as f:f.write(json.dumps(event)+'\n')
 def test_start_then_complete_both_follow_once(self):
  self.event('a','task_started',self.now+1)
  self.assertEqual(self.tracker.poll(self.rows)['id'],'a')
  self.assertIsNone(self.tracker.poll(self.rows))
  self.event('b','task_started',self.now+2)
  self.assertEqual(self.tracker.poll(self.rows)['id'],'b')
  self.event('a','task_complete',self.now+3)
  event=self.tracker.poll(self.rows)
  self.assertEqual((event['id'],event['state']),('a','已完成'))
 def test_metadata_and_log_output_do_not_refocus(self):
  self.event('a','task_complete',self.now-100)
  self.assertIsNone(self.tracker.poll(self.rows))
  with open(self.rows[0]['rollout_path'],'a') as f:f.write(json.dumps({'type':'event_msg','payload':{'type':'token_count'}})+'\n')
  self.assertIsNone(self.tracker.poll(self.rows))
 def test_simultaneous_changes_follow_latest_event(self):
  self.event('a','task_complete',self.now+2);self.event('b','task_started',self.now+1)
  self.assertEqual(self.tracker.poll(self.rows)['id'],'a')
 def test_new_session_is_detected(self):
  row={'id':'c','rollout_path':str(self.home/'c.jsonl')};self.rows.append(row)
  self.event('c','task_started',self.now+1)
  self.assertEqual(self.tracker.poll(self.rows)['id'],'c')
if __name__ == '__main__':
    unittest.main()
