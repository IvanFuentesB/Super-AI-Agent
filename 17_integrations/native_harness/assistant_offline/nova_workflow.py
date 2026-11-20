"""Synthetic-only assistant slice using installed Hermes stores and approval RPC.

There is deliberately NO real calendar/email adapter or scheduled automation.
The test renderer is a fixture, not a human decision and not a live grant.
"""
import json,os,uuid
from time import monotonic
from datetime import timedelta
from pathlib import Path
from tools.todo_tool import TodoStore
from hermes_state import SessionDB
from tui_gateway import server_requests
from nova_planner import plan_one,preview_event,verify_preview,StateConflict,digest

class SyntheticCalendar:
 def __init__(self,path,events):
  self.path=Path(path);self.create_calls=0;self.timeout_after_write=False
  self.path.parent.mkdir(parents=True,exist_ok=True)
  if not self.path.exists():self._save(events)
 def _save(self,events):
  temp=self.path.with_suffix('.writing')
  with temp.open('x',encoding='utf-8') as f:
   json.dump({'synthetic':True,'events':events},f,indent=2);f.flush();os.fsync(f.fileno())
  os.replace(temp,self.path)
 def list(self):
  data=json.loads(self.path.read_text(encoding='utf-8'))
  if data.get('synthetic') is not True:raise StateConflict('Not a synthetic calendar')
  return data['events']
 def get(self,event_id):
  found=[e for e in self.list() if e['id']==event_id]
  if len(found)>1:raise StateConflict('Duplicate event ID')
  return found[0] if found else None
 def create(self,event):
  self.create_calls+=1
  prior=self.get(event['id'])
  if prior is not None:
   if prior!=event:raise StateConflict('Event ID collision')
   return prior
  self._save(self.list()+[event])
  if self.timeout_after_write:raise TimeoutError('synthetic uncertain write after commit')
  return event

class Assistant:
 def __init__(self,home,records,calendar,calendar_info):
  if type(calendar) is not SyntheticCalendar:raise StateConflict('Live connectors are not enabled')
  self.home=Path(home);self.home.mkdir(parents=True,exist_ok=True)
  self.db=SessionDB(self.home/'state.db');self.sid='nova-personal-synthetic'
  self.db.create_session(self.sid,'local')
  self.calendar=calendar;self.calendar_info=calendar_info;self.used=set()
  self.todos=TodoStore()
  if not self.db.get_messages(self.sid):
   if len({r['id'] for r in records})!=len(records):raise StateConflict('Duplicate task IDs')
   native={'Done':'completed','Partially Done':'in_progress','Pending':'pending','Uncertain':'pending'}
   self.todos.write([{'id':r['id'],'content':r['title'],'status':native[r['status']]} for r in records])
   self.db.append_message(self.sid,'assistant',json.dumps({'kind':'task_evidence',
       'records':records,'todo_snapshot':self.todos.snapshot(),'synthetic':True}))
  else:self.recall()
 def recall(self):
  for message in reversed(self.db.get_messages(self.sid)):
   data=json.loads(message['content'])
   if data.get('kind')=='task_evidence' and data.get('synthetic') is True:
    snap=data['todo_snapshot'];self.todos.restore(snap['todos'],revision=snap['revision'])
    return data['records']
  raise StateConflict('No authoritative synthetic task evidence; do not recreate')
 def review(self,text):return plan_one(text,self.recall(),self.calendar.list())
 def preview(self,text,start,minutes,now):
  return preview_event(self.review(text),self.calendar_info,self.calendar.list(),start,minutes,now)
 def _verify_selection(self,preview):
  expected={key:self.calendar_info[field] for key,field in
    [('calendar_id','id'),('calendar_name','name'),('color','color'),('timezone','timezone')]}
  if any(preview.get(key)!=value for key,value in expected.items()):
   raise StateConflict('Preview targets a different selected calendar')
 def execute(self,preview,now,timeout=30):
  # Detach the complete JSON tree from caller-owned mutable state before display.
  # The approval description and every subsequent check/write use this snapshot.
  preview=json.loads(json.dumps(preview,sort_keys=True,allow_nan=False))
  started=monotonic()
  self._verify_selection(preview)
  if preview['preview_hash'] in self.used:raise StateConflict('Preview already consumed')
  verify_preview(preview,self.recall(),self.calendar.list(),now)
  response=server_requests.send('approval',self.sid,{
    'request_id':uuid.uuid4().hex,'tool_name':'nova_synthetic_calendar_create',
    'command':'Create one synthetic calendar event',
    'description':json.dumps(preview,sort_keys=True),
    'choices':['once','deny'],'allow_session':False,'allow_permanent':False},timeout=timeout)
  if not response or response.get('choice')!='once' or response.get('all'):
   raise StateConflict('Fresh exact-preview approval not received')
  elapsed=monotonic()-started
  if elapsed>=timeout:raise StateConflict('Decision expired')
  self._verify_selection(preview)
  verify_preview(preview,self.recall(),self.calendar.list(),now+timedelta(seconds=elapsed))
  self.used.add(preview['preview_hash'])
  event={k:v for k,v in preview.items() if k not in ['preview_hash','observed_state_hash','status']}
  event['status']='scheduled'
  write_status='acknowledged'
  try:self.calendar.create(event)
  except TimeoutError:write_status='uncertain_reconciled_by_id'
  actual=self.calendar.get(event['id'])
  if actual!=event:raise StateConflict('Write uncertain or readback mismatch; no blind retry')
  result={'status':'readback_verified','write_status':write_status,'event':actual,
    'preview_hash':preview['preview_hash'],'task_completion_changed':False,'synthetic':True}
  self.db.append_message(self.sid,'assistant',json.dumps({'kind':'execution_result','result':result}))
  if self.saved_results()[-1]!=result:raise StateConflict('Saved-result readback mismatch')
  return result
 def saved_results(self):
  return [d['result'] for m in self.db.get_messages(self.sid)
    if (d:=json.loads(m['content'])).get('kind')=='execution_result']
 def close(self):self.db.close()

def synthetic_renderer(choice,before_answer=None,frames=None):
 """Offline test surface only. Never register on the working gateway process."""
 def render(frame):
  if frames is not None:frames.append(frame)
  if before_answer:before_answer()
  if choice is not None:
   server_requests.resolve_response({'jsonrpc':'2.0','id':frame['id'],
       'result':{'choice':choice,'all':False}})
 server_requests.bind_sinks(render,lambda *_:None)
