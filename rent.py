import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [핵심] 날짜 상태 관리 (이게 있어야 클릭할 때마다 누적됩니다)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [기능] 날짜 변경 함수
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (화살표를 박스 안 날짜 옆으로 강제 배치)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 날짜 표시 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 10px; }
    
    /* [성공 포인트] 화살표 버튼 스타일링 (파란 배경 + 흰색 화살표) */
    div.stButton > button {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 20px !important; font-weight: bold !important;
        width: 50px !important; height: 40px !important; padding: 0 !important;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 UI
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 (박스 내부에 버튼식 화살표 배치)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 박스 시작
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # [박스 내부 정렬] 컬럼을 사용하여 화살표-날짜-화살표 배치
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("⬅️", key="prev_btn"):
            change_date(-1)
            st.rerun()
    with col2:
        st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col3:
        if st.button("➡️", key="next_btn"):
            change_date(1)
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 안내 문구
    st.info(f"조회중인 날짜: {d.strftime('%Y-%m-%d')}")
