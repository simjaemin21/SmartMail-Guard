# SmartMail Guard ✉️

**Solar Pro 4 기반 이메일 스팸·피싱 의심 분석 AI 에이전트 MVP**

## 프로젝트 개요
일상 속 머신러닝 사례인 *이메일 스팸 자동 분류*에서 출발하여, 이메일의 위험 신호를 분석하고 사용자가 안전하게 대응할 수 있도록 돕는 결선 프로젝트입니다.

- **개발 플랫폼:** Timely AI
- **사용 LLM:** Solar Pro 4 (결선 지정 모델)
- **핵심 기능:** 이메일 제목·발신자·본문 입력 → 분류 → 위험도·판단 근거·대응 방법 안내
- **분류:** 정상 메일 / 광고성 스팸 / 피싱 의심 / 판단 보류

## 현재 구현 상태와 한계

- Timely AI에서 `SmartMail Guard`라는 에이전트 템플릿을 설정하고 저장함(사용자 환경).
- `smartmail-guard-email-triage` 스킬을 등록하고 활성화함(사용자 환경).
- Solar Pro 4가 선택된 에이전트 화면에서 가상 이메일 4건의 대화형 분석 결과를 확인함(사용자 테스트).
- 이 저장소의 `app/`은 **별도의 로컬 웹 시연용 프로토타입**입니다. API 키가 없으면 **규칙 기반 오프라인 데모**이며 Timely AI 에이전트 실행이나 Solar Pro 4 추론의 증거가 아닙니다.
- Gmail 실시간 연동, 자동 스팸 라벨링, 자동 삭제, 외부 공개 배포는 현재 구현 범위가 아닙니다.
- **실제 Timely AI 스킬 호출 여부와 배포 상태는 실행 기록/공유 설정으로 별도 확인해야 합니다.**

## 폴더 구성

```text
app/                           로컬 웹 시연용 코드
  server.py                    Python HTTP 서버 (오프라인 데모 또는 선택적 Upstage API)
  index.html, app.js           입력·분류 UI
tests/                         합성 샘플 8건과 오프라인 자체 테스트
Timely_AI/                     Timely 설정 참고 자료
  SYSTEM_PROMPT.txt            로컬 API 실험용 JSON 출력 프롬프트
  skills/smartmail-guard-email-triage/SKILL.md
  AGENT_SETUP.md                 Timely 에이전트 수동 설정 과정
  TEST_MESSAGES.txt
docs/TEST_GUIDE.md             테스트 가이드
START_WINDOWS.bat              Windows에서 로컬 시연 실행
START_WINDOWS_SOLAR.bat        외부 API 실험 실행 (개인 키 필요)
```

## 로컬 시연 실행 (선택)

Python 3 설치 후 프로젝트 폴더에서 아래 명령을 실행합니다.

```bash
python app/server.py
```

브라우저에서 `http://127.0.0.1:8765` 접속. 기본 상태는 **규칙 기반 데모**입니다.

### 오프라인 테스트

```bash
python tests/test_offline.py
```

8개 합성 사례에 대한 규칙 기반 출력 비교 테스트이며, 실제 AI 모델의 정확도를 의미하지 않습니다.

### 외부 Solar Pro 4 API 실험 (선택)

별도로 발급한 개인 API 키가 있는 경우에만 `UPSTAGE_API_KEY` 환경변수를 통해 사용할 수 있도록 구현했습니다. 이 코드는 Timely AI 네이티브 에이전트와 별도의 실험 경로이며, **실제 API 호출 성공은 검증되지 않았습니다.** API 실패 시 다른 모델로 자동 대체하지 않습니다.

## 보안 및 개인정보

실제 이메일에는 개인정보가 포함될 수 있습니다. 공개 저장소에 실제 메일 본문, API 키, 자격 증명을 업로드하지 마세요. 의심스러운 링크를 열거나 첨부를 실행하지 않고 입력된 문자열만 분석합니다. 분석 결과는 확정적인 악성 판정이 아닌 안전 판단 보조입니다.

## 결선 제출용 추가 작업

- Timely AI 에이전트의 실행·공유 가능 여부 확인
- 실제 모델/스킬 실행 로그와 시연 영상 확보
- 정식 PRD와 발표자료 최종본 작성
- GitHub 공개 URL 및 MVP 접근 방법 제출

---
본 프로젝트의 공개 코드는 **결선 MVP 개발 과정과 재현 가능한 로컬 시연용 소스**를 설명합니다. 테스트 결과나 소개 이미지를 실제 Solar Pro 4 API 호출 증빙으로 사용하지 않습니다.
