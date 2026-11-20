"""One-item, evidence-first planning. No network, calendar writes or scheduler.

Gateway audio and text must pass through the same review parser. Explicit
selection is required; unknown/ambiguous requests and uncertain state stop.
"""
from datetime import datetime,timedelta,timezone
import hashlib,json,re
from zoneinfo import ZoneInfo

class StateConflict(ValueError):pass

def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def state_hash(records,events):
 return digest({'tasks':sorted(records,key=lambda r:r['id']),
                'events':sorted(events,key=lambda e:e['id'])})

def _words(value):return ' '.join(re.findall(r'\w+',value.casefold()))

def plan_one(request,records,events):
 if not isinstance(request,str) or not request.casefold().startswith('review '):
  raise StateConflict('Select one item with Review <item title>; no bulk scheduling.')
 title=_words(request[7:])
 matches=[r for r in records if _words(r['title'])==title]
 if len(matches)!=1:raise StateConflict('Missing or ambiguous existing task; do not recreate it.')
 task=matches[0]
 status=task.get('status','Uncertain')
 if status not in ['Done','Partially Done','Pending','Uncertain']:status='Uncertain'
 existing=[e['id'] for e in events if e.get('task_id')==task['id'] and e.get('status')!='cancelled']
 decisions={'Done':'no_action_done','Partially Done':'review_remaining_work',
            'Pending':'propose_selected_pending','Uncertain':'needs_evidence'}
 decision=decisions[status]
 if existing and status!='Done':decision='already_scheduled'
 return {'task_id':task['id'],'title':task['title'],'classification':status,
         'decision':decision,'event_ids':existing,'task_revision':task['revision'],
         'observed_state_hash':state_hash(records,events),
         'deadline':task.get('deadline'),'evidence':task.get('evidence',[])}

def _aware(value):
 try:dt=datetime.fromisoformat(value)
 except (TypeError,ValueError) as error:raise StateConflict('Invalid timestamp') from error
 if dt.tzinfo is None or dt.utcoffset() is None:raise StateConflict('Timezone/offset required')
 return dt

def preview_event(plan,calendar,events,start,minutes,now):
 if plan['decision']!='propose_selected_pending':raise StateConflict('Task is not selected pending work')
 if calendar.get('name')!='Learning/Studying' or calendar.get('color')!='purple':
  raise StateConflict('Study events require the selected purple Learning/Studying calendar')
 if not calendar.get('id'):raise StateConflict('Calendar ID must be resolved, not just its display name')
 if type(minutes) is not int or not 1<=minutes<=240:raise StateConflict('Invalid duration')
 if now.tzinfo is None:raise StateConflict('Timezone-aware current time required')
 zone=ZoneInfo(calendar['timezone']);begin=_aware(start)
 # A caller-supplied wall time + offset must describe a real instant in this
 # calendar's zone. This rejects nonexistent DST wall times and wrong offsets.
 local=begin.astimezone(zone)
 if local.replace(tzinfo=None)!=begin.replace(tzinfo=None) or local.utcoffset()!=begin.utcoffset():
  raise StateConflict('Offset/wall-time does not match calendar timezone')
 if begin<=now:raise StateConflict('Historical timetable cannot become a current event')
 finish=(begin.astimezone(timezone.utc)+timedelta(minutes=minutes)).astimezone(zone)
 if plan.get('deadline') and finish>_aware(plan['deadline']):raise StateConflict('After recorded deadline')
 for event in events:
  if event.get('status')=='cancelled':continue
  if event.get('task_id')==plan['task_id']:raise StateConflict('Task already has an event')
  if begin<_aware(event['end']) and finish>_aware(event['start']):
   raise StateConflict('Conflicts with an existing commitment')
 event={'id':'nova'+digest({'task':plan['task_id'],'calendar':calendar['id']})[:40],
        'task_id':plan['task_id'],'task_revision':plan['task_revision'],'title':plan['title'],
        'calendar_id':calendar['id'],'calendar_name':calendar['name'],'color':calendar['color'],
        'timezone':calendar['timezone'],'start':local.isoformat(),'end':finish.isoformat(),
        'status':'proposed','observed_state_hash':plan['observed_state_hash']}
 event['preview_hash']=digest(event)
 return event

def verify_preview(preview,records,events,now):
 signed={k:v for k,v in preview.items() if k!='preview_hash'}
 if digest(signed)!=preview.get('preview_hash'):raise StateConflict('Preview changed')
 if preview['observed_state_hash']!=state_hash(records,events):raise StateConflict('State changed since preview')
 plan=plan_one('Review '+preview['title'],records,events)
 begin,end=_aware(preview['start']),_aware(preview['end'])
 minutes=int((end-begin).total_seconds()/60)
 current=preview_event(plan,{'id':preview['calendar_id'],'name':preview['calendar_name'],
    'color':preview['color'],'timezone':preview['timezone']},events,preview['start'],minutes,now)
 if current!=preview:raise StateConflict('Fresh preview differs')
 return True
