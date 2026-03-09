import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 세션 초기화 (기존 로직 유지)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS: 타이틀 박스(테두리) 안에 화살표와 날짜를 강제로 가둠
st.markdown("""
<style>
    /* 박스 테두리 설정 */
    .integrated-container {
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        background-color: white;
        padding: 5px;
        margin: 10px 0;
    }
    /* 박스 내부 가로 정렬 */
    [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }
    /* 화살표 버튼 투명화 및 날짜와 밀착 */
    .stButton > button {
        border: none !important;
        background: transparent !important;
        font-size: 20px !important;
        color: #1E3A5F !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 30px !important;
    }
    .date-text-wrapper {
        text-align: center;
        width: 100%;
    }
    .m-title { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; }
    .s-title { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: blue; } .sun { color: red; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 영역 (기존 코드 그대로 유지)
st.markdown('### 🏫 성의교정 시설 대관 현황')

# (이 자리에 기존의 건물 선택 체크박스들 배치)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력 (날짜와 화살표가 박스 하나에 들어간 형태)
if st.session_state.search_performed:
    # 박스 테두리 시작
    st.markdown('<div class="integrated-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col1:
        if st.button("←", key="nav_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun() # 링크 방식 대신 rerun을 써야 화면이 안 사라집니다.
            
    with col2:
        d = st.session_state.target_date
        w = ['월','화','수','목','금','토','일'][d.weekday()]
        w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")
        st.markdown(f"""
        <div class="date-text-wrapper">
            <span class="m-title">성의교정 대관 현황</span>
            <span class="s-title">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w})</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        if st.button("→", key="nav_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True) # 박스 테두리 끝

    # --- 아래 데이터 출력(카드 디자인 등)은 기존 소스 그대로 사용하세요 ---
