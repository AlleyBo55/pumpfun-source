"""Passive source derivation and frozen-byte checks; no target interpretation or import."""
from pathlib import Path
import argparse,ast,hashlib,json
P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
def verify():
 d=J(P/'derivation.json');pc=P/'predecessor-controls';m=J(pc/'manifest.json');assert H(pc/'manifest.json')==d['prior_manifest_sha256']
 for n,h in d['retained_predecessor_controls'].items():assert H(pc/n)==h==m[n],n
 for n,h in J(P/'inputs.json').items():assert H(P/'repo'/n)==h==m['repo/'+n]
 for row in d['changed_same_path_payloads']:
  assert H(P/row['path'])==row['new_sha256'] and H(pc/row['path'])==row['old_sha256']==m[row['path']]
 for f in P.glob('*.py'):ast.parse(f.read_text())
 if J(P/'plan.json')['lane']=='ordinary':
  old=(pc/'controller.py').read_text();new=old.replace("E=P.parent/'cto-wallet-collector-build-01'","E=P.parents[1]/'cto-shared6093-v2-build-01'").replace("OUT=P.parent/'cto-wallet-collector-preservation-01'","OUT=P.parents[1]/'cto-shared6093-v2-ordinary-preservation-01'").replace('6e0c9002d09e0cee6cc738b3a9e0983a8d0cd89374fa2cc7c41fa45910515b9e','fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5')
  assert new==(P/'controller.py').read_text(),'ordinary controller must be exact three substitutions'
 else:
  assert H(P/'cases.json')==m['cases.json'];assert H(P/'prior/receipt.json')==m['prior/receipt.json']
 print('PASS passive predecessor derivation;15 original inputs;exact ordinary substitutions or six exact case objects;no target import')
if __name__=='__main__':verify()
