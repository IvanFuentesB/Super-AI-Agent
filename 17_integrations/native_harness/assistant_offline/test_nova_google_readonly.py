"""Synthetic tests of the Google Calendar read-only request boundary."""
import sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).parent))
from nova_google_readonly import CalendarReader,ReadConflict

class ReaderTests(unittest.TestCase):
 def make(self,pages):
  svc=Mock()
  svc.calendarList().get().execute.return_value={'id':'study-id','summary':'Learning/Studying',
      'timeZone':'Europe/London','backgroundColor':'#b99aff'}
  svc.events().list().execute.side_effect=pages
  return CalendarReader(svc,'study-id',('study-id',),'Europe/London','#b99aff'),svc
 def read(self,r):return r.snapshot('2026-11-20T00:00:00+00:00','2026-11-21T00:00:00+00:00')
 def event(self):return {'id':'event-1','summary':'Existing study','start':{'dateTime':'2026-11-20T10:00:00Z'},'end':{'dateTime':'2026-11-20T11:00:00Z'},'description':'not exported','attendees':[{'email':'synthetic@example.invalid'}]}
 def test_all_pages_current_query_and_data_minimization(self):
  r,s=self.make([{'items':[],'nextPageToken':'page-2'},{'items':[self.event()]}])
  out=self.read(r)
  self.assertEqual(len(out['events']),1)
  self.assertNotIn('description',out['events'][0]);self.assertNotIn('attendees',out['events'][0])
  calls=[x.kwargs for x in s.events().list.call_args_list if x.kwargs]
  self.assertEqual(len(calls),2);self.assertEqual(calls[1]['pageToken'],'page-2')
  self.assertTrue(calls[0]['singleEvents']);self.assertFalse(calls[0]['showDeleted'])
  self.assertFalse(s.events().insert.called);self.assertFalse(s.events().update.called)
 def test_changed_calendar_identity_rejected(self):
  r,s=self.make([{'items':[]}]);s.calendarList().get().execute.return_value['id']='wrong'
  with self.assertRaises(ReadConflict):self.read(r)
 def test_repeated_pagination_token_is_not_partial_success(self):
  r,s=self.make([{'items':[],'nextPageToken':'same'}]*2)
  with self.assertRaises(ReadConflict):self.read(r)
 def test_all_day_events_retain_calendar_zone(self):
  r,s=self.make([{'items':[{'id':'all-day','start':{'date':'2026-11-20'},'end':{'date':'2026-11-21'}}]}])
  self.assertEqual(self.read(r)['events'][0]['start'],'2026-11-20T00:00:00+00:00')
 def test_naive_query_rejected_before_network(self):
  r,s=self.make([]);s.reset_mock()
  with self.assertRaises(ReadConflict):r.snapshot('2026-11-20T00:00:00','2026-11-21T00:00:00Z')
  self.assertFalse(s.calendarList.called)
 def test_installed_official_client_executes_fixture_requests_offline(self):
  import json
  from googleapiclient.discovery import build
  from googleapiclient.http import HttpMockSequence
  from unittest.mock import patch
  metadata={'id':'study-id','summary':'Learning/Studying','timeZone':'Europe/London','backgroundColor':'#b99aff'}
  responses=[metadata,{'items':[],'nextPageToken':'page-2'},{'items':[self.event()]}]
  transport=HttpMockSequence([({'status':'200'},json.dumps(v).encode()) for v in responses])
  with patch('socket.socket.connect',side_effect=AssertionError('No network permitted')):
   service=build('calendar','v3',http=transport,static_discovery=True,cache_discovery=False)
   reader=CalendarReader(service,'study-id',('study-id',),'Europe/London','#b99aff')
   self.assertEqual(len(self.read(reader)['events']),1)
 def test_each_read_fetches_again_without_cache(self):
  r,s=self.make([{'items':[]},{'items':[self.event()]}])
  self.assertEqual(len(self.read(r)['events']),0)
  self.assertEqual(len(self.read(r)['events']),1)

if __name__=='__main__':unittest.main(verbosity=2)
