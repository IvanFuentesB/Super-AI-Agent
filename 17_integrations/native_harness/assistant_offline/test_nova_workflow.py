"""Integration tests with real installed Hermes stores/approval transport.
Only the calendar and human renderer are synthetic fixtures.
"""
import sys,os,tempfile,unittest,json
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,sys.argv.pop(1))  # installed Hermes source, explicitly supplied
sys.path.insert(0,str(Path(__file__).parent))
from nova_workflow import Assistant,SyntheticCalendar,synthetic_renderer
from nova_planner import StateConflict
from test_nova_planner import TASKS,EVENTS,CAL,NOW

class WorkflowTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.old=os.environ.get('HERMES_HOME');os.environ['HERMES_HOME']=str(self.root)
  self.cal=SyntheticCalendar(self.root/'calendar.json',EVENTS)
  self.a=Assistant(self.root,TASKS,self.cal,CAL)
 def tearDown(self):
  self.a.close();self.tmp.cleanup()
  if self.old is None:os.environ.pop('HERMES_HOME',None)
  else:os.environ['HERMES_HOME']=self.old
 def preview(self):return self.a.preview('Review pending study','2026-11-18T11:00:00+00:00',45,NOW)
 def test_native_task_recall_and_no_reschedule(self):
  self.assertEqual(self.a.recall()[0]['status'],'Done')
  self.assertEqual(self.a.review('Review completed work')['decision'],'no_action_done')
  self.assertEqual(self.a.review('Review existing study')['event_ids'],['existing-id'])
 def test_denied_or_permanent_or_missing_decision_does_not_write(self):
  for decision in ['deny','always','session',None]:
   synthetic_renderer(decision)
   with self.assertRaises(StateConflict):self.a.execute(self.preview(),NOW,timeout=.01)
  self.assertEqual(len(self.cal.list()),1)
 def test_exact_preview_execution_readback_and_replay(self):
  synthetic_renderer('once');p=self.preview();result=self.a.execute(p,NOW)
  self.assertEqual(result['status'],'readback_verified')
  self.assertEqual(self.a.saved_results()[-1],result)
  self.assertEqual(len(self.cal.list()),2)
  with self.assertRaises(StateConflict):self.a.execute(p,NOW)
  self.assertEqual(len(self.cal.list()),2)
 def test_other_calendar_rejected_even_with_recomputed_preview_hash(self):
  from nova_planner import digest
  p=self.preview();p['calendar_id']='other-calendar'
  p['id']='nova'+digest({'task':p['task_id'],'calendar':p['calendar_id']})[:40]
  p['preview_hash']=digest({k:v for k,v in p.items() if k!='preview_hash'})
  synthetic_renderer('once')
  with self.assertRaises(StateConflict):self.a.execute(p,NOW)
  self.assertEqual(self.cal.create_calls,0)
 def test_displayed_snapshot_is_not_changed_by_caller_during_approval(self):
  from nova_planner import digest
  p=self.preview();frames=[]
  original_start=p['start']
  def mutate_caller_preview():
   p['start']='2026-11-18T12:00:00+00:00'
   p['end']='2026-11-18T12:45:00+00:00'
   p['preview_hash']=digest({k:v for k,v in p.items() if k!='preview_hash'})
  synthetic_renderer('once',before_answer=mutate_caller_preview,frames=frames)
  result=self.a.execute(p,NOW)
  shown=json.loads(frames[0]['params']['description'])
  self.assertEqual(result['event']['start'],original_start)
  self.assertEqual(result['event']['start'],shown['start'])
  self.assertEqual(result['preview_hash'],shown['preview_hash'])
  self.assertEqual(self.cal.get(result['event']['id']),result['event'])
 def test_selected_calendar_change_while_waiting_is_rejected(self):
  def change_calendar():self.a.calendar_info=dict(CAL,id='different-calendar')
  synthetic_renderer('once',before_answer=change_calendar)
  with self.assertRaises(StateConflict):self.a.execute(self.preview(),NOW)
  self.assertEqual(self.cal.create_calls,0)
 def test_expired_decision_rejected_after_wait(self):
  from unittest.mock import patch
  synthetic_renderer('once')
  with patch('nova_workflow.monotonic',side_effect=[100,131],create=True):
   with self.assertRaises(StateConflict):self.a.execute(self.preview(),NOW,timeout=30)
  self.assertEqual(self.cal.create_calls,0)
 def test_reopen_recalls_existing_state_without_recreating(self):
  synthetic_renderer('once');self.a.execute(self.preview(),NOW)
  self.a.close()
  self.a=Assistant(self.root,[],self.cal,CAL)
  self.assertEqual(self.a.review('Review pending study')['decision'],'already_scheduled')
  self.assertEqual(len(self.cal.list()),2)
 def test_uncertain_write_reads_before_any_retry(self):
  synthetic_renderer('once');self.cal.timeout_after_write=True
  result=self.a.execute(self.preview(),NOW)
  self.assertEqual(result['write_status'],'uncertain_reconciled_by_id')
  self.assertEqual(self.cal.create_calls,1)
 def test_state_change_during_approval_rejected(self):
  p=self.preview()
  synthetic_renderer('once',before_answer=lambda:self.cal.create({
   'id':'conflict','task_id':'other','start':p['start'],'end':p['end']}))
  with self.assertRaises(StateConflict):self.a.execute(p,NOW)
  self.assertNotIn(p['id'],[e['id'] for e in self.cal.list()])
 def test_tampered_preview_rejected_before_prompt(self):
  p=self.preview();p['calendar_id']='wrong-calendar'
  with self.assertRaises(StateConflict):self.a.execute(p,NOW)
if __name__=='__main__':unittest.main(verbosity=2)
