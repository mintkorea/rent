import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 유지 (기존 유지)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS: 기존 카드 디자인은 건드리지 않고, 날짜바 영역만 가로로 고정
st.markdown("""
<style>
    /* 날짜 이동 바: 모바일에서도 무조건 가로 한 줄 */
    .date-nav-bar {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        gap: 10px !important;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    /* 날짜가 표시되는 중앙 박스 */
    .date-text-box {
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
        font-size: 16px;
        color: #1E3A5F;
        text-align: center;
        min-width: 160px;
    }
    .sat { color: #0000FF !important; } 
    .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 기존 입력 UI (손대지 않음)
st.markdown('### 🏫 성의교정 시설 대관 현황')
target_date = st.date_input("날짜 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}")]

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력 및 날짜바꾸기 (← 날짜 → 형태)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # --- 요청하신 날짜바꾸기 UI ---
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_l:
        if st.button("←", key="prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with col_m:
        st.markdown(f"""
            <div style="text-align:center; padding:7px; border:1px solid #d1d9e6; border-radius:8px; background:#fff;">
                <span style="font-weight:bold;">{d.strftime('%Y.%m.%d')}.<span class="{w_class}">({w_str})</span></span>
            </div>
        """, unsafe_allow_html=True)
    with col_r:
        if st.button("→", key="next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # --- 데이터 로직 및 카드 출력 (기존 디자인 그대로 사용) ---
    # 사용자님의 기존 카드 렌더링 코드를 이 아래에 그대로 유지하시면 됩니다.
