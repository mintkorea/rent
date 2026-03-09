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

# 2. CSS: 올려주신 이미지와 똑같은 가로 캡슐형 디자인
st.markdown("""
<style>
    /* 전체를 감싸는 컨테이너: 절대 줄바꿈 금지 */
    .nav-wrapper {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 20px 0;
        gap: 5px !important;
    }
    
    /* 화살표 링크 버튼 스타일 (이미지 느낌) */
    .nav-arrow {
        background: #fdfdfd;
        border: 2px solid #e0e0e0;
        border-radius: 25px; /* 둥근 캡슐형 */
        width: 60px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: bold;
        color: #888;
        text-decoration: none !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* 중앙 날짜 박스 스타일 (이미지 느낌) */
    .nav-date-box {
        flex: 1;
        max-width: 300px;
        background: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 5px 15px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .m-title { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; }
    .s-title { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }

    /* 기존 카드 디자인 보존용 */
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)

# 3. 날짜 변경 로직 (링크 클릭 시 작동)
params = st.query_params
if "action" in params:
    if params["action"] == "prev":
        st.session_state.target_date -= timedelta(days=1)
    elif params["action"] == "next":
        st.session_state.target_date += timedelta(days=1)
    st.query_params.clear()
    st.rerun()

# 4. 입력 UI (건물 선택 등 기존 코드 그대로 두세요)
st.markdown('### 🏫 성의교정 시설 대관 현황')
# (기존의 date_input, checkbox, 검색 버튼 코드를 여기에 유지)

# 5. 결과 출력 (이미지 형태의 내비게이션 바)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # HTML로 이미지와 동일한 레이아웃 구현
    st.markdown(f"""
    <div class="nav-wrapper">
        <a href="/?action=prev" target="_self" class="nav-arrow">＜</a>
        <div class="nav-date-box">
            <span class="m-title">성의교정 대관 현황</span>
            <span class="s-title">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w_str})</span></span>
        </div>
        <a href="/?action=next" target="_self" class="nav-arrow">＞</a>
    </div>
    """, unsafe_allow_html=True)

    # --- 데이터 출력 로직 (📍, ⏰ 빨간색 시간 등 기존 소스 그대로 사용) ---
