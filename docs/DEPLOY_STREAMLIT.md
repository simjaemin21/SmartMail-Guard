# SmartMail Guard 2.0 — 공개 배포 절차 (Streamlit Community Cloud)

> 2026-11-24 강의 검토 반영. 실제 URL의 비로그인 접근 및 Solar API 성공 여부는 직접 확인해야 합니다.
> **현재 앱은 2개의 탭으로 분리**되어 있습니다: `① 무료 규칙 기반 체험(LLM 아님, API 키·체험 코드 불필요)` / `② Solar Pro 4 실시간(API 키·체험 코드 필요, 잔액이 있어야 동작)`. 동영상의 Vercel 배포는 대체 경로이며 의무가 아닙니다.

## 이 배포물이 무엇인가요?

- **공개 URL**: Streamlit Community Cloud에 GitHub 저장소를 연결하여 생성하는 `https://...streamlit.app` 형태의 URL
- **실제 엔진**: Upstage API의 Solar Pro 4, 별도 API 키가 필요합니다.
- **다름**: 사용자가 Timely AI에서 만든 에이전트 자체를 인터넷에 공개하는 기능이 아닙니다. 동일한 모델을 외부 API로 호출하는 독립 데모입니다.
- **의도적 제한**: 이메일 자동 수집·라벨 변경·삭제·자동 답장·첨부 검사·발신자 인증은 없습니다.

## 0. 준비물

1. GitHub 공개 저장소 `simjaemin21/SmartMail-Guard` (이미 존재)
2. `UPSTAGE_API_KEY`: Upstage Console에서 유효하게 발급한 키. Solar Pro 4 사용 권한 및 충전 잔액이 필요할 수 있습니다.
3. `DEMO_ACCESS_CODE`: 12자 이상의 임의 문자열. PowerShell에서는 `python -c "import secrets; print(secrets.token_urlsafe(18))"`로 생성할 수 있습니다.
4. Streamlit Community Cloud 계정. GitHub와 연결해야 합니다.

> 어떤 API 키·체험 코드도 GitHub 저장소, README, 스크린샷, 일반 채팅에 붙여 넣지 마세요.

## 1. 코드 업로드

VS Code에서 `SmartMail-Guard` 저장소 폴더를 연 뒤 공개 배포 업데이트 ZIP을 루트에 압축 해제합니다. 안내에 따라 테스트 성공 여부를 확인한 다음 `git add -A`, `git commit`, `git push`로 업로드합니다.

배포 진입점은 `streamlit_app.py`, 의존성 파일은 `requirements.txt`입니다.

## 2. Streamlit 배포

1. `https://share.streamlit.io/`에서 GitHub 계정으로 로그인합니다.
2. **Create app / Deploy an app → From existing repo**를 선택합니다.
3. Repository: `simjaemin21/SmartMail-Guard`
4. Branch: `main`
5. Main file path: `streamlit_app.py`
6. App URL: 사용 가능한 적절한 서브도메인으로 지정 (실제 URL은 생성 후 확인)
7. **Advanced settings → Secrets**에 다음 TOML 형식으로 입력합니다. 값은 본인이 가진 값으로 교체하세요.

```toml
UPSTAGE_API_KEY = "여기에_본인의_실제_키"
DEMO_ACCESS_CODE = "여기에_12자_이상_무작위_체험_코드"
```

8. Deploy를 클릭합니다. API 키는 소스 코드가 아니라 Streamlit 배포 설정에 저장됩니다.

## 3. 시크릿 창 검증 — 제출 전 필수

1. 배포된 URL을 시크릿 창에서 엽니다. 로그인 화면이 뜨지 않고 앱과 **체험 코드 입력창**이 나와야 합니다.
2. **무료 체험 탭**에서 체험 코드 없이 정상 가상 메일·피싱 메일을 분석합니다. 결과에 규칙 기반(LLM 아님)이 명시되는지 봅니다.
3. **실시간 AI 탭**에 별도 체험 코드를 입력하고 정상 메일 가상 예제로 분석합니다. 사용 가능한 Upstage API 잔액이 있어야 성공합니다.
4. **Upstage API 응답 확인: solar-pro-4...** 문구를 실제 분석 후 확인합니다. API 키를 설정했다는 상태 표시는 실호출 성공 증거가 아닙니다.
4. 피싱 예제로 다시 분석해서 비밀번호·OTP 제공을 권장하지 않는지 확인합니다.
5. 판단 보류 예제로 정보 부족을 처리하는지 확인합니다.
6. 신뢰할 수 있는 다른 장치/네트워크에서 다시 접속해 봅니다.
7. 제출에 정확한 **공개 URL**과 (실시간 AI 탭을 심사위원에게 열어둘 경우) **체험 코드**를 함께 제공합니다. 해당 URL이 심사 종료까지 사용 가능한지 확인합니다.
8. 배포 실패, 401/403/429, 요금·권한 문제 발생 시 실제 AI가 동작한다고 제출하지 않습니다.

## 4. 보안·비용·운영 주의

- Streamlit은 무료 공개 앱 배포를 제공하지만 실행 자원·휴면 정책은 변경될 수 있습니다. 외부 Solar API 요금은 별도입니다.
- 체험 코드는 UI 접근을 제한하나 정식 계정 인증·요청 제한 시스템을 대체하지 않습니다. 재시작하면 글로벌 45회 카운터가 초기화됩니다. **절대적인 과금 상한이 아닙니다.**
- 세션당 4회 제한이 있고, 전체 인메모리 한도 45회가 있으므로 심사위원이 접속할 때 한도가 남아 있어야 합니다.
- API 키는 `.streamlit/secrets.toml`이나 `.env` 등에 커밋하지 않습니다. `.gitignore`에 제외 규칙이 있습니다.
- 개인정보가 포함된 실제 메일을 입력하지 마세요. 생성·분석을 위해 Upstage API로 전송됩니다.
- 비공식 도메인의 악성 여부, 첨부파일, SPF/DKIM/DMARC 등은 실제 검사하지 않습니다.
- 데모의 오류 메시지나 멈춤은 투명하게 표시되며 규칙 기반 가짜 응답으로 대체하지 않습니다.

## 5. 다시 실행/테스트

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
python tests/test_solar_deploy.py
```

로컬 Streamlit 앱도 API 키와 체험 코드가 없으면 분석되지 않습니다. 유효한 값은 `st.secrets` 또는 해당 PowerShell 세션의 환경변수에만 넣으세요.

## 출처

- https://docs.streamlit.io/deploy/streamlit-community-cloud
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
