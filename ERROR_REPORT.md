# 🐛 오류 보고서 (Error Report)

## 1인 뉴스룸 프로젝트 - 오류 진단 및 해결 가이드

---

## 📋 목차

1. [일반적인 오류 유형](#일반적인-오류-유형)
2. [인증 관련 오류](#인증-관련-오류)
3. [GitHub API 오류](#github-api-오류)
4. [RSS 수집 오류](#rss-수집-오류)
5. [Gemini API 오류](#gemini-api-오류)
6. [데이터 처리 오류](#데이터-처리-오류)
7. [디버깅 가이드](#디버깅-가이드)
8. [로그 확인 방법](#로그-확인-방법)

---

## 일반적인 오류 유형

### 1.1 모듈 Import 오류

**증상:**
```
ModuleNotFoundError: No module named 'streamlit'
ModuleNotFoundError: No module named 'feedparser'
ModuleNotFoundError: No module named 'google.generativeai'
```

**원인:**
- 필요한 라이브러리가 설치되지 않음

**해결 방법:**
```bash
pip install -r requirements.txt
```

**예방:**
- 프로젝트 시작 전 `requirements.txt` 확인
- 가상환경 사용 권장

---

### 1.2 Streamlit 실행 오류

**증상:**
```
Streamlit is not recognized as an internal or external command
```

**원인:**
- Streamlit이 설치되지 않았거나 PATH에 없음

**해결 방법:**
```bash
# Streamlit 재설치
pip install streamlit

# 또는 Python 모듈로 직접 실행
python -m streamlit run app.py
```

---

## 인증 관련 오류

### 2.1 GitHub 인증 실패

**증상:**
```
GitHub 인증 실패: Bad credentials
GitHub 인증 실패: 401 Unauthorized
```

**원인:**
- 잘못된 GitHub Token
- 만료된 Token
- Token 권한 부족

**해결 방법:**
1. GitHub Settings → Developer settings → Personal access tokens 확인
2. 새 Token 생성 (권한: `repo` 전체 체크)
3. Token 형식 확인: `ghp_`로 시작해야 함
4. 사이드바에서 Token 재입력

**예방:**
- Token은 안전하게 보관
- 정기적으로 Token 갱신

---

### 2.2 리포지토리 이름 오류

**증상:**
```
GitHub 인증 실패: 404 Not Found
GitHub 인증 실패: Repository not found
```

**원인:**
- 잘못된 리포지토리 이름 형식
- 존재하지 않는 리포지토리
- 접근 권한 없음

**해결 방법:**
1. 리포지토리 이름 형식 확인: `username/repository-name`
2. GitHub에서 리포지토리 존재 확인
3. 리포지토리 접근 권한 확인
4. Token에 해당 리포지토리 접근 권한이 있는지 확인

**올바른 형식 예시:**
- ✅ `username/my-newsroom`
- ✅ `github-username/newsroom-app`
- ❌ `https://github.com/username/my-newsroom` (URL 형식 불가)
- ❌ `username my-newsroom` (공백 불가)

---

### 2.3 Gemini API Key 오류

**증상:**
```
분석 실패: API key not valid
분석 실패: 403 Forbidden
```

**원인:**
- 잘못된 API Key
- 만료된 API Key
- API Key 형식 오류

**해결 방법:**
1. Google AI Studio에서 새 API Key 발급
2. API Key 형식 확인 (일반적으로 `AIza...`로 시작)
3. API Key 사용량 및 제한 확인
4. 사이드바에서 API Key 재입력

**예방:**
- API Key는 안전하게 보관
- API 사용량 모니터링

---

## GitHub API 오류

### 3.1 Rate Limit 초과

**증상:**
```
파일 읽기 실패: 403 API rate limit exceeded
파일 저장 실패: 403 API rate limit exceeded
```

**원인:**
- GitHub API 시간당 5,000회 요청 제한 초과
- 너무 빈번한 API 호출

**해결 방법:**
1. 잠시 대기 후 재시도 (약 1시간)
2. 캐싱 활용 확인 (`@st.cache_data` 데코레이터)
3. 불필요한 API 호출 줄이기
4. 앱 새로고침 최소화

**예방:**
- `load_json` 함수는 캐싱 사용 (TTL: 60초)
- 한 번에 여러 작업 수행 시 배치 처리
- 사용자 액션에 따른 불필요한 호출 방지

---

### 3.2 파일 읽기 실패

**증상:**
```
파일 읽기 실패: 404 Not Found
파일 읽기 실패: Network error
```

**원인:**
- 파일이 존재하지 않음 (정상 - 첫 실행 시)
- 네트워크 연결 문제
- 리포지토리 접근 권한 없음

**해결 방법:**
1. 첫 실행 시 정상 동작 (빈 딕셔너리 반환)
2. 네트워크 연결 확인
3. 리포지토리 권한 확인
4. GitHub 서비스 상태 확인

**참고:**
- `news_data.json`, `feeds.json`, `stats.json`이 없어도 정상 동작
- 첫 실행 시 자동으로 생성됨

---

### 3.3 파일 저장 실패

**증상:**
```
파일 저장 실패: 422 Unprocessable Entity
파일 저장 실패: 409 Conflict
```

**원인:**
- 동시 수정 충돌
- 잘못된 데이터 형식
- 파일 크기 제한 초과

**해결 방법:**
1. 페이지 새로고침 후 재시도
2. 데이터 형식 확인 (JSON 유효성)
3. 큰 데이터는 분할 저장 고려
4. GitHub에서 직접 파일 확인

**예방:**
- 저장 전 데이터 검증
- 충돌 방지를 위한 재시도 로직

---

## RSS 수집 오류

### 4.1 RSS 피드 연결 실패

**증상:**
```
RSS 피드 수집 실패: [Errno 11001] getaddrinfo failed
RSS 피드 수집 실패: 404 Not Found
```

**원인:**
- 잘못된 RSS URL
- 네트워크 연결 문제
- RSS 피드 서버 다운

**해결 방법:**
1. RSS URL 유효성 확인 (브라우저에서 직접 접속)
2. 네트워크 연결 확인
3. RSS 피드 URL 업데이트
4. 대체 RSS 피드 사용

**RSS URL 확인 방법:**
- 브라우저에서 URL 직접 접속
- XML 형식으로 표시되어야 함
- Feed Validator 사용: https://validator.w3.org/feed/

---

### 4.2 RSS 파싱 오류

**증상:**
```
수집된 뉴스가 없습니다
AttributeError: 'NoneType' object has no attribute 'entries'
```

**원인:**
- RSS 형식이 표준과 다름
- 빈 RSS 피드
- 날짜 파싱 실패

**해결 방법:**
1. RSS 피드 형식 확인
2. 다른 RSS 피드로 테스트
3. 날짜 정보가 없는 경우 오늘 날짜로 대체 (정상 동작)
4. `utils_logic.py`의 예외 처리 확인

**참고:**
- 날짜 정보가 없으면 자동으로 오늘 날짜 사용
- 빈 피드는 건너뛰고 다음 피드 처리

---

## Gemini API 오류

### 5.1 API 호출 실패

**증상:**
```
분석 실패: 429 Resource has been exhausted
분석 실패: 503 Service Unavailable
```

**원인:**
- API 사용량 초과
- Gemini 서비스 일시 중단
- 네트워크 문제

**해결 방법:**
1. 잠시 대기 후 재시도 (자동 재시도 3회)
2. Google AI Studio에서 사용량 확인
3. API Key 제한 확인
4. 네트워크 연결 확인

**예방:**
- API 사용량 모니터링
- 재시도 로직 활용 (이미 구현됨)

---

### 5.2 응답 파싱 오류

**증상:**
```
키워드 추출 실패
요약 형식이 예상과 다름
```

**원인:**
- Gemini 응답 형식 변경
- 프롬프트 이해 실패

**해결 방법:**
1. 프롬프트 명확화
2. 응답 형식 검증 로직 추가
3. 키워드 추출 로직 개선
4. 수동으로 요약 확인

**참고:**
- 키워드가 없어도 요약은 정상 표시
- 키워드 추출은 보조 기능

---

## 데이터 처리 오류

### 6.1 JSON 파싱 오류

**증상:**
```
JSONDecodeError: Expecting value
json.decoder.JSONDecodeError: Invalid control character
```

**원인:**
- 손상된 JSON 파일
- 인코딩 문제
- GitHub에서 수동 수정 시 오류

**해결 방법:**
1. GitHub에서 JSON 파일 직접 확인
2. JSON 유효성 검사 도구 사용
3. 파일 삭제 후 재생성
4. `ensure_ascii=False` 옵션 확인

**예방:**
- GitHub에서 직접 수정 시 주의
- JSON 형식 준수

---

### 6.2 날짜 형식 오류

**증상:**
```
ValueError: time data 'invalid-date' does not match format '%Y-%m-%d'
KeyError: '2024-01-15'
```

**원인:**
- 날짜 형식 불일치
- 잘못된 날짜 키

**해결 방법:**
1. 날짜 형식 확인: `YYYY-MM-DD`
2. `datetime.strptime()` 사용 시 형식 일치 확인
3. 날짜 선택 시 유효한 날짜만 표시

**참고:**
- 날짜는 항상 `YYYY-MM-DD` 형식 사용
- 날짜 파싱 실패 시 오늘 날짜로 대체

---

## 디버깅 가이드

### 7.1 단계별 디버깅

1. **인증 확인**
   ```python
   # app.py에서 확인
   print(f"Token: {github_token[:10]}...")
   print(f"Repo: {repo_name}")
   print(f"Gemini Key: {gemini_key[:10]}...")
   ```

2. **GitHub 연결 확인**
   ```python
   # utils_github.py에서 확인
   repo = init_github(token, repo_name)
   if repo:
       print(f"Repository: {repo.full_name}")
   ```

3. **RSS 피드 확인**
   ```python
   # utils_logic.py에서 확인
   feed = feedparser.parse(feed_url)
   print(f"Feed entries: {len(feed.entries)}")
   ```

4. **Gemini API 확인**
   ```python
   # utils_logic.py에서 확인
   try:
       model = genai.GenerativeModel('gemini-pro')
       response = model.generate_content("테스트")
       print("Gemini API 정상")
   except Exception as e:
       print(f"Gemini 오류: {e}")
   ```

---

### 7.2 일반적인 디버깅 순서

1. ✅ 라이브러리 설치 확인
2. ✅ 인증 정보 확인
3. ✅ 네트워크 연결 확인
4. ✅ GitHub 리포지토리 접근 확인
5. ✅ RSS 피드 URL 확인
6. ✅ Gemini API Key 확인
7. ✅ 데이터 형식 확인

---

## 로그 확인 방법

### 8.1 Streamlit 로그

**터미널에서 확인:**
```bash
streamlit run app.py
# 터미널에 오류 메시지 표시
```

**주요 로그 위치:**
- 콘솔 출력 (터미널)
- Streamlit UI의 에러 메시지
- 브라우저 개발자 도구 (F12)

---

### 8.2 Python 로그 추가

**utils_logic.py에 로깅 추가:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_rss_feeds(feed_urls):
    logger.info(f"RSS 피드 수집 시작: {len(feed_urls)}개")
    # ...
```

---

### 8.3 오류 추적

**예외 처리 개선:**
```python
try:
    # 코드 실행
except Exception as e:
    import traceback
    st.error(f"오류 발생: {str(e)}")
    st.code(traceback.format_exc())
```

---

## 빠른 문제 해결 체크리스트

### ✅ 인증 문제
- [ ] GitHub Token이 올바른가?
- [ ] 리포지토리 이름 형식이 올바른가? (`username/repo-name`)
- [ ] Gemini API Key가 유효한가?
- [ ] 모든 인증 정보가 입력되었는가?

### ✅ 네트워크 문제
- [ ] 인터넷 연결이 정상인가?
- [ ] GitHub 서비스가 정상인가?
- [ ] RSS 피드 URL이 접근 가능한가?

### ✅ 데이터 문제
- [ ] JSON 파일이 손상되지 않았는가?
- [ ] 날짜 형식이 올바른가? (`YYYY-MM-DD`)
- [ ] 데이터 구조가 예상과 일치하는가?

### ✅ API 문제
- [ ] GitHub API Rate Limit에 걸리지 않았는가?
- [ ] Gemini API 사용량이 초과되지 않았는가?
- [ ] API Key가 만료되지 않았는가?

---

## 자주 묻는 질문 (FAQ)

### Q1: "수집된 뉴스가 없습니다" 메시지가 나옵니다.
**A:** RSS 피드에서 뉴스를 가져오지 못했습니다. RSS URL을 확인하고, 네트워크 연결을 확인하세요.

### Q2: "새로운 뉴스가 없습니다" 메시지가 나옵니다.
**A:** 정상 동작입니다. 모든 뉴스가 이미 수집되어 있어서 새 뉴스가 없는 것입니다.

### Q3: GitHub에 파일이 저장되지 않습니다.
**A:** GitHub Token 권한을 확인하세요. `repo` 권한이 필요합니다. 또한 Rate Limit에 걸리지 않았는지 확인하세요.

### Q4: Gemini 분석이 실패합니다.
**A:** API Key가 유효한지, 사용량이 초과되지 않았는지 확인하세요. 네트워크 연결도 확인하세요.

### Q5: 날짜별 뉴스가 표시되지 않습니다.
**A:** 해당 날짜에 수집된 뉴스가 없습니다. 관리 대시보드에서 뉴스를 수집하세요.

---

## 추가 지원

문제가 지속되면 다음 정보를 포함하여 보고하세요:

1. 오류 메시지 전체 내용
2. 발생한 단계 (인증, RSS 수집, 분석, 저장 등)
3. 사용한 입력값 (민감 정보 제외)
4. 환경 정보 (OS, Python 버전, 라이브러리 버전)

---

**마지막 업데이트:** 2024-01-XX
**버전:** 1.0.0

