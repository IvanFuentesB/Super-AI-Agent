"""Synthetic planner acceptance; no real calendar or personal records."""
import sys,unittest
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).parent))
from nova_planner import plan_one,preview_event,StateConflict
NOW=datetime(2026,11,17,12,tzinfo=timezone.utc)
CAL={'id':'synthetic-learning','name':'Learning/Studying','color':'purple','timezone':'Europe/Lisbon'}
TASKS=[{'id':'done','title':'Completed work','status':'Done','revision':1},
 {'id':'scheduled','title':'Existing study','status':'Pending','revision':2},
 {'id':'pending','title':'Pending study','status':'Pending','revision':3},
 {'id':'uncertain','title':'Uncertain study','status':'Uncertain','revision':1}]
EVENTS=[{'id':'existing-id','task_id':'scheduled','calendar_id':CAL['id'],
 'start':'2026-11-18T09:00:00+00:00','end':'2026-11-18T10:00:00+00:00'}]
class PlannerTests(unittest.TestCase):
 def test_done_not_rescheduled(self):
  self.assertEqual(plan_one('Review completed work',TASKS,EVENTS)['decision'],'no_action_done')
 def test_existing_event_reused(self):
  p=plan_one('Review existing study',TASKS,EVENTS)
  self.assertEqual(p['decision'],'already_scheduled');self.assertEqual(p['event_ids'],['existing-id'])
 def test_pending_preview_correct_calendar(self):
  p=plan_one('Review pending study.',TASKS,EVENTS)
  e=preview_event(p,CAL,EVENTS,'2026-11-18T11:00:00+00:00',45,NOW)
  self.assertEqual(e['calendar_name'],'Learning/Studying');self.assertEqual(e['color'],'purple')
  self.assertEqual(e['status'],'proposed');self.assertEqual(e['end'],'2026-11-18T11:45:00+00:00')
 def test_uncertain_not_scheduled(self):
  p=plan_one('Review uncertain study',TASKS,EVENTS)
  with self.assertRaises(StateConflict):preview_event(p,CAL,EVENTS,'2026-11-18T11:00:00+00:00',45,NOW)
 def test_conflict_and_past_rejected(self):
  p=plan_one('Review pending study',TASKS,EVENTS)
  for start in ['2026-11-18T09:30:00+00:00','2026-04-18T11:00:00+00:00']:
   with self.assertRaises(StateConflict):preview_event(p,CAL,EVENTS,start,45,NOW)
 def test_timezone_required_and_dst_nonexistent_rejected(self):
  p=plan_one('Review pending study',TASKS,EVENTS)
  for start in ['2026-11-18T11:00:00','2027-03-28T01:30:00+00:00']:
   with self.assertRaises(StateConflict):preview_event(p,CAL,EVENTS,start,45,NOW)
 def test_duplicate_titles_do_not_guess(self):
  with self.assertRaises(StateConflict):plan_one('Review pending study',TASKS+[dict(TASKS[2],id='other')],EVENTS)
 def test_unselected_request_does_not_schedule_all(self):
  with self.assertRaises(StateConflict):plan_one('Schedule everything',TASKS,EVENTS)
 def test_event_identity_stable(self):
  p=plan_one('Review pending study',TASKS,EVENTS)
  one=preview_event(p,CAL,EVENTS,'2026-11-18T11:00:00+00:00',45,NOW)
  two=preview_event(p,CAL,EVENTS,'2026-11-18T11:00:00+00:00',45,NOW)
  self.assertEqual(one['id'],two['id']);self.assertEqual(one['preview_hash'],two['preview_hash'])
if __name__=='__main__':unittest.main(verbosity=2)
