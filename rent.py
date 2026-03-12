import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 시간대
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- 세션 상태 관리 (버튼 클릭 즉시 반영용) ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()

# URL 파라미터가 있으면 세션에 우선 반영
query_params = st.query_params
if "d" in query_params:
    try:
        param_date = datetime.strptime(query_params["d"], "%Y-%m-%d").date()
        if st.session_state.target_date != param_date:
            st.session_state.target_date = param_date
    except: pass

# --- 근무조 계산 (2026-03-13 금요일 = A조 기준) ---
def get_work_shift(target_date):
    anchor_date = date(2026, 3, 13)
    days_diff = (target_date - anchor_date).days
    shift_idx = days_diff % 3
    
    shifts = [
        {"name": "A조", "bg": "#FF9800", "color": "white"}, # 주황
        {"name": "B조", "bg": "#E91E63", "color": "white"}, # 빨강
        {"name": "C조", "bg": "#2196F3", "color": "white"}  # 파랑
    ]
    return shifts[shift_idx]

# 2. CSS 스타일 (사용자 원본 디자인 100% 복구)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .stCheckbox { margin-top: -10px !important; margin-bottom: -5px !important; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none; line-height: 1.2 !important;
    }
    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 4px; }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 25px !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important; font-weight: bold !important; 
        border-right: 1px solid #F0F0F0 !important; font-size: 13px !important;
    }
    .nav-item:last-child { border-right: none !important; }
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 15px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; background-color: #ffffff; line-height: 1.4 !important; }
    .status-badge { display: inline-block; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 8px; display: flex; justify-content: space-between; border-top: 1px solid #f0f0f0; padding-top: 6px; }
    .open-card { border: 2px dashed #2E5077; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #F8FAFF; }
    .open-bu-title { font-weight: 800; color: #2E5077; font-size: 19px !important; margin-bottom: 10px; border-bottom: 2px solid #D1D9E6; }
    .open-room-name { font-weight: bold; color: #333; font-size: 17px !important; margin-bottom: 3px; }
    .open-room-time { font-size: 16px !important; color: #FF4B4B; font-weight: bold; margin-bottom: 5px; }
    .open-room-note { font-size: 14px !important; color: #444; line-height: 1.4; background: #eee; padding: 5px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>
