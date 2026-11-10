# ⚔️ 비트 블레이드 (Beat Blade)

> **2D 게임 프로그래밍 프로젝트**  
> **개발 환경:** Python 3.x, pico2d  
> **장르:** 2D 횡스크롤 리듬 패링 액션 아케이드  

## 1. 게임 소개
**"이동은 없다, 오직 타이밍과 순발력뿐!"**  
복잡한 지형 이동을 배제하고, 화면 중앙에 고정된 캐릭터를 조작하여 양방향에서 BGM 비트에 맞춰 다가오는 적들을 순간적인 판단(베기 vs 패링)으로 처치하는 하이퍼 액션 아케이드 게임입니다.

## 2. 조작 방법 (4-Key System)
* **좌/우 방향키 (`←`, `→`):** 해당 방향의 일반 적(파란색) 즉시 베기 및 무력화된 적 반격
* **A / D 키:** 해당 방향의 강적(노란 방패병, 빨간 암살자) 공격 쳐내기 (패링)
* **ESC:** 게임 종료

## 3. 핵심 기능 및 기술 설계
* **상태 머신 (FSM):** 플레이어(`IDLE`, `SLASH`, `PARRY`, `HIT`) 및 적(`APPROACH`, `STUNNED`, `KNOCKBACK_DEAD`) 상태 분리
* **1차원 거리 판정:** `|Player_X - Enemy_X|` 거리 계산을 통한 정교한 `PERFECT` / `GOOD` / `MISS` 판정
* **타격감 연출 (Game Juice):** 패링 성공 시 역경직(Hit Stop), 카메라 흔들림(Screen Shake), 감속 넉백 물리 적용
* **피버 시스템 (Fever Mode):** 50콤보 달성 시 게임 템포 가속 및 점수 배율 증가

## 4. 디렉토리 및 모듈 구조 (예정)
```text
BeatBlade/
├── main.py              # 게임 진입점
├── game_framework.py    # 씬(State) 전환 및 Delta Time 관리
├── play_state.py        # 인게임 메인 루프 및 카메라/역경직 제어
├── player.py            # 플레이어 클래스 및 상태 머신
├── enemy.py             # 적 3종 클래스 및 물리 이동
├── spawn_manager.py     # BPM 동기화 적 스폰 스케줄러
├── ui_manager.py        # 체력바, 콤보, 판정 폰트 UI
└── resources/           # 스프라이트 시트 및 사운드 리소스