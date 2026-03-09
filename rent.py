import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화 (기존 코드 유지)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS: 버튼과 날짜가 무조건 한 줄에 나오도록 강제 (기존 카드 디자인은 보존)
st.markdown("""
<style>
    .date-nav-wrapper {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 10px 0 20px 0;
        gap: 15px !important;
    }
    .date-btn {
        background-color: #f8f9fa;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 8px 15px;
        font-size: 20px;
        cursor: pointer;
        color: #1E3A5F;
        text-decoration: none !important;
        line-height: 1;
    }
    .date-display-box {
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 10px 20px;
        text-align: center;
        min-width: 180px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .main-txt { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; }
    .sub-txt { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI (기존 소스 그대로)
st.markdown('### 🏫 성의교정 시설 대관 현황')
target_date = st.date_input("날짜 직접 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date

# ... 건물 선택 체크박스들 로직 (기존 소스 유지) ...

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력 영역 (요청하신 날짜바꾸기 버튼 + 타이틀)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # 날짜 이동 로직 (쿼리 파라미터나 세션을 직접 건드리는 대신 버튼으로 구현)
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("←", key="nav_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with col2:
        st.markdown(f"""
        <div class="date-display-box">
            <span class="main-txt">성의교정 대관 현황</span>
            <span class="sub-txt">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w_str})</span></span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("→", key="nav_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # --- 데이터 출력 로직 (📍, ⏰ 빨간색 시간 등 기존 카드 디자인 그대로 아래에 유지) ---
