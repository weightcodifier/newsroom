import streamlit as st
from github import Github
from github import GithubException
from github import UnknownObjectException
import json


@st.cache_resource
def init_github(token, repo_name):
    """GitHub 인증 및 리포지토리 객체 반환 (캐싱됨)"""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except GithubException as e:
        if e.status == 401:
            st.error("GitHub 인증 실패: Token을 확인하세요. (보고서 2.1)")
        elif e.status == 404:
            st.error(f"리포지토리를 찾을 수 없습니다: {repo_name}. 리포지토리 이름을 확인하세요. (보고서 2.2)")
        elif e.status == 403:
            st.warning("API 요청 한도 초과 (Rate Limit). 잠시 후 다시 시도하세요. (보고서 3.1)")
        else:
            st.error(f"GitHub 오류 발생 ({e.status}): {str(e)}")
        return None
    except Exception as e:
        st.error(f"GitHub 인증 실패: {str(e)}")
        return None


@st.cache_data(ttl=60)
def load_json(repo, filename):
    """GitHub에서 JSON 파일 읽기 (캐싱됨) - API 호출 횟수 절약 (보고서 3.1 해결)"""
    if repo is None:
        return {}
    
    try:
        contents = repo.get_contents(filename)
        return json.loads(contents.decoded_content.decode())
    except UnknownObjectException:
        # 파일이 없는 경우 (첫 실행) -> 정상적인 빈 값 반환
        return {}
    except GithubException as e:
        if e.status == 401:
            st.error("GitHub 인증 실패: Token을 확인하세요. (보고서 2.1)")
        elif e.status == 403:
            st.warning("API 요청 한도 초과 (Rate Limit). 잠시 후 다시 시도하세요. (보고서 3.1)")
        else:
            st.error(f"파일 읽기 실패 ({filename}): {str(e)}")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 오류 ({filename}): {str(e)} (보고서 6.1)")
        return {}
    except Exception as e:
        st.error(f"파일 읽기 실패 ({filename}): {str(e)}")
        return {}


def save_json(repo, filename, data, message="Update data"):
    """GitHub에 JSON 파일 저장 (생성 또는 업데이트)"""
    if repo is None:
        st.error("리포지토리 연결이 없습니다.")
        return False
    
    try:
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        st.error(f"JSON 변환 실패: {str(e)} (보고서 6.1)")
        return False
    
    try:
        contents = repo.get_contents(filename)
        # 파일이 존재하면 업데이트
        repo.update_file(contents.path, message, json_str, contents.sha)
        # 저장 후 캐시 비우기 (최신 데이터 반영)
        load_json.clear()
        return True
    except UnknownObjectException:
        # 파일이 없으면 생성
        try:
            repo.create_file(filename, message, json_str)
            # 캐시 무효화
            load_json.clear()
            return True
        except GithubException as e:
            if e.status == 409:
                st.error(f"파일 충돌 발생 ({filename}). 페이지를 새로고침하고 다시 시도하세요. (보고서 3.3)")
            else:
                st.error(f"파일 생성 실패 ({filename}): {str(e)}")
            return False
        except Exception as e:
            st.error(f"파일 생성 실패 ({filename}): {str(e)}")
            return False
    except GithubException as e:
        if e.status == 409:
            st.error(f"파일 충돌 발생 ({filename}). 페이지를 새로고침하고 다시 시도하세요. (보고서 3.3)")
        elif e.status == 403:
            st.warning("API 요청 한도 초과 (Rate Limit). 잠시 후 다시 시도하세요. (보고서 3.1)")
        else:
            st.error(f"파일 저장 실패 ({filename}): {str(e)}")
        return False
    except Exception as e:
        st.error(f"파일 저장 실패 ({filename}): {str(e)} (보고서 3.3)")
        return False
