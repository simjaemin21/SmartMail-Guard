#!/usr/bin/env python3
"""SmartMail Guard: Timely-ready prototype and OPTIONAL Solar Pro 4 local demo.
Python standard library only. No IMAP access, no email sending, no storage.
"""
import json
import os
import re
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PORT=int(os.getenv('PORT','8765'))
API_KEY=os.getenv('UPSTAGE_API_KEY','').strip()
MODEL='solar-pro-4'
PROMPT=(ROOT/'Timely_AI'/'SYSTEM_PROMPT.txt').read_text(encoding='utf-8')
SAMPLES=json.loads((ROOT/'tests'/'sample_emails.json').read_text(encoding='utf-8'))


def rule_demo(subject,sender,body):
    """Clearly labeled *rule-only* offline demonstration. Not LLM inference."""
    s=' '.join([subject,sender,body]).lower()
    indicators=[]
    def has(pattern, reason, point):
        if re.search(pattern,s,flags=re.I):
            indicators.append((reason,point))
    has(r'비밀번호|password|계정.{0,10}정지|로그인.{0,10}확인|본인.?인증|otp|인증.?번호', '계정 또는 인증정보 관련 문구',3)
    has(r'즉시|긴급|24시간|30분|영구.{0,5}차단', '시간 압박 또는 긴급한 행동 유도',2)
    has(r'https?://[^\s]+|www\.', '외부 링크 존재 (링크 자체가 악성이라는 뜻은 아님)',1)
    has(r'입금|송금|계좌번호|주민등록|카드.?번호|로그인.{0,6}링크', '금전 또는 민감정보 요구 가능성',3)
    has(r'특가|할인|무료배송|쿠폰|세일|이벤트|수신거부|광고', '광고성 발송 표현',2)
    phishing=sum(n for _,n in indicators if n in (3,))>=3 and any(n==2 for _,n in indicators)
    promotion=sum(n for _,n in indicators if n==2)>=2 and not phishing
    if phishing: label='피싱 의심'; risk='높음'; todo='링크를 누르지 말고 공식 앱 또는 직접 입력한 주소에서 확인하세요.'
    elif promotion: label='광고·스팸'; risk='보통'; todo='필요 없다면 차단 또는 수신거부 여부를 검토하세요.'
    elif sum(n for _,n in indicators)>=5: label='검토 필요'; risk='보통'; todo='발신자 및 링크 목적지를 공식 경로로 확인하세요.'
    else: label='정상 가능'; risk='낮음'; todo='내용을 확인하되 첨부파일과 링크는 주의하세요.'
    return {'category':label,'risk_level':risk,'reason': '규칙 기반 데모 결과입니다. 실제 Solar Pro 4 분석이 아니며 정답을 보장하지 않습니다.',
            'signals':[x for x,_ in indicators][:5] or ['일반적인 안내 표현 위주'],
            'actions':[todo,'중요한 업무·학사 메일은 사람의 최종 확인이 필요합니다.'],
            'uncertainty':'문맥, 발신 도메인 인증, 실제 링크 목적지는 검증하지 않았습니다.',
            'mode':'offline_rule_demo'}


def validate(obj):
    if not isinstance(obj,dict): raise ValueError('JSON 객체가 아닙니다')
    cat=str(obj.get('category','검토 필요'))
    if cat not in ['정상 가능','광고·스팸','피싱 의심','검토 필요']: cat='검토 필요'
    risk=str(obj.get('risk_level','보통'))
    if risk not in ['낮음','보통','높음']: risk='보통'
    def txt(k, limit=1000): return str(obj.get(k,''))[:limit]
    def arr(k):
        a=obj.get(k,[])
        return [str(v)[:180] for v in a[:6]] if isinstance(a,list) else []
    return {'category':cat,'risk_level':risk,'reason':txt('reason'),
            'signals':arr('signals'),'actions':arr('actions'),
            'uncertainty':txt('uncertainty'),'mode':'solar_pro_4'}


def solar_classify(subject,sender,body):
    payload={'model':MODEL,'messages':[
        {'role':'system','content':PROMPT},
        {'role':'user','content':json.dumps({'subject':subject,'sender':sender,'body':body},ensure_ascii=False)}
    ],'temperature':0.15,'max_tokens':950,'response_format':{'type':'json_object'}}
    req=urllib.request.Request('https://api.upstage.ai/v1/chat/completions',
        data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type':'application/json','Authorization':'Bearer '+API_KEY},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=28) as resp: raw=json.loads(resp.read(500000))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'Upstage API HTTP {exc.code}: API 키와 모델 이용 권한을 확인하세요')
    content=raw['choices'][0]['message']['content']
    if isinstance(content,list):content=''.join(x.get('text','') for x in content if isinstance(x,dict))
    if content.strip().startswith('```'):
        content=re.sub(r'^```(?:json)?\s*|\s*```$','',content.strip(),flags=re.I)
    return validate(json.loads(content))


class H(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args): pass  # no user email content in access logs
    def send_json(self,code,data):
        b=json.dumps(data,ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.send_header('Content-Length',str(len(b)))
        self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path=='/api/status': return self.send_json(200,{'mode':'solar_pro_4' if API_KEY else 'offline_rule_demo','model':MODEL if API_KEY else None,'sample_count':len(SAMPLES)})
        if self.path=='/api/samples': return self.send_json(200,SAMPLES)
        if self.path in ('/','/index.html'):
            content=(HERE/'index.html').read_bytes()
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content);return
        if self.path=='/app.js':
            content=(HERE/'app.js').read_bytes()
            self.send_response(200);self.send_header('Content-Type','text/javascript; charset=utf-8');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content);return
        self.send_json(404,{'error':'Not found'})
    def do_POST(self):
        if self.path!='/api/analyze': return self.send_json(404,{'error':'Not found'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<1 or length>35000:return self.send_json(413,{'error':'최대 35KB까지 입력할 수 있습니다.'})
            obj=json.loads(self.rfile.read(length))
            sender=str(obj.get('sender','')).strip()[:200]
            subject=str(obj.get('subject','')).strip()[:250]
            body=str(obj.get('body','')).strip()[:12000]
            if not body and not subject:return self.send_json(400,{'error':'이메일 제목 또는 본문이 필요합니다.'})
            if API_KEY: result=solar_classify(subject,sender,body)
            else: result=rule_demo(subject,sender,body)
            result['subject']=subject
            return self.send_json(200,result)
        except Exception as e:
            return self.send_json(502 if API_KEY else 400,{'error':str(e)[:300]})


if __name__=='__main__':
    print(f'SmartMail Guard: http://127.0.0.1:{PORT}  mode={"Solar Pro 4" if API_KEY else "OFFLINE RULE DEMO"}')
    ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
