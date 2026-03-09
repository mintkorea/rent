import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정 및 세션 유지 (검색 결과 증발 방지 핵심)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 날짜 이동 로직 (링크 클릭 시 화면 증발 없이 날짜만 변경)
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": st.session_state.target_date -= timedelta(days=1)
    if params["nav"] == "next": st.session_state.target_date += timedelta(days=1)
    st.session_state.search_performed = True # 날짜 바꿔도 결과창 유지
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (메모 그림처럼 글자 키우고 화살표 밀착)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    
    /* 메모 그림 사각형 박스 구현 */
    .integrated-date-box {
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        background-color: #F8FAFF;
        padding: 20px 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* 타이틀 글자 키움 */
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* 화살표와 날짜를 한 줄로 바짝 밀착 */
    .date-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px; /* 화살표와 날짜 사이 간격 */
    }
    .nav-link {
        font-size: 30px !important; /* 화살표 크기 확대 */
        font-weight: bold;
        color: #1E3A5F !important;
        text-decoration: none !important;
        line-height: 1;
    }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: blue; } .sun { color: red; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI (기존 소스 유지)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
target_date_input = st.date_input("날짜 직접 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date_input

# (건물 선택 체크박스 등 기존 로직 생략 없이 그대로 사용하세요)
if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력 (메모 그림 완벽 재현 부분)
if st.session_state.search_performed:
    # 검색 시 결과 위치로 자동 스크롤
    st.markdown('<div id="result-scroll"></div>', unsafe_allow_html=True)
    components.html("<script>window.parent.document.getElementById('result-scroll').scrollIntoView({behavior:'smooth'});</script>", height=0)

    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [핵심] 메모 그림 그대로: 박스 하나에 모든 게 한 줄로 들어감
    st.markdown(f"""
    <div class="integrated-date-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-row">
            <a href="./?nav=prev" target="_self" class="nav-link">←</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_cls}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-link">→</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 이 아래에 기존의 데이터 파싱 및 카드 출력(📍, ⏰ 등) 소스를 붙여넣으세요.
