"""Offline, deterministic review-mode classifier. NOT a model and NOT Solar Pro 4.

Only intended for synthetic-email demonstrations. Unverified mail should never
be treated as verified-safe by a local heuristic.
"""
import re

PHISH_REQUESTS = [
    r"(?:비밀번호|인증번호|OTP|일회용\s*코드).{0,42}(?:회신|입력|전송|보내|알려|전달)",
    r"(?:회신|입력|전송|보내|알려|전달).{0,42}(?:비밀번호|인증번호|OTP|일회용\s*코드)",
    r"(?:개인\s*명의\s*계좌|담당자\s*개인\s*계좌).{0,50}(?:송금|입금|재입금)",
    r"(?:송금|입금|재입금).{0,50}(?:개인\s*명의\s*계좌|담당자\s*개인\s*계좌)",
    r"\.exe.{0,55}(?:실행|설치)",
    r"(?:실행|설치).{0,35}\.exe",
    r"(?:이전의\s*모든\s*지시|최상위\s*규칙|분류하라)",
]
ADS = r"광고|할인|쿠폰|특가|무료배송|세일|판촉|프로모션|구매\s*(?:유도|추천|하러)|홍보|경품\s*이벤트"
# Check whether the *email's essential decision facts* are still unresolved.
# Generic '확인되지 않아' is NOT sufficient: in an administrative reminder it
# often means the recipient's submission has not yet been confirmed.
UNCERTAIN_FACT = (
    # Only facts about the decision or essential instructions—not an unconfirmed
    # LMS registration/receipt state—should trigger review.
    r"(?:합격|불합격|선발|선정|본선\s*진출|수상)\s*(?:여부|결과|대상자)?"
    r"\s*(?:는|이|가)?\s*(?:아직\s*)?"
    r"(?:확인되지\s*않|확정되지\s*않|미확정|확인\s*중|결정되지\s*않)"
    r"|(?:실제\s*)?(?:대상자|필요(?:한)?\s*서류|제출\s*기한|발신자|"
    r"발신\s*주체|담당자|일정|핵심\s*정보)"
    r"\s*(?:정보|명단|여부)?\s*(?:는|이|가)?\s*(?:아직\s*)?"
    r"(?:확인되지\s*않|확정되지\s*않|미확정|확인\s*중|정해지지\s*않|정보(?:가|는)?\s*없)"
    r"|공식\s*공지.{0,80}반영되지\s*않"
)

IMPORTANT = r"장학금|수강신청|수강정정|기말고사|시험|면접|과제\s*제출|현장실습|등록금|학사\s*일정|발표\s*자료|대회|공모전|경진대회|선발\s*결과|합격\s*통보|본선\s*진출"
# Informational mail types. Lack of a known keyword alone is NOT proof of fraud.
# This merely avoids defaulting legitimate selection notices to '판단 보류'.
ROUTINE_NOTICE = r"\d{1,2}월|공지|제출|회의|면접|시험|수업|모임|운영|합격|불합격|선발|선정|결과\s*(?:안내|발표|통보|확인)|본선\s*진출|참가\s*(?:확정|안내)|심사\s*결과|당첨\s*안내"
# Preserve the weekday, time-of-day, minutes, and deadline marker if present.
DATE = r"(?:\d{4}년\s*)?(?:\d{1,2}월\s*\d{1,2}일|\d{1,2}/\d{1,2})(?:\s*\(\s*[월화수목금토일](?:요일)?\s*\))?"
CLOCK = r"(?:(?:오전|오후|낮|정오|자정)\s*)?\d{1,2}\s*시(?:\s*\d{1,2}\s*분)?"
TIME_PATTERNS = [
    rf"{DATE}\s*(?:{CLOCK})?\s*(?:까지|부터|경|마감)?",
    r"(?:이번\s*주|다음\s*주)\s*(?:(?:월|화|수|목|금|토|일)요일)?\s*(?:오전|오후|낮)?\s*\d{1,2}시(?:까지)?",
    r"(?:이번\s*주|다음\s*주)\s*(?:월|화|수|목|금|토|일)요일(?:까지)?",
    r"(?:이번\s*주\s*중|이번\s*주까지|오늘만|오늘\s*안에|\d+분\s*안에|\d+시간\s*안에|주말\s*동안만|이달)",
]


def analyze(sender: str, subject: str, body: str) -> dict:
    """Deliberately limited rules; never assert sender or link verification."""
    sender, subject, body = sender.strip(), subject.strip(), body.strip()
    content = subject + '\n' + body
    indicators=[]
    if any(re.search(p, content, re.I) for p in PHISH_REQUESTS):
        category='피싱 의심'; risk='높음'; importance='낮음'; priority='높음'
        indicators=['인증정보 요구, 개인 계좌 송금, 실행파일 유도 또는 검사 결과 조작 지시가 탐지됨']
        actions=['이 메일의 요청에 따라 비밀번호·인증번호를 전달하거나 송금·파일 실행을 하지 마세요.', '메일의 링크나 회신 주소가 아닌 기존에 알고 있는 공식 채널에서 사실관계를 확인하세요.']
    elif re.search(ADS,content,re.I):
        category='광고성 스팸'; risk='낮음'; importance='낮음';priority='낮음'
        indicators=['할인·쿠폰·구매 등 판촉 중심 표현이 발견됨']
        actions=['관심 없으면 무시하거나 메일 서비스의 수신 차단 기능을 검토하세요.', '관심 있다면 기존에 알고 있는 공식 쇼핑몰에서 조건을 확인하세요.']
    elif re.search(UNCERTAIN_FACT,content,re.I) or not re.search(ROUTINE_NOTICE,content,re.I):
        category='판단 보류'; risk='보통'; importance='높음' if re.search(IMPORTANT, content) else '보통';priority='보통'
        indicators=['발신 주체 또는 핵심 일정·대상·요청 정보가 불분명할 수 있음']
        actions=['이 메일만으로 요청의 진위를 확정하지 마세요.', '평소 이용하는 공식 포털·담당자 연락처로 내용을 확인하세요.']
    else:
        category='정상 메일'; risk='낮음'; importance='높음' if re.search(IMPORTANT, content) else '보통';priority='낮음'
        indicators=['본문에 일반적인 일정·정보 안내가 확인되며 강한 피싱 위험 신호는 발견되지 않음']
        actions=['메일에 있는 일정과 요청 내용을 확인하세요.', '실제 기관에서 보낸 메일인지는 공식 포털 또는 기존 연락처로 별도 확인하세요.']
    spans=[]
    for pat in TIME_PATTERNS:
        for m in re.finditer(pat,content):
            raw=m.group().strip(); start=m.start(); end=m.end()
            if not raw: continue
            if any(start>=s and end<=e for s,e,_ in spans):continue
            spans.append((start,end,raw))
    spans.sort()
    times=[]
    for _,_,raw in spans:
        if any(raw in x for x in times): continue
        if any(raw in other and len(raw)<len(other) for other in [v for _,_,v in spans]):continue
        times.append(raw)
    note='분석 범위는 텍스트에 한정됩니다. 발신자 인증·링크 도착지·첨부파일 검사는 수행하지 않았습니다.'
    return {
        'category':category,'risk_level':risk,'importance':importance,'security_priority':priority,
        'signals':indicators,'timeline':times,'actions':actions,
        'uncertainty':note, 'engine':'offline_rule_only',
    }
