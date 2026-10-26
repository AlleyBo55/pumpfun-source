"""Passive registry-time/retained deployment-time witness, no network or executable inputs."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda p:json.loads(p.read_text())
def analyze():
 unit=J(P/'current-unit-analysis.json');expected={(r['name'],r['version']):r['archive_sha256']for r in unit['observed_registry_packages'].values()};assert len(expected)==176
 http=J(P/'http-receipts.json');assert len(http)==176 and len({(r['name'],r['version'])for r in http})==176
 finish=J(P/'completion.json');assert finish['requested']==finish['observed']==176 and finish['all_200']and finish['all_locked_checksums_match']and finish['automatic_retries']==0
 req=J(P/'deployment-time/request.json');raw=(P/'deployment-time/response.raw').read_bytes();rpc=J(P/'deployment-time/result.json');assert rpc['status']==200 and rpc['response_sha256']==H(raw)and rpc['response_bytes']==len(raw)and rpc['request_sha256']==H((P/'deployment-time/request.json').read_bytes())
 responses={r['id']:r for r in json.loads(raw)};assert set(responses)=={r['id']for r in req}and responses['genesis']['result']=='5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d'
 captures={n:J(P/'captures'/f'{n}.json')for n in ['pump','pump_amm','pump_fees','mayhem']}
 for n,c in captures.items():assert c['genesis_hash']==responses['genesis']['result']and next(x['params'][0]for x in req if x['id']==n)==c['last_deploy_slot']
 epoch=responses['pump']['result'];assert epoch==1792432022
 cutoff=datetime.datetime.fromtimestamp(epoch,datetime.timezone.utc);rows=[]
 for r in http:
  name,version=r['name'],r['version'];assert r['url']=='https://crates.io/api/v1/crates/'+name+'/'+version and r['status']==200 and r['attempts']==1
  raw=(P/r['file']).read_bytes();assert len(raw)==r['bytes']and H(raw)==r['sha256'];md=json.loads(raw)['version'];assert md['crate']==name and md['num']==version and md['checksum']==expected[name,version]==r['expected_locked_archive_sha256']and r['checksum_match']and md['created_at']==r['created_at']
  published=datetime.datetime.fromisoformat(md['created_at'].replace('Z','+00:00'));assert published.tzinfo is not None
  rows.append({'name':name,'version':version,'checksum':md['checksum'],'published_at':md['created_at'],'yanked_at_query':md['yanked'],'published_after_recorded_Pump_deploy':published>cutoff,'seconds_after_Pump_deploy':(published-cutoff).total_seconds()})
 late=[r for r in rows if r['published_after_recorded_Pump_deploy']]
 return {'scope':'176 observed CURRENT Pump registry versions only, not full252lock or other program graphs. Metadata timestamps not cryptographic registry/deployment history proof.','Pump_deploy_slot':captures['pump']['last_deploy_slot'],'Pump_deploy_utc':cutoff.isoformat(),'checked_registry_versions':176,'published_after_deployment':late,'all_versions':rows,'then_available_published_registry_graph_equal_current':not bool(late),'private_vendor_prerelease_alternatives_excluded':False,'historical_graph_identified':False,'compiled_output_effect_proved':False,'native_or_target_execution':0}
if __name__=='__main__':
 d=analyze();print(json.dumps({k:v for k,v in d.items()if k!='all_versions'},indent=2))
