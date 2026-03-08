import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 및 디자인 (색상 강조 추가)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 요일 및 근무조 관련 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']

def get_shift_group(target_date):
    """2026년 1월 1일(B조) 기준 3교대 순환 계산"""
    base_date = date(2026, 1, 1)
    diff_days = (target_date - base_date).days
    # 2026-01-01이 B조(인덱스 1)이므로 (diff + 1) % 3
    shift_idx = (diff_days + 1) % 3
    return SHIFT_TYPES[shift_idx]

def get_header_style(target_date):
    """요일별 헤더 색상 및 근무조 텍스트 생성"""
    w_idx = target_date.weekday() # 0:월 ~ 6:일
    w_str = WEEKDAY_KR[w_idx]
    shift_group = get_shift_group(target_date)
    
    # 색상 결정 (토: 청색, 일: 적색, 평일: 검정)
    color = "#1E3A5F" # 기본 어두운 청색
    if w_idx == 5: color = "#0000FF" # 토요일 청색
    elif w_idx == 6: color = "#FF0000" # 일요일 적색
    
    date_str = target_date.strftime("%Y.%m.%d")
    return f'<span style="color:{color};">📋 성의교정 대관 현황 [ {date_str}({w_str}) | {shift_group} ]</span>'

# CSS 스타일 유지
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 17px !important; font-weight: 800; color: #2E5077; margin-top: 12px !important; margin-bottom: 5px !important; display: block; }
    .date-display { 
        text-align: center; font-size: 18px; font-weight: 800; 
        background-color: #F0F2F6; padding: 12px; border-radius: 10px; 
        margin: 20px 0; border: 1px solid #D1D9E6; 
    }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #444; margin: 18px 0 10px 0; padding-left: 8px; border-left: 5px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 12px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .status-badge { float: right; padding: 2px 10px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .place-time { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; margin-left: 8px; font-weight: 800; }
    .event-name { font-size: 14px; margin-top: 8px; color: #333; font-weight: 600; }
    .info-row { font-size: 12px; color: #666; margin-top: 8px; display: flex; align-items: center; gap: 8px; }
    .weekday-text { color: #2E5077; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜선택", value=date(2026, 3, 12), label_visibility="collapsed", key="v58_date")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v58_bu_{i}"):
            selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관 보기", value=True, key="v58_show_t")
with c2: show_period = st.checkbox("기간 대관 보기", value=True, key="v58_show_p")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True, key="v58_search_btn")

# 3. 데이터 로드 (생략)
@st.cache_data(ttl=300)
def fetch_data(selected_date):
    url = "
