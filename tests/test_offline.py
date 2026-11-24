"""Offline smoke tests. Run from pack root: python tests/test_offline.py"""
import sys, json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'app'))
import server
for x in server.SAMPLES:
    res=server.rule_demo(x['subject'],x['sender'],x['body'])
    assert res['category'] in ('정상 가능','광고·스팸','피싱 의심','검토 필요')
    assert res['mode']=='offline_rule_demo'
    assert res['category']==x['expected'], (x['id'],res['category'],x['expected'])
    print(x['id'],x['kind'], '=>',res['category'], '(기대:',x['expected']+')')
print('OK: 8 synthetic examples tested; results are demo-only and not Solar predictions')
