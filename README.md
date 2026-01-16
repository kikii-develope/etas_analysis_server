## 위험운전자 크롤링 서버

### 1. 주요 기능

- 운전자 정보 수집
- 위험 운전자 통계 데이터 업로드
- PDF 리포트 다운로드
- 엑셀 데이터 파싱 후 DB 저장
- FastAPI 기반 API 제공

---

### 2. 기술 스택

- **Language**: Python 3  
- **Web Framework**: FastAPI  
- **Crawling**: Selenium (ChromeDriver 기반 웹 자동화)  
- **Data Processing**: Pandas (엑셀 데이터 파싱 및 가공)  
- **Database**: MySQL (운전자 및 통계 데이터 저장)  
    - 관련 테이블
        - etas_driver: eTAS에 게시되어 있는 승무원 정보와, 스운솔 내의 승무원 정보 맵핑을 위한 테이블
        - dangerous_driving_stat: 월 별 위험운전자 데이터를 내부 DB에서 관리하기 위해 업로드하는 테이블
- **API Server**: Uvicorn  
- **Container**: Docker  
- **File Handling**: Excel(.xls), PDF


## 3. 전체 디렉토리 구조

```text
crawling_driver_data/
├── index.py                 # FastAPI 서버 엔트리포인트
├── Dockerfile               # Docker 실행 환경 설정
├── requirements.txt         # Python 의존성 목록
├── type.py                  # 공용 타입 정의
│
├── config/
│   ├── environment.py       # 환경 변수 로딩
│   └── settings.py          # 서비스 설정 값
│
├── crawler/
│   ├── index.py             # 크롤러 실행 진입점
│   ├── crawler_etas.py      # ETAS 사이트 크롤링 핵심 로직
│   ├── session_utils.py     # 세션(JSESSIONID) 관리 유틸
│   ├── etas_company_info.py # ETAS 회사/계정 정보 관련
│   └── databases/
│       └── etas_db.py       # 크롤링 결과 DB 저장 로직
│
├── excel_parser/
│   ├── excel_driver_info.py           # 운전자 정보 엑셀 파싱
│   └── excel_dangerous_driver_stat.py # 위험 운전자 통계 엑셀 파싱
│
├── models/
│   └── etas_login_request.py # ETAS 로그인 요청 모델
│
├── sql/
│   ├── index.py              # MySQL 커넥션 관리
│   └── queries.py            # SQL 쿼리 정의
│
└── data/
    └── *.xls                 # 테스트 및 샘플 엑셀 파일
```
---

### 3. ETAS 계정

- 삼영
    - sybus
    - bo8106591*
- 보영
    - bybus
    - **sam00831
- 편안
    - pybus007
    - pybus007!
- 덕장
    - dz007
    - dzbus46438@

---

### 4. API 목록

### 4.2 ETAS 크롤러

#### `crawler/crawler_etas.py`
- `login(driver, user_id, password)`
  - Selenium을 이용한 ETAS 웹 로그인 수행
- `is_change_password_page(driver)`
  - 비밀번호 변경 페이지 노출 여부 확인
- `get_dangerous_driver_list(driver)`
  - ETAS 시스템 내 위험 운전자 목록 조회
- `download_pdf_files(conn, driver, company_id, year_month, risk_level)`
  - 월별 위험 운전자 리포트 PDF 다운로드
- `initialize_driver_page(driver)`
  - 웹 드라이버를 초기 상태로 초기화 하는 함수

---

### 4.3 크롤러 제어 로직

#### `crawler/index.py`
- `get_default_download_path()`
  - 웹 드라이버에서 파일이 다운로드 될 위치를 리턴하는 함수.
- `load_web_driver(user_data_dir)`
  - 웹 드라이버 불러오는 함수
  - user_data_dir: 저장경로 지정 함수.

---

### 4.4 세션 관리

#### `crawler/session_utils.py`
- `check_jsessionid(driver)`
  - 로그인 세션(JSESSIONID) 유효성 검사
- `check_main_page(driver, main_page_url)`
  - ETAS 메인페이지에 접근이 가능한 지 확인하는 함수

---

### 4.5 엑셀 파서

#### `excel_parser/excel_driver_info.py`
- `upload_etas_driver_data(df, conn, companyId)`
  - ETAS 운전자 정보 스운솔 업로드 API

#### `excel_parser/excel_dangerous_driver_stat.py`
- `upload_etas_dangerous_driver_stats(df, conn, companyId, yearMonth)`
  - ETAS에서 뽑은 위험운전 통계 엑셀 데이터를 스운솔에 업로드하는 함수

---

### 5. 실제 업무 프로세스
1. ETAS 운전자 명단 업로드
- ETAS 로그인
- 메인메뉴 -> 운수회사/개인사업자 클릭
- 기초정보관리 -> 운전자정보 관리 진입
- 조회 후 엑셀 다운로드
- 스운솔 업로드 

2. 위험운전통계 자료 업로드
- ETAS 로그인
- 메인메뉴 -> 운수회사/개인사업자 클릭
- 위험운전행동통계 -> 운전자별(배차기준) 메뉴 진입
- 조회 후 전체 자료 보기 -> 엑셀 다운로드
- 스운솔 업로드

3. 위험운전 통계 분석 차트 관리
- ETAS 로그인
- 메인메뉴 -> 운수회사/개인사업자 클릭
- 종합진단표 클릭
- 조회년도 선택 후 조회
- 하단 승무원 목록 상단에 전체 선택, 배치 인쇄 클릭


### 6. 시스템 구조
``` mermaid
flowchart TD

  ETAS[ETAS]
  STS[스운솔]
  DB[(DB)]
  STOR[(S3)]

  SVC[ETAS 연동 서비스 로그인]
  MAP[승무원 맵핑]
  STAT[위험운전 통계 수집]
  EXCELD[엑셀 데이터 다운로드]
  EXCELU[엑셀 데이터 업로드]
  DIAG[종합진단표 수집 기능]
  CRAWL[ETAS Crawler/파이썬 서버]

  STS --> SVC
  SVC --> DIAG
  DIAG --> CRAWL
  CRAWL --> STOR
  CRAWL --> DB
  ETAS --> EXCELD
  STS --> MAP
  STS --> STAT
  EXCELD --> STS
  MAP --> EXCELU
  STAT --> EXCELU
  EXCELU --> CRAWL

  



```

### 7. 유의사항
1. ETAS 데이터는 차량정보로 우선 저장되는 것으로 파악되어, 실제 업로드가 될때 까지 약 5~6달 가량 소요되는 것으로 예상됨.(26.01의 경우 25.08 데이터 조회 가능)

2. 서버 내에서 ETAS 로그인이 되어 있어야 세션으로 원하는 페이지 접근 후 크롤링이 가능.

3. 종합진단표의 경우, 쿼리 파라미터 분석하여 링크에 직접 엑세스하는 방식으로 구성되어 있음.