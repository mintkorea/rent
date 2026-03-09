import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [핵심] 날짜 상태 유지용 세션
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [성공 로직] 클릭 시마다 URL 파라미터를 통해 날짜를 무한 누적 변경
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": 
        st.session_state.target_date -= timedelta(days=1)
    elif params["nav"] == "next": 
        st.session_state.target_date += timedelta(days=1)
    st.session_state.search_performed = True 
    st.query_params.clear() # 처리 후 파라미터 삭제
    st.rerun() # 즉시 반영

# 2. CSS 스타일 (화살표를 박스 안 날짜 양옆에 고정)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 박스 전체 디자인 (스크린샷 기반) */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 25px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* [박스 내부 정렬] 화살표와 날짜를 수평으로 배치 */
    .date-nav-wrapper {
        display: flex; align-items: center; justify-content: center; gap: 20px;
    }
    /* 스크린샷의 텍스트 링크형 화살표 스타일 */
    .nav-arrow { 
        font-size: 32px !important; font-weight: bold; color: #1E3A5F !important; 
        text-decoration: none !important; cursor: pointer;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 입력 UI
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 날짜 선택기도 세션과 동기화
st.session_state.target_date = st.date_input("날짜 선택", value=st.session_state.target_date, label_visibility="collapsed")

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 (성공한 박스 내 화살표 정렬 구조)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [HTML] 화살표를 박스 내부에 정확히 위치시킴
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-nav-wrapper">
            <a href="./?nav=prev" target="_self" class="nav-arrow">⬅️</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">➡️</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info(f"현재 {d.strftime('%Y-%m-%d')} 대관 내역을 조회 중입니다.")
    # 이 아래에 카드 출력 로직을 붙이면 됩니다.
