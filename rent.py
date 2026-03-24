import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# --- 1. 한국 시간대(KST) 자동 감지 및 설정 보강 ---
KST = ZoneInfo("Asia/Seoul")

def get_now_kst():
    """현재 한국의 날짜와 시간을 정확히 반환"""
    return datetime.now(KST)

def today_kst():
    """현재 한국 날짜 반환"""
    return get_now_kst().date()

# 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회(M)", page_icon="🏫", layout="centered")

# 세션 상태 초기화 (최초 실행 시 한국 날짜 강제 주입)
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()

# URL 파라미터 확인 (날짜 이동 로직)
url_params = st.query_params
if "d" in url_params:
    try:
        url_d = datetime.strptime(url_params["d"], "%Y-%m-%d").date()
        st.session_state.target_date = url_d
    except:
        pass

# --- 이하 기존 로직 및 UI 코드 ---
# (요일 변환, 근무조 계산 등 기존 코드와 동일)

def get_work_shift(d):
    # 기준일(anchor) 대비 오늘 날짜 차이로 근무조 계산
    anchor = date(2026, 3, 13) 
    diff = (d - anchor).days
    shifts = [
        {"n": "A조", "bg": "#FF9800"}, 
        {"n": "B조", "bg": "#E91E63"}, 
        {"n": "C조", "bg": "#2196F3"}
    ]
    return shifts[diff % 3]

# ... (CSS 및 HTML 레이아웃 생략) ...

# 실시간 시간 표시 (필요 시 상단에 추가 가능)
now_time = get_now_kst().strftime("%H:%M:%S")
st.sidebar.info(f"현재 한국 시간: {now_time}") # 사이드바에 현재 시간 표시 예시
