import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [성공 로직] 클릭하는 만큼 날짜가 계속 바뀌는 쿼리 파라미터 방식
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": 
        st.session_state.target_date -= timedelta(days=1)
    elif params["nav"] == "next": 
        st.session_state.target_date += timedelta(days=1)
    st.session_state.search_performed = True 
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (화살표를 박스 안 날짜 양옆에 고정)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 박스 전체 디자인 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 25px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* [핵심] 화살표와 날짜를 박스 안에서 수평 정렬 */
    .date-nav-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px; /* 화살표와 날짜 사이 간격 */
    }
    /* 성공했던 텍스트 링크형 화살표 디자인 */
    .nav-arrow { 
        font-size: 32px !important; 
        font-weight: bold; 
        color: #1E3A5F !important; 
        text-decoration: none !important;
        padding-bottom: 5px;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부 (간결하게 유지)
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크"] if st.checkbox(b, value=True)]

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력부 (화살표가 박스 안으로 들어온 버전)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [수정된 부분] HTML 구조를 하나로 묶어 화살표를 박스 안으로 완벽 삽입
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-nav-wrapper">
            <a href="./?nav=prev" target="_self" class="nav-arrow">⬅️</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">➡️</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 출력 로직... (이하 생략)
    st.write(f"현재 선택된 날짜: {d}")
