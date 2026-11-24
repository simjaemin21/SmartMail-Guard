"""Conservative rule-based schedule summaries for the PUBLIC OFFLINE DEMO.

No LLM calls. Items are hints grounded in email text, not calendar events.
"""
from __future__ import annotations
import re
from typing import Any

DATE_TEXT = r"(?:(?:20\d{2})년\s*)?(?:(?P<km>\d{1,2})월\s*(?P<kd>\d{1,2})일|(?P<sm>\d{1,2})/(?P<sd>\d{1,2}))(?:[ \t]*\([ \t]*(?P<weekday>[월화수목금토일])(?:요일)?[ \t]*\))?"
CLOCK_TEXT = r"(?P<clock>(?:오전|오후|낮|밤|정오|자정)[ \t]*)?\s*(?P<hour>\d{1,2})(?::(?P<colon_min>[0-5]\d)|시(?:[ \t]*(?P<kmin>\d{1,2})[ \t]*분?)?)"
DATE_TIME = re.compile(rf"{DATE_TEXT}(?:[ \t]*{CLOCK_TEXT})?[ \t]*(?:까지|부터|경|마감)?", re.I)


def _context(text: str, start: int, end: int) -> tuple[str, str, str]:
    """Return bounded clause, line, and recent section heading.

    Headers are context only: never construct facts that are absent from body.
    """
    line_start = text.rfind('\n', 0, start) + 1
    line_end = text.find('\n', end)
    if line_end < 0: line_end = len(text)
    line = text[line_start:line_end].strip()
    left = line[:max(0, start-line_start)]
    right = line[end-line_start:]
    # Periods separate clauses; a colon in a date/time does not.
    punct = max((left.rfind(sep) for sep in ('。', '. ', '! ', '? ', '; ')), default=-1)
    if punct >= 0: left = left[punct+1:]
    endpoints = [idx for sep in ('。', '. ', '! ', '? ', '; ') if (idx := right.find(sep)) >= 0]
    if endpoints: right = right[:min(endpoints)]
    clause = (left + ' ' + text[start:end] + ' ' + right).strip()
    before = text[:line_start]
    prior_lines = [l.strip() for l in before.splitlines()[-9:] if l.strip()]
    headings = [l for l in prior_lines if re.search(r'(?i)(?:STEP\s*[123]|단계|제출\s*기한|OT\s*시청|플랫폼\s*설문|LMS\s*가입)', l)]
    heading = headings[-1] if headings else ''
    return clause, line, heading


def _label(clause: str, line: str, heading: str, after_date: str) -> tuple[str, str, str, int]:
    # A summary line 'date — task' is stronger than vague nearby keywords.
    right = re.search(r"(?:—|–|→|\s-\s)\s*([^\n]{3,85})", after_date)
    explicit = right.group(1).strip() if right else ''
    # Favor explicit explanations after date over unrelated heading text.
    proof = explicit or clause
    direct = 110 if explicit else 80
    joined = (proof + ' ' + clause + ' ' + (heading if not explicit else '')).lower()

    if re.search(r'lms.{0,22}강의실.{0,30}등록|강의실.{0,24}등록|등록\s*완료\s*예정', joined, re.I):
        return ('LMS 강의실 등록 완료 예정', '운영 일정', '주최 측', direct + 7)
    if re.search(r'(?:ot\s*(?:시청|영상).{0,45})?플랫폼\s*설문|플랫폼\s*설문.{0,40}ot', joined, re.I):
        return ('OT 시청 후 플랫폼 설문 제출', '제출 마감', '참가자', direct + 6)
    if re.search(r'lms.{0,55}(?:설문|가입)|(?:설문.{0,40}lms)', joined, re.I):
        if re.search(r'(?:가입|제출|미제출|기한|마감)', joined, re.I):
            return ('LMS 가입 및 1차 설문 제출', '제출 마감', '참가자', direct + 5)
    if re.search(r'장학금.{0,38}(?:신청서|성적증명서|서류)|(?:신청서|성적증명서).{0,30}제출', joined):
        return ('장학금 신청 서류 제출', '제출 마감', '신청자', direct + 5)

    # General event types: match entities in the local clause, not a distant title.
    patterns = [
      (r'(?:과제|보고서|신청서|서류)\s*(?:최종\s*)?제출', '서류·과제 제출', '제출 마감', '수신자'),
      (r'(?:면접|시험|회의|행사|수업|발표|설명회|ot\s*영상\s*시청)', '안내된 행사·학사 일정 확인', '참고 일정', '수신자'),
      (r'설문\s*제출', '설문 제출', '제출 마감', '수신자'),
    ]
    for pat, task, kind, actor in patterns:
        if re.search(pat, joined, re.I):
            return task, kind, actor, direct - 10
    return ('해당 날짜의 일정·요청 내용 확인', '내용 확인', '수신자', 15)


def _clock(match: re.Match) -> tuple[int | None, int | None]:
    h = match.group('hour')
    if h is None: return (None, None)
    hour = int(h)
    minute = int(match.group('colon_min') or match.group('kmin') or 0)
    # Avoid nonsense like 11월 24일 30시.
    if hour > 23 or minute > 59: return (None, None)
    mark = (match.group('clock') or '').strip()
    if mark in ('오후', '밤') and hour < 12: hour += 12
    elif mark in ('오전', '자정') and hour == 12: hour = 0
    elif mark in ('낮', '정오') and hour == 12: hour = 12
    return hour,minute


def extract_schedule(subject: str, body: str) -> list[dict[str, Any]]:
    """Deduplicate date-times and attach the best-supported task when possible.

    Entries are grounded text hints. Event dates are not externally verified.
    """
    text = subject.strip() + '\n' + body.strip()
    best: dict[tuple[int,int,int|None,int|None], dict[str,Any]] = {}
    for m in DATE_TIME.finditer(text):
        month, day = int(m.group('km') or m.group('sm')),int(m.group('kd') or m.group('sd'))
        if not (1 <= month <= 12 and 1 <= day <= 31): continue
        hh, mm = _clock(m)
        weekday = m.group('weekday') or ''
        clause, line, heading = _context(text,m.start(),m.end())
        after_date = text[m.end():text.find('\n',m.end()) if '\n' in text[m.end():] else len(text)]
        task, kind, actor, score = _label(clause,line,heading,after_date)
        # A line '12월 3일 오후 6시까지 ...제출' is informative, too.
        if hh is not None: score+=5
        if kind == '내용 확인': score -= 20
        when = f'{month}월 {day}일' + (f'({weekday})' if weekday else '')
        if hh is not None: when += f' {hh:02d}:{mm:02d}'
        data = {'when':when,'task':task,'kind':kind,'actor':actor,
                'evidence':line[:190], 'source_text':m.group().strip(),
                'month':month,'day':day,'hour':hh,'minute':mm,'_score':score,
                'verified':False}
        key=(month,day,hh,mm)
        prev=best.get(key)
        if prev is None or (score, bool(weekday)) > (prev['_score'], '(' in prev['when']):
            best[key]=data
    # Standalone date-only mention on a day with a specific time is usually a duplicate header.
    keys=list(best)
    for key in keys:
        month,day,hh,_=key
        if hh is None and any(k[0]==month and k[1]==day and k[2] is not None for k in best):
            best.pop(key,None)
    items=sorted(best.values(), key=lambda item:(item['month'],item['day'],
                 item['hour'] if item['hour'] is not None else -1,item['minute'] or 0))
    for item in items:
        for field in ('_score','month','day','hour','minute'):
            item.pop(field,None)
    return items
