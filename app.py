import streamlit as st
from datetime import datetime, date
import utils_local as db
import utils_logic as logic
import plotly.express as px
import pandas as pd
import traceback  # 상세 에러 확인용

# 페이지 설정
st.set_page_config(
    page_title="1인 뉴스룸 (로컬)",
    page_icon="🏠",
    layout="wide"
)

# 세션 스테이트 초기화
if "visited" not in st.session_state:
    st.session_state.visited = False

# 필수 설정 확인 (Gemini API Key만 필요)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🚨 .streamlit/secrets.toml에 GEMINI_API_KEY가 없습니다.")
    st.info("💡 Google AI Studio에서 Gemini API Key를 발급받아 secrets.toml에 추가하세요.")
    st.stop()

gemini_key = st.secrets["GEMINI_API_KEY"]

# 방문 통계 업데이트 (한 세션당 1번만)
if not st.session_state.visited:
    try:
        stats = db.load_json("stats.json")
        if "total_visits" not in stats:
            stats["total_visits"] = 0
        if "daily_visits" not in stats:
            stats["daily_visits"] = {}
        
        today = datetime.now().strftime("%Y-%m-%d")
        stats["total_visits"] += 1
        stats["daily_visits"][today] = stats["daily_visits"].get(today, 0) + 1
        
        # 통계 저장은 실패해도 메인 기능에 영향 없도록
        db.save_json("stats.json", stats)
        st.session_state.visited = True
    except Exception:
        pass  # 통계 저장 실패해도 계속 진행

# 사이드바 메뉴
st.sidebar.header("🏠 로컬 모드")
st.sidebar.info("데이터는 `./data` 폴더에 저장됩니다.")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["📰 뉴스룸(메인)", "⚙️ 관리 대시보드"]
)

# 메인 화면
if menu == "📰 뉴스룸(메인)":
    st.title("📰 1인 IT 뉴스룸 (로컬 모드)")
    st.caption("내 컴퓨터에 저장된 데이터로 브리핑을 보여줍니다.")
    
    # 뉴스 데이터 로드
    with st.spinner("뉴스 데이터를 불러오는 중..."):
        news_data = db.load_json("news_data.json")
    
    if not news_data:
        st.info("📭 아직 저장된 뉴스가 없습니다. '관리 대시보드'에서 뉴스를 수집해주세요.")
    else:
        # 날짜 선택
        available_dates = sorted(news_data.keys(), reverse=True)
        selected_date = st.selectbox(
            "날짜 선택",
            available_dates,
            index=0
        )
        
        date_str = selected_date
        
        if date_str in news_data:
            date_info = news_data[date_str]
            
            # 2단 레이아웃
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("## 📋 오늘의 뉴스 요약")
                summary = date_info.get("summary", "요약이 없습니다.")
                st.markdown(summary)
                
                # 키워드 표시
                if date_info.get("keywords"):
                    st.markdown("### 🔑 핵심 키워드")
                    keywords_text = " | ".join([f"**{kw}**" for kw in date_info["keywords"]])
                    st.markdown(keywords_text)
            
            with col2:
                st.subheader("🔗 원본 링크")
                news_list = date_info.get("news", [])
                for i, news in enumerate(news_list[:10], 1):
                    st.markdown(f"{i}. [{news.get('title', '제목 없음')}]({news.get('link', '#')})")
                    st.caption(f"📅 {news.get('date', '날짜 없음')}")

