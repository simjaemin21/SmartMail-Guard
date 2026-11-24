#!/usr/bin/env python3
"""SmartMail Guard 2.0 LOCAL DEMO.
Offline mode is deterministic *rules*, NOT the Timely AI agent or Solar model.
Optional UPSTAGE_API_KEY uses a separate model API call, never a Timely invocation.
Python 3 stdlib only. All examples are synthetic.
"""
import json
import os
import re
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PORT = int(os.getenv('PORT', '8765'))
API_KEY = os.getenv('UPSTAGE_API_KEY', '').strip()
MODEL = 'solar-pro-4'
PROMPT = (ROOT / 'Timely_AI' / 'SYSTEM_PROMPT.txt').read_text(encoding='utf-8')
SAMPLES = json.loads((ROOT / 'tests' / 'sample_emails.json').read_text(encoding='utf-8'))
CATEGORIES = ('정상 메일', '광고성 스팸', '피싱 의심', '판단 보류')
LEVELS = ('낮음', '보통', '높음')


def time_phrases(body):
    """Illustrative extraction only, not a complete Korean time parser."""
    patterns = [
        r'\d{1,2}월\s*\d{1,2}일(?:\s*(?:오전|오후)\s*\d{1,2}시(?:\s*\d{1,2}분)?)?',
        r'(?:이번\s*주|다음\s*주)?\s*(?:월|화|수|목|금|토|일)요일(?:\s*(?:오전|오후)\s*\d{1,2}시(?:\s*\d{1,2}분)?)?',
        r'(?:이번\s*주|다음\s*주)\s*중',
        r'(?:오늘|내일|모레)(?:\s*안에|\s*까지|\s*만)?',
        r'\d+\s*(?:분|시간|일)\s*(?:안에|이내|내)',
        r'(?:오전|오후)\s*\d{1,2}시(?:\s*\d{1,2}분)?',
    ]
    found = []
    for pat in patterns:
        for m in re.finditer(pat, body):
            phrase = m.group().strip()
            if phrase and not any(phrase in x['raw_text'] for x in found):
                found.append({'type': '원문 시간 표현(규칙 추출)', 'raw_text': phrase,
                              'note': '일정 유형/날짜는 사용자가 원문에서 직접 확인하세요.'})
    return found[:6]


def rule_demo(subject, sender, body):
    """Demonstration rules, *never* a model accuracy claim."""
    s = (subject + ' ' + body).lower()
    dangerous = bool(re.search(r'(?:비밀번호|otp|인증.?번호|보안.?코드|카드.?번호|보증금|개인\s*계좌|주민등록증)', s))
    send_or_enter = bool(re.search(r'입력|보내|회신|송금|입금|결제|전달|제출|실행', s))
    coercion = bool(re.search(r'즉시|긴급|차단|잠금|정지|말소|30분|24시간|취소|지연', s))
    high_risk = (dangerous and send_or_enter and coercion) or bool(re.search(r'(?:개인\s*계좌|보증금).{0,25}(?:송금|입금)|(?:송금|입금).{0,25}(?:개인\s*계좌|보증금)', s))
    ads = bool(re.search(r'\[광고\]|광고|쿠폰|할인|특가|무료배송|세일|구매|프로모션', s))
    uncertain = bool(re.search(r'미확정|확인\s*중|아직\s*확인|출처\s*불명|소유자\s*정보.*없|정보가\s*없', s))
    if high_risk:
        category, risk, importance, priority = '피싱 의심', '높음', '낮음', '높음'
        action = '메일의 자격증명·인증번호·금전 요구를 따르지 말고 공식 기관에 직접 확인하세요.'
    elif ads:
        category, risk, importance, priority = '광고성 스팸', '낮음', '낮음', '낮음'
        action = '원하지 않는 광고는 무시하고, 관심이 있다면 공식 채널에서 조건을 직접 확인하세요.'
    elif uncertain:
        category, risk, importance, priority = '판단 보류', '보통', '보통', '보통'
        action = '핵심 정보나 발신 주체가 확인될 때까지 행동을 보류하고 공식 채널로 확인하세요.'
    else:
        category, risk, priority = '정상 메일', '낮음', '낮음'
        importance = '높음' if re.search(r'과제|시험|수강|장학금|면접|마감|제출',s) else '보통'
        action = '중요 일정은 공식 공지와 교차 확인하고 필요한 조치를 직접 진행하세요.'
    return {
        'category': category, 'risk_level': risk, 'importance': importance,
        'security_priority': priority,
        'reason': '규칙 기반 로컬 예시 결과입니다. 실제 Solar Pro 4 추론이 아닙니다.',
        'signals': ['메일 텍스트에서 추출한 단어만 기반으로 하는 단순 규칙이며 오분류할 수 있습니다.'],
        'timeline': time_phrases(body),
        'actions': [action],
        'uncertainty': '발신자 인증·URL 실제 목적지·첨부파일은 검사하지 않았습니다.',
        'mode': 'offline_rule_demo',
    }


