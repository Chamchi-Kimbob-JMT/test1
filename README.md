📝 AI 서술형 평가 시스템 (AI-Based Essay Grading System)이 프로젝트는 Streamlit을 활용하여 학생들의 서술형 답안을 수집하고, OpenAI (GPT) API를 통해 자동 채점 및 피드백을 제공하며, 결과 데이터를 Supabase 데이터베이스에 저장하는 올인원 웹 애플리케이션입니다.📊 시스템 구조 및 흐름 (System Flow)이 시스템은 크게 학생 입력, AI 채점, DB 저장의 3단계로 구성됩니다.graph TD
    A[🧑‍🎓 학생] -->|1. 학번 & 답안 입력| B(📝 Streamlit 웹 인터페이스)
    B -->|2. 제출 버튼 클릭| C{✅ 유효성 검사}
    C -->|성공| D[💾 세션 상태 저장]
    D -->|3. GPT 피드백 요청| E[🤖 OpenAI API]
    E -->|4. 채점 결과 반환 O/X| B
    E -.->|5. 데이터 자동 저장| F[(🗄️ Supabase DB)]
    
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px
🚀 핵심 기능답안 수집 UI: 학번 및 3개의 서술형 문항 답안 입력 폼 제공.자동 유효성 검사: 빈 칸 제출 방지.AI 자동 채점: 교사가 설정한 가이드라인에 따라 GPT가 정오답(O/X) 판정 및 피드백 생성.클라우드 저장: 채점 결과와 답안을 Supabase 테이블에 실시간 저장.🛠️ 설치 및 설정 (Installation & Setup)1. 필수 라이브러리 설치터미널에서 아래 명령어를 실행하여 필요한 패키지를 설치하세요.pip install streamlit openai supabase
2. Secrets 설정 (.streamlit/secrets.toml)프로젝트 루트 경로에 .streamlit 폴더를 만들고, 그 안에 secrets.toml 파일을 생성하여 아래 내용을 작성해야 합니다.# .streamlit/secrets.toml

OPENAI_API_KEY = "sk-..."  # OpenAI API 키

[supabase]
SUPABASE_URL = "[https://your-project.supabase.co](https://your-project.supabase.co)"
SUPABASE_SERVICE_ROLE_KEY = "eyJ..." # 주의: Service Role Key 사용 (서버용)
📂 코드 상세 설명 (Code Structure)제공된 코드는 크게 두 가지 단계(Step)로 나뉩니다.🔹 Step 1: UI 구성 및 입력 처리사용자가 답안을 작성하고 제출하는 부분입니다.st.form: 입력란과 제출 버튼을 하나의 폼으로 묶어, 버튼 클릭 시에만 데이터가 전송되도록 처리합니다.Session State: submitted_ok 상태를 관리하여, 제출이 완료된 후에만 AI 피드백 버튼이 활성화되도록 제어합니다.🔹 Step 2: AI 채점 및 DB 저장제출된 데이터를 바탕으로 심화 로직을 수행하는 부분입니다.Supabase 연결 (get_supabase_client):@st.cache_resource를 사용하여 DB 연결을 효율적으로 관리합니다.제출된 답안, 피드백, 모델 정보 등을 student_submissions 테이블에 insert 합니다.AI 채점 로직:GRADING_GUIDELINES: 문항별 정답 기준을 딕셔너리로 관리합니다.Prompting: AI에게 "교사" 페르소나를 부여하고, 반드시 O: ... 또는 X: ... 형식으로 출력하도록 지시합니다.후처리 (normalize_feedback): AI 응답 형식이 깨져도 UI가 망가지지 않도록 텍스트를 규격화합니다.🗄️ 데이터베이스 스키마 (Supabase)Supabase의 student_submissions 테이블은 아래 컬럼을 포함해야 합니다.컬럼명데이터 타입설명idint8 (Primary)고유 ID (자동 생성)student_idtext학번answer_1 ~ 3text학생 답안feedback_1 ~ 3textAI 피드백 결과guideline_1 ~ 3text채점 당시 기준modeltext사용된 AI 모델명created_attimestamptz생성 일시 (Default: now())⚠️ 주의사항API 비용: OpenAI API 호출 횟수에 따라 비용이 발생하므로 테스트 시 유의하세요.보안: secrets.toml 파일은 깃허브 등에 절대 업로드하지 마세요 (.gitignore 추가 필수).Supabase Key: 코드에서는 쓰기 권한이 있는 SERVICE_ROLE_KEY를 사용하므로 키 관리에 주의해야 합니다.Note: 이 프로젝트는 교육용 도구 프로토타입이며, 실제 수업 적용 시 네트워크 환경 및 트래픽에 따른 최적화가 필요할 수 있습니다.
