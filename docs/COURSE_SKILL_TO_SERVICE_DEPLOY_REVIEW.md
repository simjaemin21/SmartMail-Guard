# Skill to Service 강의 검토 — SmartMail Guard 2.0 적용

검토한 자료: Google Drive `Screen_Recording_20261124_213831_Chrome.mp4` (2026-11-24 업로드, 21분 21초 화면 녹화).
영상 예제는 의료 알레르기 확인 스킬을 Timely AI의 `skill-to-service` 메타스킬로 웹서비스로 변환하고 Vercel에 배포하여 공개 `vercel.app` URL에서 작동 여부를 검사합니다.
영상 녹화 구간 기준 시각은 대략 아래와 같습니다. 실제 강의 플레이어 시각은 배속·녹화로 인해 다릅니다.

- 01:35: Timely 스킬 스토어에서 예선 제출 스킬 설치.
- 02:00–02:20: `skill-to-service` 메타스킬 검색 및 활성화.
- 03:10–04:10: Vercel 계정과 액세스 토큰 준비, Timely의 Vercel 커넥터 연결.
- 04:35–05:20: Timely 채팅에서 `skill-to-service`를 호출해 스킬을 웹서비스로 전환 요청.
- 05:40–15:00: 서비스 기획(P0/P1), PRD, 코드 생성 과정.
- 11:35–12:15: PRD의 11항목(한 줄 정의/타깃 사용자/문제/트리거/핵심 기능/스킬 매핑/입출력/필요 설정/데이터 규칙/성공 기준/제외 범위) 설명.
- 14:40: 우선순위별 범위 설정: P0 핵심 최대 4개, P1 보완 기능.
- 16:00–19:30: Vercel에서 배포 환경 설정, 공개 웹페이지 시연, 예제 공개 URL 확인.
- 20:40: GitHub 저장소와 Vercel 프로젝트를 연동하는 대안 설명.

## SmartMail Guard에 적용할 판단

1. **배포 URL:** Vercel `*.vercel.app`은 강의가 직접 시연하는 외부 공개 서비스 URL의 한 가지 예시입니다. **기존 Streamlit `*.streamlit.app`도 외부에서 접근할 수 있는 공개 URL**입니다. 심사 지침에 Vercel 전용이라는 요구는 보이지 않습니다. 따라서 기존 Streamlit 앱을 *무조건* 옮길 이유는 없습니다.
2. **실제 AI 모델:** Vercel/Streamlit은 웹 호스팅입니다. Timely의 Solar Pro 4 크레딧을 외부 웹사이트에 자동으로 연결하지 않습니다. 강의 예제는 약품 공개 데이터 API를 활용한 서비스로, SmartMail Guard의 실시간 Solar 호출과는 다른 과금/인증 구조입니다.
3. **비용 0원 대응:** 웹의 '① 무료 체험'은 규칙 기반임을 명확히 표시하고 누구나 접속할 수 있게 합니다. '② Solar Pro 4 실시간'은 별도 체험 코드와 실제 API 키·잔액이 있어야 하고 크레딧 부족 시 안내만 표시합니다. **부족 시 자동 규칙 전환은 하지 않습니다.**
4. **규정:** Gemini 등 다른 LLM은 사용하지 않습니다. 규칙 기반 처리 자체는 생성형 LLM이 아닙니다. Timely AI에서 만든 Solar Pro 4 에이전트는 프로젝트의 핵심 MVP이며, 공개 데모와 그 기능을 혼동하지 않습니다.
5. **제출 전 검증:** 실제 URL을 시크릿 창에서 열기, 무료 체험 실행, AI 탭의 크레딧 제한 확인, 3분 영상에서 Timely Solar Pro 4 실제 작동 보이기, 8분 발표 PDF·PRD·GitHub 공개 여부 확인하기. 체험 코드로 막힌 AI 탭을 발표/제출 안내 없이 제공하지 않습니다.

## 강의 방식대로 Vercel로 별도 배포하는 경우(선택)

1. Timely AI의 스킬 스토어에서 제출 스킬과 `skill-to-service` 메타스킬을 활성화합니다.
2. Timely의 Vercel 커넥터는 본인의 Vercel 액세스 토큰으로 연결합니다. 토큰은 채팅과 GitHub에 입력하지 않습니다.
3. `docs/SKILL_TO_SERVICE_TIMELY_PROMPT.txt`의 요청문을 Timely 채팅에서 사용합니다.
4. 배포 결과로 받은 **실제** `https://...vercel.app` URL만 제출합니다. 화면만 있다고 URL이 자동 생성되는 것은 아닙니다.
5. 기 구축된 Streamlit 서비스가 정상 공개·작동한다면 중복 Vercel 이전은 필요 없습니다.

참고: https://vercel.com/docs/git, https://vercel.com/docs/plans