def validate(obj):
    if not isinstance(obj, dict):
        raise ValueError('응답이 JSON 객체가 아닙니다.')
    def enum(k, vals, fallback):
        s = str(obj.get(k, fallback))
        return s if s in vals else fallback
    def txt(k, limit=1000): return str(obj.get(k, ''))[:limit]
    def arr(k):
        a = obj.get(k, [])
        return [str(v)[:220] for v in a[:6]] if isinstance(a, list) else []
    time_items = obj.get('timeline', [])
    timeline = []
    if isinstance(time_items, list):
        for item in time_items[:8]:
            if isinstance(item, dict):
                timeline.append({k: str(item.get(k, ''))[:160] for k in ('type', 'raw_text', 'note')})
    return {
        'category': enum('category', CATEGORIES, '판단 보류'),
        'risk_level': enum('risk_level', LEVELS, '보통'),
        'importance': enum('importance', LEVELS, '보통'),
        'security_priority': enum('security_priority', LEVELS, '보통'),
        'reason': txt('reason'),
        'signals': arr('signals'), 'timeline': timeline, 'actions': arr('actions'),
        'uncertainty': txt('uncertainty'), 'mode': 'solar_pro_4',
    }


def solar_classify(subject, sender, body):
    payload = {'model': MODEL, 'messages': [
        {'role': 'system', 'content': PROMPT},
        {'role': 'user', 'content': json.dumps({'subject': subject, 'sender': sender, 'body': body}, ensure_ascii=False)},
    ], 'temperature': 0.15, 'max_tokens': 1400, 'response_format': {'type': 'json_object'}}
    request = urllib.request.Request(
        'https://api.upstage.ai/v1/chat/completions',
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_KEY},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=28) as response:
            raw = json.loads(response.read(500000))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Upstage API HTTP {e.code}: 개인 API 키와 Solar Pro 4 사용 권한을 확인하세요.')
    content = raw['choices'][0]['message']['content']
    if isinstance(content, list):
        content = ''.join(x.get('text', '') for x in content if isinstance(x, dict))
    if content.strip().startswith('```'):
        content = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.I)
    return validate(json.loads(content))


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # No email content in access logs.

    def send_json(self, code, data):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == '/api/status':
            return self.send_json(200, {'mode': 'solar_pro_4' if API_KEY else 'offline_rule_demo', 'model': MODEL if API_KEY else None, 'sample_count': len(SAMPLES)})
        if self.path == '/api/samples':
            return self.send_json(200, SAMPLES)
        for route, filename, ctype in [('/', 'index.html', 'text/html'), ('/index.html', 'index.html', 'text/html'), ('/app.js', 'app.js', 'text/javascript')]:
            if self.path == route:
                data = (HERE / filename).read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', ctype + '; charset=utf-8')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
        return self.send_json(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path != '/api/analyze':
            return self.send_json(404, {'error': 'Not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 35000:
                return self.send_json(413, {'error': '최대 35KB까지 입력할 수 있습니다.'})
            obj = json.loads(self.rfile.read(length))
            if not isinstance(obj, dict):
                return self.send_json(400, {'error': 'JSON 객체가 필요합니다.'})
            sender = str(obj.get('sender', '')).strip()[:200]
            subject = str(obj.get('subject', '')).strip()[:250]
            body = str(obj.get('body', '')).strip()[:12000]
            if not body and not subject:
                return self.send_json(400, {'error': '제목 또는 본문이 필요합니다.'})
            result = solar_classify(subject, sender, body) if API_KEY else rule_demo(subject, sender, body)
            result['subject'] = subject
            return self.send_json(200, result)
        except Exception as e:
            return self.send_json(502 if API_KEY else 400, {'error': str(e)[:300]})


if __name__ == '__main__':
    print(f'SmartMail Guard 2.0 local demo: http://127.0.0.1:{PORT}  mode={"Solar Pro 4 (separate API)" if API_KEY else "RULE-ONLY DEMO"}')
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
