import importlib.machinery,importlib.util,tempfile,unittest,json
from pathlib import Path
loader=importlib.machinery.SourceFileLoader('picker',str(Path(__file__).resolve().parents[1]/'codex-sessions'))
spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'session.jsonl'
 def tearDown(self):self.tmp.cleanup()
 def write(self,events):
  self.path.write_text('\n'.join(json.dumps({'timestamp':ts,'type':'event_msg','payload':p}) for ts,p in events)+'\n')
  return {'rollout_path':str(self.path),'updated_at':2000000000}
 def test_success_then_new_turn_does_not_reuse_old_finish(self):
  events=[('2026-11-10T07:00:00Z',{'type':'task_started','turn_id':'a','started_at':1794294000}),('2026-11-10T07:01:00Z',{'type':'task_complete','turn_id':'a','started_at':1794294000,'completed_at':1794294060,'duration_ms':60000})]
  row=self.write(events);times=m.session_times(row)
  self.assertEqual(times['finish'],1794294060);self.assertEqual(times['duration_ms'],60000)
  events.append(('2026-11-10T07:02:00Z',{'type':'task_started','turn_id':'b','started_at':1794294120}))
  row=self.write(events);times=m.session_times(row)
  self.assertEqual(times['state'],'未结束');self.assertIsNone(times['finish']);self.assertEqual(times['start'],1794294120)
 def test_interrupted_is_not_success(self):
  row=self.write([('2026-11-10T07:00:00Z',{'type':'task_started','turn_id':'a'}),('2026-11-10T07:01:00Z',{'type':'turn_aborted','turn_id':'a'})])
  times=m.session_times(row);self.assertEqual(times['state'],'已中断');self.assertIsNone(times['finish']);self.assertIsNotNone(times['start'])
 def test_legacy_completion_uses_event_timestamp(self):
  row=self.write([('2026-11-10T07:01:00Z',{'type':'task_complete'})])
  self.assertEqual(m.session_times(row)['finish'],1794294060)
 def test_missing_and_partial_records_are_unknown(self):
  self.path.write_text('[]\n{"bad":\n')
  self.assertEqual(m.session_times({'rollout_path':str(self.path)})['state'],'未知')
  self.assertIsNone(m.session_times({'updated_at':2000000000})['finish'])
if __name__ == '__main__':
    unittest.main()
