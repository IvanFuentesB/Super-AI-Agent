"""Default-unconnected Google Calendar discovery-client reader.

Supply an independently authorized official Calendar v3 service; this module
never loads credentials, opens OAuth, refreshes tokens explicitly or writes.
Binding arguments must come from trusted host configuration, not model input.
A returned snapshot is not a completion ledger or approval. Live mutation remains
unavailable in nova_workflow.Assistant. No account connection occurs on import.
"""
from datetime import datetime,time,timezone
from zoneinfo import ZoneInfo

READ_SCOPES=('https://www.googleapis.com/auth/calendar.events.readonly',
             'https://www.googleapis.com/auth/calendar.calendarlist.readonly')
class ReadConflict(ValueError):pass

def aware(value):
 try:result=datetime.fromisoformat(value)
 except (ValueError,TypeError) as error:raise ReadConflict('Invalid timestamp') from error
 if result.tzinfo is None:raise ReadConflict('Timezone required')
 return result

def instant(value,zone):
 if 'dateTime' in value:return aware(value['dateTime']).isoformat()
 if 'date' in value:
  return datetime.combine(datetime.fromisoformat(value['date']).date(),time(),ZoneInfo(zone)).isoformat()
 raise ReadConflict('Missing event time')

class CalendarReader:
 def __init__(self,service,selected_id,conflict_ids,expected_timezone,approved_purple_rgb):
  if not selected_id or selected_id=='primary':raise ReadConflict('Exact selected calendar ID required')
  self.service=service;self.selected_id=selected_id
  self.ids=tuple(dict.fromkeys((selected_id,*conflict_ids)))
  if not 1<=len(self.ids)<=20 or any(not isinstance(x,str) or not x or x=='primary' for x in self.ids):
   raise ReadConflict('Bounded exact conflict-calendar IDs required')
  ZoneInfo(expected_timezone)
  self.zone=expected_timezone;self.rgb=approved_purple_rgb.lower()
  if not self.rgb.startswith('#') or len(self.rgb)!=7:raise ReadConflict('Explicit approved color required')
 def snapshot(self,start,end):
  begin,finish=aware(start),aware(end)
  if finish<=begin:raise ReadConflict('Invalid query interval')
  events=[];identities=set();selected=None
  for calendar_id in self.ids:
   meta=self.service.calendarList().get(calendarId=calendar_id).execute()
   if meta.get('id')!=calendar_id:raise ReadConflict('Calendar identity mismatch')
   zone=meta.get('timeZone');ZoneInfo(zone)
   if calendar_id==self.selected_id:
    if (meta.get('summary')!='Learning/Studying' or zone!=self.zone
        or meta.get('backgroundColor','').lower()!=self.rgb):
     raise ReadConflict('Selected calendar name, timezone or approved color changed')
    selected={'id':calendar_id,'name':'Learning/Studying','timezone':zone,'color':'purple'}
   page_token=None;seen_tokens=set()
   for _ in range(20):
    args={'calendarId':calendar_id,'timeMin':begin.isoformat(),'timeMax':finish.isoformat(),
          'singleEvents':True,'showDeleted':False,'maxResults':2500,'timeZone':zone}
    if page_token:args['pageToken']=page_token
    page=self.service.events().list(**args).execute()
    for item in page.get('items',[]):
     if item.get('status')=='cancelled':continue
     identity=(calendar_id,item.get('id'))
     if not identity[1] or identity in identities:raise ReadConflict('Missing or repeated event ID')
     identities.add(identity)
     event={'id':item['id'],'calendar_id':calendar_id,'summary':item.get('summary',''),
            'start':instant(item['start'],zone),'end':instant(item['end'],zone)}
     if aware(event['end'])<=aware(event['start']):raise ReadConflict('Invalid event interval')
     # Only a duplicate-prevention hint, never completion authority.
     task_id=item.get('extendedProperties',{}).get('private',{}).get('novaTaskId')
     if isinstance(task_id,str) and task_id:event['task_id']=task_id
     events.append(event)
    page_token=page.get('nextPageToken')
    if not page_token:break
    if page_token in seen_tokens:raise ReadConflict('Repeated pagination token')
    seen_tokens.add(page_token)
   else:raise ReadConflict('Query exceeds bounded pagination; no partial result')
  return {'calendar':selected,'events':events,'queried_calendar_ids':list(self.ids),
          'query_start':begin.isoformat(),'query_end':finish.isoformat(),
          'observed_at':datetime.now(timezone.utc).isoformat(),'read_only':True}
