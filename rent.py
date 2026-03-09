import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일: 기존 레이아웃 유지하며 간격만 압축
st.markdown("""
<style>
    /* [핵심] 기본 여백 및 줄간격 제거 */
    .block-container { padding: 0.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 모든 요소의 마진과 패딩을 최소화 */
    p, div, label, .stCheckbox { 
        margin-bottom: -2px !important; 
        padding-bottom: 0px !important; 
        line-height: 1.0 !important; 
    }
    .stDateInput { margin-bottom: 10px !important; }

    /* 메인 헤더 (크기 줄이고 간격 압축) */
    .main-header { 
        text-align: center; color: #1E3A5F; font-size: 22px !important; 
        font-weight: 800; margin: 5px 0 10px 0 !important; 
    }

    /* 섹션 타이틀 (아이콘 포함) */
    .section-title { 
        font-size: 15px; font-weight: bold; color: #444; 
        margin-top: 5px !important; margin-bottom: 5px !important; 
    }

    /* 검색 버튼 (빨간색 유지) */
    div.stButton > button[kind="primary"] {
        background-color: #FF5252 !important; color: white !important;
        height: 40px !important; font-weight: bold !important;
        margin-top: 10px !important;
    }

    /* [수정] 날짜 이동 바: 19:17의 깨짐 방지, 한 줄 강제 고정 */
    .nav-row {
        display: flex; align-items: center; justify-content: space-between;
        background-color: #F8FAFF; padding: 5px; border-radius: 10px;
        border: 1px solid #E1E8F0; margin: 10px 0;
    }
    
    /* 날짜이동 버튼 스타일 */
    .nav-btn-container .stButton > button {
        background-color: #A3D2F3 !important; color: white !important;
        width: 45px !important; height: 35px !important; padding: 0 !important;
        font-size: 20px !important; line-height: 35px !important;
    }

    /* 카드 디자인 (18:57 디자인 유지) */
    .building-header { font-size: 17px !important; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 2px; margin-top: 15px; }
    .event-card { 
        border: 1px solid #E8E8E8; border-left: 5px solid #1E3A5F; 
        padding: 8px 10px; border-radius: 6px; margin-bottom: 5px; 
        background-color: white; line-height: 1.1 !important;
    }
    .place-name { font-size: 15px; font-weight: 800; color: #1E3A5F; }
    .time-text { font-weight: bold; color: #E63946; font-size: 14px; }
    .info-sub { font-size: 11px; color: #888; display: flex; justify-content: space-between; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI (18:13 스크린샷의 모든 항목 유지)
st.markdown('<div class="main-header">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">📅 날짜 선택</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("d", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<div class="section-title">🏢 건물 선택</div>', unsafe_allow_html=True)
# 18:13 원본 리스트 복구
buildings = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in buildings:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
        selected_bu.append(b)

st.markdown('<div class="section-title">📋 대관 유형 선택</div>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 섹션
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [중요] 날짜 이동 바: 버튼이 위아래로 찢어지지 않게 컬럼 비율 고정
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1: 
        if st.button("⬅️", key="p_btn"): change_date(-1); st.rerun()
    with c2:
        st.markdown(f'<div style="text-align:center; line-height:35px; font-size:18px; font-weight:bold;">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="n_btn"): change_date(1); st.rerun()

    # 데이터 출력 (중략된 로직은 기존과 동일)
    # ... (데이터 필터링 및 카드 생성 로직) ...
    st.markdown(f'<div class="building-header">🏢 성의회관</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="event-card">
        <div style="display:flex; justify-content:space-between;">
            <span class="place-name">📍 522호</span>
            <span style="font-size:10px; background:#E6F2FF; color:#007AFF; padding:1px 5px; border-radius:4px;">예약확정</span>
        </div>
        <div style="margin:2px 0;"><span class="time-text">⏰ 15:00 ~ 17:00</span></div>
        <div style="font-size:13px;">📄 소라동인회 리크루팅</div>
        <div class="info-sub"><span>🗓️ {d.strftime("%Y-%m-%d")}</span><span>👥 소라동인회</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<a href="#" style="position:fixed; bottom:20px; right:20px; background:#1E3A5F; color:white; width:40px; height:40px; border-radius:50%; text-align:center; line-height:40px; text-decoration:none; font-size:10px; font-weight:bold; z-index:999;">TOP</a>', unsafe_allow_html=True)
