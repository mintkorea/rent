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

# 2. CSS: 타이틀 박스 안에 버튼이 들어간 것처럼 보이게 디자인
st.markdown("""
<style>
    /* 박스 내부 버튼들이 한 줄로 고정되도록 강제 */
    [data-testid="stHorizontalBlock"] {
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 5px;
        align-items: center !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }
    /* 화살표 버튼 투명화 및 크기 조절 */
    .stButton > button {
        border: none !important;
        background-color: transparent !important;
        font-size: 24px !important;
        color: #1E3A5F !important;
        padding: 0 !important;
        width: 40px !important;
    }
    .main-txt { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; line-height: 1.2; }
    .sub-txt { font-size: 14px; font-weight: 700; color: #333; line-height: 1.2; }
    .sat { color: blue; } .sun { color: red; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 입력 UI (기존 소스 유지)
st.markdown('### 🏫 성의교정 시설 대관 현황')

# (여기에 기존의 건물 선택 체크박스들 유지...)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력 (타이틀 박스 안에 버튼 통합)
if st.session_state.search_performed:
    # 1:8:1 비율로 컬럼을 만들고 CSS로 한 박스처럼 묶음
    c1, c2, c3 = st.columns([1, 8, 1])
    
    with c1:
        if st.button("←", key="nav_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun() # 화면 증발 없이 데이터 유지하며 날짜만 변경
            
    with c2:
        d = st.session_state.target_date
        w = ['월','화','수','목','금','토','일'][d.weekday()]
        w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")
        st.markdown(f"""
        <div style="text-align: center;">
            <span class="main-txt">성의교정 대관 현황</span>
            <span class="sub-txt">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w})</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        if st.button("→", key="nav_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # --- 데이터 로드 및 카드 출력 (📍, ⏰ 등 기존 카드 디자인 그대로 유지) ---
    # 사용자님의 기존 get_data 및 결과 출력 루프 코드를 여기에 붙여넣으세요.
