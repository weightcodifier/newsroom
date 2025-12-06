멋진 아이디어입니다! **"GitHub 자체를 데이터베이스처럼 사용하고, Streamlit Cloud로 배포하며, Gemini로 분석하는 1인 뉴스룸"**을 만드는 구조네요.

Cursor AI를 활용해 빠르게 개발할 수 있도록 **프로젝트 구조**와 **핵심 코드**, 그리고 **Cursor에게 내릴 프롬프트**를 정리해 드립니다.

이 프로젝트의 핵심 기술적 난관은 **Streamlit Cloud는 재부팅 시 로컬 파일이 초기화된다**는 점입니다. 따라서 JSON 파일을 단순히 로컬에 저장하는 것이 아니라, **GitHub API를 통해 리포지토리에 커밋(Push)하는 방식**으로 구현해야 영구 저장이 됩니다.

---

### 1. 프로젝트 구조 (Directory Structure)

먼저 폴더를 만들고 아래 구조를 잡으세요.

```
my-newsroom/
├── app.py                # 메인 실행 파일 (Streamlit UI 및 라우팅)
├── utils_github.py       # GitHub API 연동 (JSON 읽기/쓰기/커밋 담당)
├── utils_logic.py        # RSS 수집 및 Gemini 분석 로직
├── requirements.txt      # 라이브러리 목록
├── .gitignore           # Git 제외 파일 목록
└── .streamlit/
    └── secrets.toml      # API Key 저장소 (로컬 테스트용, 절대 깃허브 업로드 X)
```

---

### 2. 사전 준비 (API Key 발급)

1.  **Google Gemini API Key:** Google AI Studio에서 발급.
2.  **GitHub Personal Access Token (Classic):**
    *   GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
    *   권한: `repo` (전체 체크)
    *   이 토큰이 있어야 파이썬 코드가 당신의 깃허브에 파일을 쓰고 저장할 수 있습니다.

---

### 3. Cursor AI를 위한 단계별 가이드 (프롬프트 포함)

Cursor의 **Composer (Ctrl+I 또는 Cmd+I)** 기능을 켜고 아래 순서대로 요청하세요.

#### Step 1: 라이브러리 설치 및 설정

**Cursor 프롬프트:**
> `requirements.txt` 파일을 생성해줘. 필요한 라이브러리는 `streamlit`, `feedparser`, `google-generativeai`, `PyGithub`, `pandas`, `plotly` 야.

#### Step 1-1: .gitignore 파일 생성

**Cursor 프롬프트:**
> `.gitignore` 파일을 생성해줘. `.streamlit/secrets.toml`, `__pycache__/`, `*.pyc`, `.env` 파일들을 제외하도록 설정해줘.

#### Step 2: GitHub를 DB처럼 쓰는 모듈 구현 (`utils_github.py`)

이 부분이 가장 중요합니다. Streamlit Cloud에서 데이터가 날아가지 않게 하려면 GitHub API로 파일을 직접 수정해야 합니다.

**Cursor 프롬프트:**
> `utils_github.py`를 작성해줘. `PyGithub` 라이브러리를 사용해서 GitHub 리포지토리의 특정 JSON 파일을 읽고(Read), 내용을 수정해서 커밋(Update/Write)하는 기능을 만들어야 해.
>
> 1. `init_github(token, repo_name)` 함수로 인증하고 리포지토리 객체를 반환. 이 함수는 `@st.cache_resource` 데코레이터를 사용해서 한 번만 인증하도록 최적화해줘.
> 2. `load_json(filename)`: 해당 파일이 없으면 빈 json({})을 반환, 있으면 내용을 파싱 해서 반환. `UnknownObjectException`을 구체적으로 처리하고, 네트워크 오류나 기타 예외는 적절한 에러 메시지와 함께 처리해줘.
> 3. `save_json(filename, data, commit_message)`: 데이터를 json으로 변환해 리포지토리에 커밋. 파일이 없으면 생성(create), 있으면 수정(update). `UnknownObjectException`과 기타 예외를 구체적으로 처리해줘.
>
> **중요:** Streamlit Secrets 대신 **비밀번호 입력 방식**을 사용해. `app.py`에서 `st.text_input(type="password")`로 토큰과 리포지토리 이름을 입력받아서 함수 파라미터로 전달하도록 설계해줘.

