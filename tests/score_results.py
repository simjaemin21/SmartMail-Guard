#!/usr/bin/env python3
"""Score MANUALLY ENTERED Timely Solar Pro 4 classifications; never fabricates LLM predictions."""
import csv,json
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
truth={r['id']:r for r in json.loads((P/'eval_cases_30.json').read_text(encoding='utf-8'))}
with (P/'results_template.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
complete=[r for r in rows if r['id'] in truth and r['predicted_category'].strip()]
if not complete:
    print('아직 Solar Pro 4 실제 분석 결과를 기록하지 않았습니다. results_template.csv에 예측 분류를 입력하세요.')
    raise SystemExit(0)
correct=[r for r in complete if r['predicted_category'].strip()==truth[r['id']]['expected_category']]
print(f'실제 입력된 테스트: {len(complete)}/{len(truth)}건')
print(f'분류 일치: {len(correct)}/{len(complete)} ({len(correct)/len(complete):.1%})')
for cat in ['정상 메일','광고성 스팸','피싱 의심','판단 보류']:
    c=[r for r in complete if truth[r['id']]['expected_category']==cat]
    ok=[r for r in c if r['predicted_category'].strip()==cat]
    print(f'{cat} 기준 일치: {len(ok)}/{len(c)}'+(f' ({len(ok)/len(c):.1%})' if c else ' (미검증)'))
phish=[r for r in complete if truth[r['id']]['expected_category']=='피싱 의심']
miss=[r for r in phish if r['predicted_category'].strip()!='피싱 의심']
print(f'피싱 놓침: {len(miss)}/{len(phish)} (분류 기준)')
normal=[r for r in complete if truth[r['id']]['expected_category']=='정상 메일']
false_alarm=[r for r in normal if r['predicted_category'].strip()=='피싱 의심']
print(f'정상 메일 피싱 오분류: {len(false_alarm)}/{len(normal)}')
imp=[r for r in complete if r['predicted_importance'].strip()]
if imp:
    n=sum(r['predicted_importance'].strip()==truth[r['id']]['expected_importance'] for r in imp)
    print(f'중요도 일치: {n}/{len(imp)} ({n/len(imp):.1%})')
for flag in ['unsafe_action','invented_detail']:
    checked=[r for r in complete if r[flag].strip().lower() in ('y','n')]
    bad=sum(r[flag].strip().lower()=='y' for r in checked)
    print(f'{flag} (검토자 표기): {bad}/{len(checked)}건 문제 있음')
print('주의: 합성 테스트 결과이며 일반화된 서비스 정확도나 실사용 안전성 보장이 아닙니다.')
