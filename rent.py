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

# 2. CSS: 모바일에서도 무조건 한 줄로 나오게 강제 설정
st.markdown("""
<style>
    /* 화살표와 타이틀 박스를 감싸는 컨테이너 고정 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    
    /* 화살표 버튼 크기 및 스타일 */
    .stButton > button {
        width: 100% !important;
        height: 50px !important;
        padding: 0 !important;
        font-size: 20px !important;
        border-radius: 8px !important;
    }

    /* 중앙 날짜 박스 스타일 */
    .date-display-box {
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 8px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 50px;
    }
    .main-txt { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; line-height: 1.2; }
    .sub-txt { font-size: 14px; font-weight: 700; color: #333; line-height: 1.2; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 입력 UI (기존 소스 유지)
st.markdown('### 🏫 성의교정 시설 대관 현황')
target_date = st.date_input("날짜 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date

# (여기에 기존의 건물 선택 체크박스 코드를 그대로 두세요)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력 및 날짜 이동 컨트롤러
if st.session_state.search_performed:
    # 1:8:1 비율로 컬럼 생성
    c1, c2, c3 = st.columns([1, 8, 1])
    
    with c1:
        if st.button("◀", key="btn_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
            
    with c2:
        d = st.session_state.target_date
        w_list = ['월','화','수','목','금','토','일']
        w_str = w_list[d.weekday()]
        w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")
        st.markdown(f"""
        <div class="date-display-box">
            <span class="main-txt">성의교정 대관 현황</span>
            <span class="sub-txt">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w_str})</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        if st.button("▶", key="btn_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # --- 데이터 로드 및 카드 출력 (기존 디자인 그대로 유지) ---
    # (여기에 기존의 get_data 함수와 건물별 루프/카드 출력 코드를 붙여넣으세요)
