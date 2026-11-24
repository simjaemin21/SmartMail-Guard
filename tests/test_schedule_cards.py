import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.offline_demo import analyze
from app.schedule_extractor import extract_schedule

class ScheduleCardTests(unittest.TestCase):
    sample_title='[공모전] LMS 가입·설문 미제출 안내 (11/24(화) 낮 12시까지 연장)'
    sample_body='''본선 진출을 축하드립니다. LMS 가입 및 설문이 아직 확인되지 않아 다시 연락드립니다.
제출 기한을 오늘 11월 24일(화) 낮 12시까지로 연장하오니 기한 내 제출 부탁드립니다.
STEP 1. LMS 가입 및 설문 제출 (필수)
제출 기한: 11월 24일(화) 낮 12시까지(연장)
기한 내 제출자에 한해 11월 24일(화) 오후 1시까지 LMS 강의실에 등록해 드립니다.
STEP 2. LMS 등록 완료 후 OT 영상 시청 (필수)
STEP 3. OT 시청 후 플랫폼 설문 제출 (필수)
플랫폼 설문 제출 기한: 11월 24일(화) 오후 11시 59분까지
[일정 요약]
- 11/24(화) 낮 12:00 — LMS 가입 + 설문 제출 마감(연장)
- 11/24(화) 오후 1:00 — LMS 강의실 등록 완료
- 11/24(화) 오후 11:59 — OT 시청 후 플랫폼 설문 제출 마감'''
    def test_three_distinct_actions_no_duplicate_time(self):
        result=analyze('contest-office@example.test',self.sample_title,self.sample_body)
        cards=result['schedule_items']
        self.assertEqual(len(cards),3, cards)
        self.assertEqual([x['when'] for x in cards],['11월 24일(화) 12:00','11월 24일(화) 13:00','11월 24일(화) 23:59'])
        self.assertIn('LMS 가입', cards[0]['task'])
        self.assertIn('플랫폼 설문', cards[2]['task'])
        self.assertIn('강의실', cards[1]['task'])
        self.assertEqual(cards[1]['kind'],'운영 일정')
        self.assertEqual(cards[1]['actor'],'주최 측')
        self.assertEqual(cards[0]['kind'],'제출 마감')
        self.assertEqual(cards[2]['kind'],'제출 마감')
        self.assertFalse(any(x['verified'] for x in cards))
    def test_free_preview_never_calls_ai(self):
        s=(Path(__file__).resolve().parents[1]/'streamlit_app.py').read_text('utf-8')
        free=s.split('def show_free_demo():',1)[1].split('def show_live_demo():',1)[0]
        self.assertIn('schedule_items',free)
        self.assertNotIn('request_solar(',free)
    def test_no_bogus_date_from_no_date(self):
        self.assertEqual(extract_schedule('일정 안내','내일까지 서류를 제출하세요.'),[])
    def test_simple_scholarship(self):
        a=analyze('x','장학금 안내','장학금 신청서는 12월 3일 오후 6시까지 제출해 주세요.')
        cards=a['schedule_items']
        self.assertEqual(len(cards),1)
        self.assertEqual(cards[0]['when'],'12월 3일 18:00')
        self.assertIn('장학금',cards[0]['task'])
if __name__=='__main__': unittest.main()