#### Step 3: RSS 수집 및 Gemini 분석 로직 (`utils_logic.py`)

**Cursor 프롬프트:**
> `utils_logic.py`를 작성해줘.
>
> 1. **RSS 수집**: `feedparser`를 사용해서 뉴스 제목, 링크, 날짜를 가져와. 각 뉴스는 딕셔너리 형태로 `{"title": "...", "link": "...", "date": "..."}` 구조로 저장해줘.
> 2. **중복 방지**: 링크(link)를 기준으로 중복 뉴스를 필터링하는 로직을 추가해줘. 이미 수집된 뉴스는 제외하도록 해.
> 3. **Gemini 분석**: `google.generativeai`를 사용해. 수집된 뉴스 리스트(텍스트)를 프롬프트로 넘겨서 "오늘의 IT 주요 뉴스 3줄 요약 및 핵심 키워드, 그리고 각 뉴스의 한 줄 평"을 Markdown 형식으로 받아오는 함수를 만들어줘. API 호출 실패 시 재시도 로직(최대 3회)을 추가해줘.
> 4. **데이터 구조**: 날짜(YYYY-MM-DD)를 키(Key)로 하는 딕셔너리 구조로 데이터를 관리하도록 해줘. 각 날짜의 값은 다음과 같은 구조를 가져야 해:
>    ```python
>    {
>      "2024-01-15": {
>        "summary": "Gemini가 생성한 마크다운 요약",
>        "news": [
>          {"title": "뉴스 제목", "link": "https://...", "date": "2024-01-15"},
>          ...
>        ],
>        "keywords": ["키워드1", "키워드2", ...]
>      }
>    }
>    ```

#### Step 4: 메인 화면 및 대시보드 UI (`app.py`)

**Cursor 프롬프트:**
> `app.py`를 작성해줘. `utils_github`와 `utils_logic`을 import 해서 사용해. Streamlit으로 다음 기능을 구현해줘.
>
> 1. **인증 섹션 (최상단)**: 
>    - `st.text_input(type="password")`로 GitHub Token, Repo Name, Gemini API Key를 입력받아서 `st.session_state`에 저장해줘. 한 번 입력하면 세션 동안 유지되도록 해.
> 2. **사이드바 메뉴**: "뉴스룸(메인)", "관리 대시보드" 두 개로 나눔.
> 3. **뉴스룸(메인)**:
>    - `news_data.json`을 GitHub에서 불러옴. 로딩 중에는 `st.spinner()`로 표시해줘.
>    - 날짜를 선택(DateInput)하면 해당 날짜의 Gemini 분석 결과(브리핑)와 원본 뉴스 링크들을 보여줌. 날짜가 없으면 "해당 날짜의 뉴스가 없습니다" 메시지 표시.
> 4. **관리 대시보드**:
>    - **RSS 관리**: `feeds.json`을 불러와서 RSS URL을 추가/삭제하는 UI. 기본값으로 몇 개의 IT 뉴스 RSS URL을 미리 넣어줘.
>    - **수집 및 분석 실행 버튼**: 버튼을 누르면 등록된 RSS를 긁어오고 Gemini로 분석한 뒤 `news_data.json`에 오늘 날짜로 저장(GitHub 커밋)하고 페이지 새로고침. 진행 상황을 `st.progress()`와 `st.status()`로 표시해줘.
>    - **접속 통계**: `stats.json`을 불러와서 총 방문자 수를 보여주고, 그래프(Plotly)로 날짜별 접속 추이를 간단히 시각화해줘. `st.session_state`를 활용해 한 세션당 1번만 카운트되게 해서 GitHub 저장.

