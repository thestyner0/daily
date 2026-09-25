# Daily

개인용 대시보드 (SMC 식단 · 주차 위치 · 볼거리 · 놀거리 · 핫플). 본문은 `app.enc`에 암호화되어 있습니다.

- 식단: 열 때마다 iamguno/smc-weekly-menu 에서 가져옴, 실패 시 `snapshot.json`
- 주차 기록: 각 기기의 브라우저에만 저장
- 볼거리·놀거리·핫플: 주기적으로 갱신 (`tools/build.py`)
