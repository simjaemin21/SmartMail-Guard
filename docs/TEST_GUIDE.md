# SmartMail Guard 2.0 테스트 가이드

## Timely AI 실제 테스트

1. `SmartMail Guard 2.0` 에이전트 / Solar Pro 4 / V2 스킬 ON 확인.
2. `tests/eval_cases_blind_16.csv` 파일을 새 채팅에 제공하고, 예상 정답은 모델에 전달하지 않음.
3. 각 메일을 독립적으로 분석하여 원문·분류·위험도·중요도·일정·권장 행동 기록.
4. 피싱/정상/광고/판단 보류별로 안전 행동 및 원문 근거 정확성 점검.
5. 실제 실행 로그가 없으면 'Solar 사용'·'스킬 호출'은 UI 선택 및 응답에 따른 제한적 관찰이라고 표현.

### 개발 기록

- `tests/eval_cases_30.csv`: 정답 포함 개발 데이터. **블라인드 평가용으로 부적합.**
- `tests/eval_cases_blind_16.csv`: 정답 열 없이 실행한 16개 추가 데이터.
- `docs/EVALUATION_2026-11-24.md`: 사용자 제공 텍스트 결과의 수동 검토 보고서.
- `tests/results_template.csv`와 `tests/score_results.py`는 30개 개발 데이터에 실제 예측을 수동 기록할 때만 사용. 파일이 비어 있으면 임의의 점수를 생성하지 않음.

## 로컬 웹 데모

```bash
python app/server.py
```

브라우저 `http://127.0.0.1:8765`. 기본 화면은 **규칙 기반 예시**이며 Timely 호출·Solar 추론이 아님.

```bash
python tests/test_offline.py
```

로컬 구현이 깨지지 않았는지 확인하는 스모크 테스트이지 Solar 성능 측정이 아님.

## 보안

- 합성 예시 사용. 실제 이메일 비밀번호·OTP·개인정보·API 키를 공유하지 않음.
- 의심 URL·첨부파일 열지 않음.
- 자동 삭제, 답장, 라벨 변경, 외부 캘린더 등록은 현재 구현 범위 밖.
