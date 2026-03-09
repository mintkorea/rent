import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화 (기존 유지)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 날짜 변경 로직 (쿼리 파라미터 기반)
query_params = st.query_params
if "nav" in query_params:
    nav_val = query_params["nav"]
    if nav_val == "prev":
        st.session_state.target_date -= timedelta(days=1)
    elif nav_val == "next":
        st.session_state.target_date += timedelta(days=1)
    st.query_params.clear()
    st.rerun()

# 2. CSS: 화살표 문자와 타이틀 박스를 무조건 가로로 배치
st.markdown("""
<style>
    .nav-container {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 15px !important;
        width: 100% !important;
        margin: 15px 0;
    }
    /* 화살표 문자 링크 스타일 */
    .arrow-link {
        font-size: 30px !important;
        font-weight: bold !important;
        color: #1E3A5F !important;
        text-decoration: none !important;
        padding: 0 10px;
        user-select: none;
    }
    /* 중앙 사각 타이틀 박스 */
    .date-display-box {
        flex: 1;
        max-width: 250px;
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 10px 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .main-txt { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; }
    .sub-txt { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI (기존 소스 그대로 유지)
st.markdown('### 🏫 성의교정 시설 대관 현황')
# ... (생략: 기존의 date_input, checkbox, 검색 버튼 로직) ...

# 4. 결과 출력 영역 (화살표 문자 링크 형태)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # HTML 링크를 이용한 내비게이션 (← 날짜박스 →)
    st.markdown(f"""
    <div class="nav-container">
        <a href="/?nav=prev" target="_self" class="arrow-link">←</a>
        <div class="date-display-box">
            <span class="main-txt">성의교정 대관 현황</span>
            <span class="sub-txt">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w_str})</span></span>
        </div>
        <a href="/?nav=next" target="_self" class="arrow-link">→</a>
    </div>
    """, unsafe_allow_html=True)

    # --- 데이터 출력 로직 (기존 카드 디자인 손대지 말고 그대로 유지) ---
