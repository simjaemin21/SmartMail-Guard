# Timely AI — SmartMail Guard 2.0 설정

> GitHub의 파일을 업로드한다고 Timely AI 계정에 자동 배포되지 않습니다.

1. 기존 `SmartMail Guard`를 1.0 백업으로 유지합니다.
2. 별도의 `SmartMail Guard 2.0` 에이전트 템플릿을 사용합니다.
3. 모델 메뉴에서 **Solar Pro 4**가 선택돼 있는지 Timely UI로 확인합니다.
4. AI 지침에 기존 1.0 지침과 `AI_INSTRUCTIONS_V2_ADDONS.txt`의 2.0 추가 지침을 반영합니다. 실제 사용자 UI 지침이 최종본입니다.
5. 기존 `smartmail-guard-email-triage`는 OFF, 신규 `smartmail-guard-email-triage-v2`는 ON으로 설정합니다.
6. 저장 후 목록에서 2.0을 다시 불러와 지침·스킬·모델 선택 상태를 확인합니다.
7. 합성 이메일로 정상/광고/피싱/판단보류, 일정 추출, 안전 행동 카드를 점검합니다.
8. 시연 영상에서 가능한 경우 실제 스킬 실행 내역을 확인합니다. 대화에서 '스킬 사용'이라고 답한 것만으로 호출 기록이 입증되지는 않습니다.

실제 메일 서비스나 캘린더와 자동 연동되지는 않습니다.
