"""One missing critical regression: unrelated jobs must not erase uncertain submission authority."""
import os
from pathlib import Path
import sys
import json
import importlib.util
import unittest
from datetime import datetime, timezone, timedelta
if len(sys.argv) != 3:
    raise SystemExit("usage: uncertain_submission_regression.py <reviewed-source-snapshot> <fresh-owned-evidence-dir>")
SNAP=Path(sys.argv[1]).resolve()
HERE=Path(sys.argv[2]).resolve()
if HERE.exists() or HERE == SNAP or HERE in SNAP.parents or SNAP in HERE.parents:
    raise SystemExit("evidence directory must be fresh and disjoint from source")
HERE.mkdir(parents=True)
(HERE/'home').mkdir()
(HERE/'tmp').mkdir()
keep={k:os.environ[k] for k in ('SYSTEMROOT','WINDIR','COMSPEC','PATHEXT') if k in os.environ}
os.environ.clear();os.environ.update(keep,HOME=str(HERE/'home'),USERPROFILE=str(HERE/'home'),TEMP=str(HERE/'tmp'),TMP=str(HERE/'tmp'),PATH='' )
assert 'TINYFISH_API_KEY' not in os.environ

def fence(event,args):
    if event in ('socket.__new__','socket.connect','socket.getaddrinfo','subprocess.Popen'):
        raise RuntimeError('No network/provider/child execution in synthetic regression')
sys.addaudithook(fence)
spec=importlib.util.spec_from_file_location('owner_frozen_helpers',SNAP/'01_projects/ghoti_os_app/tests/test_tinyfish_adapter.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
from ghoti_runtime.contracts import Task
from ghoti_runtime.run_store import RunStore
from ghoti_runtime import tinyfish
OBS={}
class DurableUncertainRun(unittest.TestCase):
    def test_unrelated_jobs_cannot_enable_second_post_of_uncertain_intent(self):
        root=HERE/'independent-runtime'
        self.assertFalse(root.exists(),'Never reuse independent fixture')
        store=RunStore(root)
        store.write('ghoti_provider_config/tinyfish.json',{'schema':'ghoti_tinyfish_approval/1','enabled':True,'approval_request_id':'approval-review-synthetic','approved_hosts':['docs.tinyfish.ai'],'expires_at':'2099-01-01T00:00:00Z','max_runs_per_day':1,'max_concurrent_runs':1})
        fake=t.Fake(start=[tinyfish.TransportError('SyntheticTimeout'),t.resp(200,{'run_id':'synthetic-second-run'})])
        clock=t.Clock()
        tf=tinyfish.TinyFish(store,transport=fake,api_key=t.KEY,clock=clock,sleep=clock.sleep)
        first=tf.start(t.URL,t.QUESTION)
        self.assertEqual(first['status'],'SUBMISSION_UNCONFIRMED')
        first_path=store.path('ghoti_runtime_runs/'+first['task_id']+'.json')
        first_bytes=first_path.read_bytes()
        for i in range(100):
            task=Task(task_id=f'task-review-local-{i:03}',title='Unrelated local task',intent='Synthetic local-only record',created_at=(datetime.now(timezone.utc)+timedelta(seconds=i+1)).isoformat(),created_by='review:local')
            store.save_task(task)
        window=tf._provider_records()
        again=tf.start(t.URL,t.QUESTION)
        OBS.update(first_state=first['status'],original_record_still_exists=first_path.is_file(),original_record_unchanged=first_path.read_bytes()==first_bytes,unrelated_local_records=100,provider_records_seen_in_window=len(window),max_concurrent_runs=1,max_runs_per_day=1,second_status=again['status'],mock_start_POSTs=len(fake.of('start')),live_calls=0,real_RunStore=True)
        (HERE/'independent-observation.json').write_text(json.dumps(OBS,indent=2)+'\n',encoding='utf-8')
        self.assertIn(again['status'],{'DUPLICATE_REFUSED','BUSY','DAILY_LIMIT'},'Durable uncertain submission must still block another metered start')
        self.assertEqual(len(fake.of('start')),1,'Never emit a second start while the first submission remains unresolved')
with (HERE/'independent-window.log').open('w',encoding='utf-8') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DurableUncertainRun))
summary={'executed':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors),'failures':len(result.failures),'errors':len(result.errors),'observed':OBS}
(HERE/'independent-window-result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary));sys.exit(0 if result.wasSuccessful() else 1)
