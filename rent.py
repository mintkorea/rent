import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화 (기존 로직 유지)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. 날짜 변경 로직 (버튼 대신 쿼리 파라미터 활용)
query = st.query_params
if "nav" in query:
    if query["nav"] == "p": st.session_state.target_date -= timedelta(days=1)
    if query["nav"] == "n": st.session_state.target_date += timedelta(days=1)
    st.query_params.clear()
    st.rerun()

# 3. CSS (기존 카드 디자인 📍, ⏰ 등은 그대로 유지됨)
st.markdown("""
<style>
    /* 날짜 내비게이션 바 강제 한 줄 고정 */
    .nav-bar {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        gap: 15px !important;
        margin: 20px 0;
    }
    .arrow {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #1E3A5F !important;
        text-decoration: none !important;
        user-select: none;
    }
    .date-display {
        flex: 1;
        max-width: 280px;
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 10px 0;
        text-align: center;
        font-weight: bold;
        color: #1E3A5F;
        font-size: 17px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .sat { color: blue; } .sun { color: red; }
</style>
""", unsafe_allow_html=True)

# --- 상단 타이틀 및 기존 입력 UI 영역 (손대지 않음) ---
st.markdown('### 🏫 성의교정 시설 대관 현황')

# (여기에 기존의 date_input, 건물 체크박스, 검색하기 버튼 코드를 그대로 두세요)

# 4. 결과 출력 시 나타나는 날짜바꾸기 (링크 형태)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [ ← ] [ 2026.03.09(월) ] [ → ]
    st.markdown(f"""
    <div class="nav-bar">
        <a href="/?nav=p" target="_self" class="arrow">←</a>
        <div class="date-display">
            {d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w_str})</span>
        </div>
        <a href="/?nav=n" target="_self" class="arrow">→</a>
    </div>
    """, unsafe_allow_html=True)

    # --- 데이터 로드 및 카드 출력 (📍, ⏰ 등 기존 카드 디자인은 이 아래에 그대로 유지) ---