---

### 4. 핵심 코드 예시 (참고용)

Cursor가 잘 짜주겠지만, **GitHub 연동 부분**은 헷갈릴 수 있어 핵심 로직을 미리 드립니다. 이 코드를 Cursor에게 참고하라고 주면 더 정확합니다.

**`utils_github.py` 예시:**

```python
import streamlit as st
from github import Github
from github import UnknownObjectException
import json
import time

@st.cache_resource
def init_github(token, repo_name):
    """GitHub 인증 및 리포지토리 객체 반환 (캐싱됨)"""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except Exception as e:
        st.error(f"GitHub 인증 실패: {str(e)}")
        return None

def load_json(repo, filename):
    """GitHub에서 JSON 파일 읽기"""
    if repo is None:
        return {}
    
    try:
        contents = repo.get_contents(filename)
        return json.loads(contents.decoded_content.decode())
    except UnknownObjectException:
        # 파일이 없으면 빈 딕셔너리 반환
        return {}
    except Exception as e:
        st.error(f"파일 읽기 실패 ({filename}): {str(e)}")
        return {}

def save_json(repo, filename, data, message="Update data"):
    """GitHub에 JSON 파일 저장 (생성 또는 업데이트)"""
    if repo is None:
        st.error("리포지토리 연결이 없습니다.")
        return False
    
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    
    try:
        contents = repo.get_contents(filename)
        # 파일이 존재하면 업데이트
        repo.update_file(contents.path, message, json_str, contents.sha)
        return True
    except UnknownObjectException:
        # 파일이 없으면 생성
        try:
            repo.create_file(filename, message, json_str)
            return True
        except Exception as e:
            st.error(f"파일 생성 실패 ({filename}): {str(e)}")
            return False
    except Exception as e:
        st.error(f"파일 저장 실패 ({filename}): {str(e)}")
        return False
```

**`app.py` 인증 부분 예시:**

```python
import streamlit as st

# 세션 스테이트 초기화
if "github_token" not in st.session_state:
    st.session_state.github_token = ""
if "repo_name" not in st.session_state:
    st.session_state.repo_name = ""
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""

# 인증 섹션
st.sidebar.header("🔐 인증 설정")
github_token = st.sidebar.text_input(
    "GitHub Token", 
    value=st.session_state.github_token,
    type="password",
    help="GitHub Personal Access Token을 입력하세요"
)
repo_name = st.sidebar.text_input(
    "Repository Name", 
    value=st.session_state.repo_name,
    help="예: username/my-newsroom"
)
gemini_key = st.sidebar.text_input(
    "Gemini API Key", 
    value=st.session_state.gemini_key,
    type="password",
    help="Google Gemini API Key를 입력하세요"
)

# 세션 스테이트에 저장
if github_token:
    st.session_state.github_token = github_token
if repo_name:
    st.session_state.repo_name = repo_name
if gemini_key:
    st.session_state.gemini_key = gemini_key

# 인증 확인
if not all([github_token, repo_name, gemini_key]):
    st.warning("⚠️ 사이드바에서 인증 정보를 입력해주세요.")
    st.stop()
```

**데이터 구조 예시:**

```python
# news_data.json 구조
{
  "2024-01-15": {
    "summary": "## 오늘의 IT 주요 뉴스\n\n1. AI 기술 발전...\n2. 클라우드 시장 확대...\n3. 보안 이슈 대두...",
    "news": [
      {
        "title": "AI 기술의 새로운 전환점",
        "link": "https://example.com/news1",
        "date": "2024-01-15"
      },
      {
        "title": "클라우드 시장 급성장",
        "link": "https://example.com/news2",
        "date": "2024-01-15"
      }
    ],
    "keywords": ["AI", "클라우드", "보안"]
  }
}

# feeds.json 구조
{
  "feeds": [
    "https://feeds.feedburner.com/geeknews",
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.securitynews.co.kr/rss/allArticle.xml"
  ]
}

# stats.json 구조
{
  "total_visits": 150,
  "daily_visits": {
    "2024-01-15": 10,
    "2024-01-16": 15,
    "2024-01-17": 12
  }
}
```

