

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 상태 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [핵심] 날짜 변경 함수 (이게 있어야 클릭할 때마다 누적됩니다)
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (스크린샷 17:45 버전의 박스 정렬)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 25px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* 파란색 화살표 버튼 스타일 (성공 버전) */
    div.stButton > button {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 20px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 55px !important; height: 40px !important;
    }

    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부
st.markdown('<div style="font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom:10px;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 입력 (세션 동기화)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 (성공했던 박스 내 버튼 배치)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [성공 구조] 박스 시작
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # 버튼-날짜-버튼 수평 정렬
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("⬅️", key="p_btn"):
            change_date(-1)
            st.rerun()
    with col2:
        st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col3:
        if st.button("➡️", key="n_btn"):
            change_date(1)
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 안내 문구 (스크린샷 17:45 스타일)
    st.info(f"현재 {d.strftime('%Y-%m-%d')} 대관 내역을 조회 중입니다.")
