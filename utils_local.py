import json
import os
import streamlit as st

# 데이터가 저장될 폴더 (현재 폴더에 'data'라는 폴더를 만들어 관리하면 깔끔함)
DATA_DIR = "data"

# 데이터 폴더가 없으면 생성
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def get_file_path(filename):
    """파일의 전체 경로를 반환합니다."""
    return os.path.join(DATA_DIR, filename)


def load_json(filename):
    """로컬 파일에서 JSON 데이터를 읽어옵니다."""
    file_path = get_file_path(filename)
    
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error(f"JSON 파싱 오류: {filename}")
        return {}
    except Exception as e:
        st.error(f"파일 읽기 오류 ({filename}): {e}")
        return {}


def save_json(filename, data, message=None):
    """로컬 파일에 JSON 데이터를 저장합니다. (message 인자는 호환성을 위해 남겨둠)"""
    file_path = get_file_path(filename)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # 로컬이라 저장 성공 메시지는 너무 자주 뜨면 귀찮으므로 주석 처리하거나 필요 시 사용
        # st.success(f"{filename} 저장 완료!") 
        return True
    except Exception as e:
        st.error(f"파일 저장 오류 ({filename}): {e}")
        return False