# 관리 대시보드
elif menu == "⚙️ 관리 대시보드":
    st.title("⚙️ 관리 대시보드")
    
    # 탭 구분
    tab1, tab2, tab3 = st.tabs(["📡 RSS 관리", "🔄 수집 및 분석", "📊 시스템 상태"])
    
    # 1. RSS 관리
    with tab1:
        st.subheader("RSS 피드 목록")
        feeds_data = db.load_json("feeds.json")
        
        # 데이터 구조 호환성 유지
        if "feeds" in feeds_data:
            current_feeds = feeds_data["feeds"]
        elif "urls" in feeds_data:
            current_feeds = feeds_data["urls"]
        else:
            current_feeds = []
            # 기본 RSS 피드
            if not current_feeds:
                current_feeds = [
                    "https://feeds.feedburner.com/geeknews",
                    "https://rss.cnn.com/rss/edition.rss"
                ]
        
        new_feed = st.text_input("새 RSS URL 추가")
        if st.button("추가"):
            if new_feed and new_feed not in current_feeds:
                current_feeds.append(new_feed)
                # 호환성을 위해 "feeds" 키 사용
                db.save_json("feeds.json", {"feeds": current_feeds})
                st.success("RSS 피드가 추가되었습니다!")
                st.rerun()
            elif new_feed in current_feeds:
                st.warning("이미 등록된 RSS 피드입니다.")
        
        st.markdown("---")
        st.write("등록된 피드:")
        for i, feed_url in enumerate(current_feeds):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.text(feed_url)
            with c2:
                if st.button("삭제", key=f"delete_{i}"):
                    current_feeds.pop(i)
                    db.save_json("feeds.json", {"feeds": current_feeds})
                    st.rerun()
    
    # 2. 수집 및 분석 (핵심 기능)
    with tab2:
        st.subheader("뉴스 수집 및 AI 분석 실행")
        if st.button("🚀 실행 (Start)", type="primary"):
            try:
                # 1. RSS 불러오기
                feeds_data = db.load_json("feeds.json")
                if "feeds" in feeds_data:
                    urls = feeds_data["feeds"]
                elif "urls" in feeds_data:
                    urls = feeds_data["urls"]
                else:
                    urls = []
                
                if not urls:
                    st.error("등록된 RSS 피드가 없습니다. 'RSS 관리' 탭에서 피드를 추가해주세요.")
                else:
                    with st.spinner("1/3 RSS 뉴스 수집 중..."):
                        raw_news = logic.fetch_rss_feeds(urls)
                    
                    if not raw_news:
                        st.warning("수집된 뉴스가 없습니다.")
                    else:
                        # 2. 중복 필터링
                        with st.spinner("중복 뉴스 필터링 중..."):
                            news_data = db.load_json("news_data.json")
                            filtered_news = logic.filter_duplicates(raw_news, news_data)
                        
                        if not filtered_news:
                            st.info("새로운 뉴스가 없습니다. 모든 뉴스가 이미 수집되어 있습니다.")
                        else:
                            # 3. AI 분석
                            with st.spinner(f"2/3 Gemini AI 분석 중... ({len(filtered_news)}개 뉴스)"):
                                summary, keywords = logic.analyze_with_gemini(filtered_news, gemini_key)
                            
                            # 4. 로컬 저장
                            with st.spinner("3/3 결과 저장 중..."):
                                today_str = datetime.now().strftime("%Y-%m-%d")
                                
                                # 기존 데이터 로드
                                full_data = db.load_json("news_data.json")
                                
                                # 오늘 데이터 업데이트
                                if today_str not in full_data:
                                    full_data[today_str] = {
                                        "summary": "",
                                        "news": [],
                                        "keywords": []
                                    }
                                
                                # 기존 뉴스와 새 뉴스 합치기
                                existing_news = full_data[today_str].get("news", [])
                                all_news = existing_news + filtered_news
                                
                                # 요약 업데이트 (새 뉴스가 있으면)
                                if summary:
                                    full_data[today_str]["summary"] = summary
                                if keywords:
                                    full_data[today_str]["keywords"] = keywords
                                
                                full_data[today_str]["news"] = all_news
                                full_data[today_str]["updated_at"] = datetime.now().strftime("%H:%M:%S")
                                
                                if db.save_json("news_data.json", full_data):
                                    st.success(f"✅ {len(filtered_news)}개의 새로운 뉴스가 수집되고 분석되었습니다!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("저장에 실패했습니다.")
            
            except Exception as e:
                st.error("❌ 작업 중 오류가 발생했습니다.")
                # 상세 에러 로그
                with st.expander("오류 상세 내용 (개발자용)"):
                    st.code(traceback.format_exc())
                    st.write(f"**오류 메시지:** {str(e)}")
    
    # 3. 시스템 상태 (통계)
    with tab3:
        st.subheader("📊 접속 통계")
        stats = db.load_json("stats.json")
        total_visits = stats.get("total_visits", 0)
        daily_visits = stats.get("daily_visits", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 방문자 수", total_visits)
        with col2:
            today = datetime.now().strftime("%Y-%m-%d")
            today_visits = daily_visits.get(today, 0)
            st.metric("오늘 방문자 수", today_visits)
        
        # 그래프
        if daily_visits:
            df = pd.DataFrame([
                {"날짜": date, "방문자 수": count}
                for date, count in sorted(daily_visits.items())
            ])
            
            fig = px.line(df, x="날짜", y="방문자 수", title="날짜별 접속 추이")
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig, use_container_width=True)
        
        # 시스템 연결 상태 점검
        st.markdown("---")
        st.subheader("🔧 시스템 연결 상태")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("✅ 로컬 저장소: 연결됨 (./data 폴더)")
        with col2:
            if "GEMINI_API_KEY" in st.secrets:
                st.success("✅ Gemini API: 연결됨")
            else:
                st.error("❌ Gemini API: 미설정")
