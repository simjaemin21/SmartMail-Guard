"""Rule-only smoke test: NOT Timely or Solar model inference."""
import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / 'app'))
import server

for x in server.SAMPLES:
    res = server.rule_demo(x['subject'], x['sender'], x['body'])
    assert res['mode'] == 'offline_rule_demo'
    assert res['category'] in server.CATEGORIES
    assert res['risk_level'] in server.LEVELS
    assert res['importance'] in server.LEVELS
    assert isinstance(res['timeline'], list)
    assert res['category'] == x['expected'], (x['id'], res['category'], x['expected'])
    print(x['id'], x['kind'], '=>', res['category'], '(기대:', x['expected'] + ')')
print('OK: 8 local RULE-ONLY smoke cases; NOT Solar Pro 4 predictions.')
