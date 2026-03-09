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

# 2. CSS 스타일: 모든 간격을 극단적으로 줄임
st.markdown("""
<style>
    /* 전체 배경 및 컨테이너 여백 제거 */
    .block-container { padding: 0.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [핵심] 모든 요소의 기본 줄간격 및 여백 제거 */
    p, div, label, .stCheckbox { 
        margin-bottom: 0px !important; 
        padding-bottom: 0px !important; 
        line-height: 1.1 !important; 
    }
    
    /* 메인 타이틀 크기 및 간격 축소 */
    .main-header { 
        text-align: center; color: #1E3A5F; font-size: 19px !important; 
        font-weight: 800; margin: 5px 0 10px 0 !important; 
    }

    /* 섹션 타이틀 간격 축소 */
    .section-title { 
        font-size: 13px; font-weight: bold; color: #444; 
        margin-top: 8px !important; margin-bottom: 2px !important; 
    }

    /* [중요] 날짜 이동 바: 버튼과 날짜를 강제로 가로 한 줄(Flex) 배치 */
    .nav-bar {
        display: flex; align-items: center; justify-content: center;
        gap: 15px; background-color: #F8FAFF; padding: 4px;
        border-radius: 8px; border: 1px solid #E1E8F0; margin: 10px 0;
    }
    .date-text { font-size: 17px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 버튼 스타일 (작고 컴팩트하게) */
    .stButton > button {
        padding: 2px 10px !important; height: 32px !important;
        min-width: 40px !important; font-size: 16px !important;
    }

    /* 카드 디자인: 줄간격 최소화 */
    .building-header { 
        font-size: 16px !important; font-weight: bold; color: #1E3A5F; 
        border-bottom: 2px solid #1E3A5F; padding-bottom: 1px; margin-top: 12px; 
    }
    
    .event-card { 
        border: 1px solid #E8E8E8; border-left: 4px solid #1E3A5F; 
        padding: 6px 10px; border-radius: 5px; margin-bottom: 4px; 
        background-color: white; line-height: 1.1 !important;
    }
    
    .place-name { font-size: 14px; font-weight: 800; color: #1E3A5F; margin-bottom: 1px; }
    .card-row { font-size: 12.5px; margin-bottom: 1px; display: flex; align-items: center; }
    .time-text { font-weight: bold; color: #E63946; }
    
    .info-sub { 
        font-size: 10px; color: #888; display: flex; 
        justify-content: space-between; margin-top: 3px; 
        border-top: 1px solid #F8F8F8; padding-top: 2px; 
    }

    /* TOP 버튼 위치 조정 */
    .top-btn {
        position: fixed; bottom: 15px; right: 15px; background: #1E3A5F;
        color: white; width: 35px; height: 35px; border-radius: 50%;
        text-align: center; line-height: 35px; font-size: 10px; z-index: 99;
    }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI
st.markdown('<div class="main-header">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 콤팩트한 입력창 레이아웃
st.markdown('<div class="section-title">📅 날짜</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("d", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<div class="section-title">🏢 건물 및 유형 (중복 선택)</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    bu_sh = st.checkbox("성의회관", value=True)
    bu_om = st.checkbox("옴니버스", value=False)
with c2:
    type_today = st.checkbox("당일 대관", value=True)
    type_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 섹션
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [수정] 날짜 이동 바: 버튼이 밖으로 나가지 않게 HTML로 직접 구성
    st.markdown(f"""
    <div class="nav-bar">
        <div id="prev-btn"></div>
        <div class="date-text">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></div>
        <div id="next-btn"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Streamlit 버튼을 위 HTML 위치에 맞추기 위해 컬럼 재사용
    col_nav = st.columns([1, 2, 1])
    with col_nav[0]: 
        if st.button("⬅️", key="btn_prev"): change_date(-1); st.rerun()
    with col_nav[2]: 
        if st.button("➡️", key="btn_next"): change_date(1); st.rerun()

    # 데이터 예시 레이아웃 (실제 데이터 매핑 필요)
    st.markdown('<div class="building-header">🏢 성의회관</div>', unsafe_allow_html=True)
    
    # 카드 예시 (당일)
    st.markdown(f"""
    <div class="event-card">
        <div style="display:flex; justify-content:space-between;">
            <span class="place-name">📍 마리아홀</span>
            <span style="font-size:9px; background:#FFF2E6; color:#FF8C00; padding:1px 4px; border-radius:4px;">예약확정</span>
        </div>
        <div class="card-row"><span class="time-text">⏰ 09:00 ~ 12:00</span></div>
        <div class="card-row">📄 의과대학 특별 강연</div>
        <div class="info-sub"><span>🗓️ {d.strftime("%Y-%m-%d")}</span><span>👥 학사지원팀</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<a href="#" class="top-btn">TOP</a>', unsafe_allow_html=True)
