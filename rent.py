import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [핵심] 클릭수만큼 날짜가 변경되는 원본 로직 (절대 수정 금지)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": 
        st.session_state.target_date -= timedelta(days=1)
    elif params["nav"] == "next": 
        st.session_state.target_date += timedelta(days=1)
    st.session_state.search_performed = True 
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (화살표를 박스 안으로 완벽하게 정렬)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    
    /* 날짜 표시 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 25px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* [정렬 핵심] 화살표와 날짜를 박스 안에서 한 줄로 */
    .date-nav-row {
        display: flex; align-items: center; justify-content: center; gap: 20px;
    }
    .nav-arrow { 
        font-size: 32px !important; font-weight: bold; color: #1E3A5F !important; 
        text-decoration: none !important; 
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 화면 (생략 가능하나 구조 유지를 위해 유지)
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 (성공했던 박스 구조)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [여기가 핵심] 화살표(nav=prev/next)를 박스 안 날짜 양옆에 배치
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-nav-row">
            <a href="./?nav=prev" target="_self" class="nav-arrow">⬅️</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">➡️</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info(f"조회 날짜: {d.strftime('%Y-%m-%d')}")
