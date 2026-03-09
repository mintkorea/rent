import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 초기화
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# CSS 스타일: 타이틀 확대 및 화살표 밀착 배치
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 1. 메인 타이틀 글자 크기 확대 */
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 10px !important; }
    
    /* 2. 결과 박스 내부 레이아웃 (메모 반영) */
    .integrated-date-container {
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        background-color: #F8FAFF;
        padding: 15px 5px;
        margin-bottom: 20px;
        text-align: center;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    
    /* 화살표와 날짜를 한 줄로 밀착 */
    .date-row { 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 10px; /* 화살표와 날짜 사이 간격 좁힘 */
    }
    .res-sub-title { font-size: 19px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 스트림릿 버튼을 화살표처럼 보이게 투명 스타일링 */
    div.stButton > button[key^="nav_"] {
        border: none !important;
        background: transparent !important;
        font-size: 24px !important;
        color: #1E3A5F !important;
        padding: 0px !important;
        width: 30px !important;
        height: 30px !important;
    }
    
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 날짜 직접 선택 및 건물 선택 UI
target_date_input = st.date_input("날짜 직접 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date_input

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}")]

st.write(" ")
st.markdown('<div id="result-point"></div>', unsafe_allow_html=True) # 스크롤 포인트
if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 3. 결과 출력 부분
if st.session_state.search_performed:
    # 검색 시 결과 위치로 스크롤
    components.html("<script>window.parent.document.getElementById('result-point').scrollIntoView({behavior:'smooth'});</script>", height=0)

    # 데이터 로드 로직 (기존 함수 활용)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_cls = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # --- [수정 핵심] 메모와 동일한 통합 박스 구조 ---
    with st.container():
        # HTML로 박스 시작
        st.markdown(f'<div class="integrated-date-container"><span class="res-main-title">성의교정 대관 현황</span><div class="date-row">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            if st.button("◀", key="nav_prev"):
                st.session_state.target_date -= timedelta(days=1)
                st.rerun()
        with col2:
            st.markdown(f'<span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_cls}">({w_str})</span></span>', unsafe_allow_html=True)
        with col3:
            if st.button("▶", key="nav_next"):
                st.session_state.target_date += timedelta(days=1)
                st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True) # 박스 닫기

    # --- 데이터 리스트 출력 (기존 로직 유지) ---
    # (여기 아래에 기존의 for bu in selected_bu: 루프를 그대로 넣으시면 됩니다)
    st.info(f"{d.strftime('%Y-%m-%d')} 대관 정보를 불러오는 중...")
