import feedparser
import google.generativeai as genai
from datetime import datetime
import time
import streamlit as st
import logging

# 로깅 설정 (보고서 8.2 해결)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_rss_feeds(feed_urls):
    """RSS 피드를 수집하고 통합합니다."""
    all_news = []
    
    for feed_url in feed_urls:
        try:
            feed = feedparser.parse(feed_url)
            
            # RSS 파싱 오류 체크 (보고서 4.2)
            if feed.bozo:
                logger.warning(f"RSS 파싱 경고 ({feed_url}): {feed.bozo_exception}")
                st.warning(f"RSS 피드 파싱 경고: {feed_url}")
            
            if not feed.entries:
                logger.info(f"뉴스 없음: {feed_url}")
                continue
            
            for entry in feed.entries:
                # 날짜 파싱 (보고서 4.2 해결)
                date_str = ""
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        date_str = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        date_str = datetime.now().strftime("%Y-%m-%d")
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    try:
                        date_str = datetime(*entry.updated_parsed[:6]).strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        date_str = datetime.now().strftime("%Y-%m-%d")
                else:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                
                news_item = {
                    "title": entry.get("title", "제목 없음"),
                    "link": entry.get("link", ""),
                    "date": date_str
                }
                all_news.append(news_item)
        except Exception as e:
            logger.error(f"RSS 수집 실패 ({feed_url}): {e}")
            st.warning(f"{feed_url} 수집 중 오류가 발생했습니다: {str(e)}")
            continue
    
    return all_news


def filter_duplicates(new_news, existing_news_data):
    """중복 뉴스 필터링 (링크 기준)"""
    existing_links = set()
    
    # 기존 뉴스의 모든 링크 수집
    for date_key, date_data in existing_news_data.items():
        if "news" in date_data:
            for news_item in date_data["news"]:
                existing_links.add(news_item.get("link", ""))
    
    # 중복되지 않은 뉴스만 반환
    filtered_news = []
    for news in new_news:
        if news.get("link", "") not in existing_links:
            filtered_news.append(news)
    
    return filtered_news


def analyze_with_gemini(news_list, api_key, max_retries=3):
    """Gemini로 뉴스를 분석합니다. (재시도 로직 포함) - 보고서 5.1 해결"""
    if not api_key:
        return "", []
    
    if not news_list:
        return "수집된 뉴스가 없습니다.", []
    
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return f"Gemini API 설정 실패: {str(e)}", []
    
    # 뉴스 리스트를 텍스트로 변환
    news_text = "\n\n".join([
        f"{i+1}. {news['title']}\n   링크: {news['link']}"
        for i, news in enumerate(news_list[:20])  # 최대 20개만 분석
    ])
    
    prompt = f"""다음은 오늘 수집된 IT 뉴스 목록입니다. 이 뉴스들을 분석해서 다음 형식으로 정리해주세요:

## 오늘의 IT 주요 뉴스 요약

(3줄로 핵심 내용 요약)

## 핵심 키워드

- 키워드1
- 키워드2
- 키워드3

## 각 뉴스 한 줄 평

1. [뉴스 제목]: (한 줄 평)
2. [뉴스 제목]: (한 줄 평)
...

---

뉴스 목록:
{news_text}
"""
    
    # 사용 가능한 모델 목록 시도 (우선순위 순) - Gemini 2.0 Flash 우선
    model_names = ['gemini-2.0-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-1.5-pro']
    last_error = None
    
    # 각 모델을 순차적으로 시도
    for model_name in model_names:
        # 재시도 로직 (보고서 5.1)
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                summary = response.text
                
                # 키워드 추출 (간단한 방법)
                keywords = []
                if "## 핵심 키워드" in summary:
                    keyword_section = summary.split("## 핵심 키워드")[1].split("##")[0]
                    for line in keyword_section.split("\n"):
                        line = line.strip()
                        if line.startswith("-") and len(line) > 1:
                            keywords.append(line[1:].strip())
                
                logger.info(f"성공적으로 {model_name} 모델 사용")
                return summary, keywords
                
            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                
                # 모델을 찾을 수 없으면 다음 모델 시도
                if "404" in error_msg or "not found" in error_msg.lower():
                    logger.warning(f"모델 {model_name}을 찾을 수 없음, 다음 모델 시도...")
                    break  # 다음 모델로
                
                # Rate Limit이나 서비스 오류는 재시도
                if "429" in error_msg or "Resource has been exhausted" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Gemini API Rate Limit, {wait_time}초 대기 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"AI 분석 실패: API 사용량 초과. 잠시 후 다시 시도하세요.", []
                elif "503" in error_msg or "Service Unavailable" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Gemini 서비스 일시 중단, {wait_time}초 대기 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"AI 분석 실패: Gemini 서비스가 일시적으로 사용 불가능합니다.", []
                else:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Gemini API 오류, {wait_time}초 대기 후 재시도: {error_msg}")
                        time.sleep(wait_time)
                        continue
                    else:
                        # 마지막 시도 실패 시 다음 모델로
                        break
    
    # 모든 모델 시도 실패
    return f"AI 분석 실패: 사용 가능한 모델을 찾을 수 없습니다. (마지막 오류: {last_error})", []
    
    return "분석 실패", []


def format_news_data(news_list, summary, keywords, date_str):
    """뉴스 데이터를 저장 형식으로 변환"""
    return {
        "summary": summary,
        "news": news_list,
        "keywords": keywords
    }