---

### 5. 배포 및 설정 (Streamlit Cloud)

개발이 끝나면 배포를 진행합니다.

1.  **GitHub Push:** 작성한 코드를 GitHub 리포지토리에 올립니다. (이때 `secrets.toml`은 `.gitignore`에 의해 자동으로 제외됩니다)
2.  **Streamlit Cloud 접속:** [streamlit.io](https://streamlit.io) 접속 후 "Deploy an app" 클릭.
3.  **New App:** 리포지토리와 브랜치, `app.py`를 선택.
4.  **Advanced Settings (Secrets):**
    이 부분이 가장 중요합니다. Streamlit Cloud 설정 화면의 Secrets 창에 아래 내용을 입력해야 합니다.

    ```toml
    GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxx"  # 발급받은 깃허브 토큰
    REPO_NAME = "본인아이디/리포지토리이름"
    GEMINI_API_KEY = "AI_Studio에서_발급받은_키"
    ```

    **참고:** 배포 환경에서는 Secrets를 사용하지만, 로컬 테스트에서는 비밀번호 입력 방식을 사용합니다.

5.  **Deploy!**

---

### 6. 팁 (개발 시 주의사항)

*   **방문자 통계 로직:** Streamlit은 상호작용할 때마다 스크립트가 재실행됩니다. 단순히 `count += 1`을 하면 버튼 누를 때마다 올라갑니다. `st.session_state`를 활용해 한 세션당 1번만 카운트되게 하거나, 쿠키 처리를 해야 하지만, 간단하게는 세션 스테이트로 중복 카운팅을 방지하세요.

*   **속도:** GitHub API로 파일을 쓰고 읽는 건 로컬보다 느립니다. 따라서 `load_json` 함수에는 `@st.cache_data(ttl=60)` 같은 데코레이터를 붙여서 API 호출을 줄이는 것이 좋습니다. 다만, **쓰기 작업 전에는 반드시 캐시를 무효화**해야 합니다 (`st.cache_data.clear()`).

*   **GitHub API Rate Limit:** GitHub API는 시간당 5,000회 요청 제한이 있습니다. 너무 자주 호출하면 제한에 걸릴 수 있으니, 캐싱을 적극 활용하고 불필요한 호출을 줄이세요. Rate Limit에 걸리면 `st.warning()`으로 사용자에게 알려주세요.

*   **에러 처리:** 네트워크 오류, API 실패 등 다양한 예외 상황을 고려해 구체적인 에러 메시지를 표시하세요. 사용자가 문제를 파악할 수 있도록 도와주세요.

*   **RSS 소스:** 국내 IT 뉴스는 `GeekNews`, `네이버 뉴스 IT 분야(특정 키워드)`, `보안뉴스` 등의 RSS URL을 미리 확보해두세요. `feeds.json`에 기본값으로 몇 개 넣어두면 편리합니다.

*   **로딩 상태:** GitHub API 호출이나 Gemini 분석은 시간이 걸릴 수 있습니다. `st.spinner()`, `st.progress()`, `st.status()` 등을 활용해 사용자에게 진행 상황을 알려주세요.

*   **중복 방지:** RSS 수집 시 같은 뉴스가 여러 번 수집되지 않도록 링크를 기준으로 중복을 체크하세요. 이미 `news_data.json`에 있는 뉴스는 제외하도록 구현하세요.

---

### 7. .gitignore 예시

```
# Streamlit
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# 환경 변수
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

이제 Cursor를 켜고 위 프롬프트들을 차례대로 입력해 보세요! 자신만의 뉴스룸이 금방 만들어질 겁니다.
