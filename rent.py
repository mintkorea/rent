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

# 2. CSS: 모바일에서 버튼 3개가 무조건 가로 1줄로 붙게 만듬 (핵심)
st.markdown("""
<style>
    /* 1:8:1 컬럼이 모바일에서 아래로 떨어지지 않게 강제 고정 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    /* 버튼 스타일 조정 */
    .stButton > button {
        border: none !important;
        background: none !important;
        font-size: 24px !important;
        color: #1E3A5F !important;
    }
    .date-box {
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# 3. 타이틀 (기존 유지)
st.markdown('### 🏫 성의교정 시설 대관 현황')

# --- 날짜 변경 컨트롤러 (타이틀 아래 배치) ---
c1, c2, c3 = st.columns([1, 6, 1])

with c1:
    if st.button("←", key="prev"):
        st.session_state.target_date -= timedelta(days=1)
        st.rerun()

with c2:
    d = st.session_state.target_date
    w = ['월','화','수','목','금','토','일'][d.weekday()]
    st.markdown(f"""
        <div class="date-box">
            <b style="font-size:16px;">{d.strftime('%Y.%m.%d')}({w})</b>
        </div>
    """, unsafe_allow_html=True)

with c3:
    if st.button("→", key="next"):
        st.session_state.target_date += timedelta(days=1)
        st.rerun()

# 4. 기존 입력창 (이 부분은 건드리지 마세요)
target_date_input = st.date_input("날짜 직접 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date_input

# ... (기존의 건물 체크박스, 검색하기 버튼 로직 유지) ...

# 5. 결과 출력 (기존 카드 디자인 📍, ⏰ 등 그대로 사용)
if st.session_state.search_performed:
    # 사용자님의 기존 get_data 및 카드 렌더링 코드를 이 아래에 그대로 유지하십시오.
    pass
