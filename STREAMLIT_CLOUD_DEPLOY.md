# Streamlit Cloud 배포 가이드

## 1. GitHub에 코드 푸시

코드가 이미 GitHub에 푸시되어 있다면 이 단계를 건너뛰세요.

```bash
git add .
git commit -m "Streamlit Cloud 배포 준비"
git push origin main
```

## 2. Streamlit Cloud에서 앱 배포

1. [Streamlit Cloud](https://share.streamlit.io) 접속
2. "New app" 클릭
3. GitHub 리포지토리 선택: `weightcodifier/newsroom`
4. 브랜치: `main`
5. Main file path: `app.py`

## 3. ⚠️ 중요: Secrets 설정

**가장 중요한 단계입니다!** 앱을 배포하기 전에 반드시 Secrets를 설정해야 합니다.

### Secrets 설정 방법:

1. 앱 설정 페이지에서 **"Secrets"** 탭 클릭
2. 아래 내용을 입력:

```toml
GEMINI_API_KEY = "AIzaSyBy9o2oIR7w4EcQ4gECfyP9qx9waCKSMC0"
```

3. **"Save"** 클릭
4. 앱이 자동으로 재배포됩니다

### Gemini API Key 발급 방법:

1. [Google AI Studio](https://aistudio.google.com) 접속
2. "Get API key" 클릭
3. 새 API 키 생성 또는 기존 키 사용
4. 생성된 키를 복사하여 Streamlit Cloud Secrets에 붙여넣기

## 4. 배포 확인

Secrets를 설정한 후:
- 앱이 자동으로 재배포됩니다
- 배포가 완료되면 앱 URL로 접속하여 정상 작동 확인
- 오류가 발생하면 Streamlit Cloud 로그를 확인하세요

## 5. 문제 해결

### "GEMINI_API_KEY가 없습니다" 오류가 계속 발생하는 경우:

1. ✅ Secrets 탭에서 키가 올바르게 입력되었는지 확인
2. ✅ 키 앞뒤에 따옴표가 있는지 확인 (TOML 형식)
3. ✅ "Save" 버튼을 클릭했는지 확인
4. ✅ 앱이 재배포되었는지 확인 (몇 분 소요될 수 있음)

### 로컬과 Cloud 환경 차이:

- **로컬**: `.streamlit/secrets.toml` 파일 사용
- **Streamlit Cloud**: 앱 설정의 Secrets 탭 사용
- 두 환경 모두 `st.secrets["GEMINI_API_KEY"]`로 접근 가능

## 참고사항

- Secrets는 암호화되어 저장되며 안전하게 관리됩니다
- Secrets를 변경하면 앱이 자동으로 재배포됩니다
- Secrets 내용은 GitHub에 푸시되지 않습니다 (보안)

