import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태로 날짜 중앙 관리 (버튼 동작의 핵심)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 3, 12)

# 요일 및 근무조 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(dt):
    """2026.01.01(B조) 기준 3교대 계산"""
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS 스타일 (image_7fbaa4.png 디자인 반영)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 22px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 15px !important; display: block; margin-bottom: 5px; }
    
    /* 타이틀 박스 스타일 (2단 구성) */
    .header-container {
        background-color: #F0F2F6; padding: 12px; border-radius: 10px;
        border: 1px solid #D1D9E6; text-align: center; margin: 10px 0;
    }
    .title-top { font-size: 17px; font-weight: 800; color: #1E3A5F; margin-bottom: 5px; }
    .title-bottom { font-size: 16px; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 10px; }
    
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px !important; background-color: #ffffff; }
    .time-highlight { color: #FF4B4B; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 필터 영역 (image_9bde43.png 기반)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택 위젯 (세션 상태와 동기화)
st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
picked_date = st.date_input("날짜선택", value=st.session_state.target_date, key="date_picker_v64", label_visibility="collapsed")
if picked_date != st.session_state.target_date:
    st.session_state.target_date = picked_date

# 건물 및 유형 선택
st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for i, b in enumerate(ALL_BU) if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_v64_{i}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c_type1, c_type2 = st.columns(2)
with c_type1: show_today = st.checkbox("당일 대관 보기", value=True, key="t_v64")
with c_type2: show_period = st.checkbox("기간 대관 보기", value=True, key="p_v64")

st.write(" ")
search_btn = st.button("🔍 검색하기", use_container_width=True, key="search_v64")

# 3. 데이터 로드 함수
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 화살표 버튼 및 타이틀 박스 (image_7fbaa4.png 스타일 완성)
def move_day(offset):
    st.session_state.target_date += timedelta(days=offset)
    st.rerun()

st.write("---")
# 화살표 배치를 위한 컬럼 구성
col_left, col_mid, col_right = st.columns([0.6, 4, 0.6])

with col_left:
    st.write(" ") # 수직 정렬용
    if st.button("◀", key="prev_v64"):
        move_day(-1)

with col_right:
    st.write(" ") # 수직 정렬용
    if st.button("▶", key="next_v64"):
        move_day(1)

with col_mid:
    curr = st.session_state.target_date
    w_idx = curr.weekday()
    # 요일 색상: 토(청색), 일(적색), 평일(기본)
    t_color = "#0000FF" if w_idx == 5 else ("#FF0000" if w_idx == 6 else "#1E3A5F")
    shift = get_shift_group(curr)
    
    st.markdown(f"""
        <div class="header-container">
            <div class="title-top">📋 성의교정 대관 현황</div>
            <div class="title-bottom" style="color:{t_color};">
                [ {curr.strftime('%Y.%m.%d')}({WEEKDAY_KR[w_idx]}) | {shift} ]
            </div>
        </div>
    """, unsafe_allow_html=True)

# 5. 데이터 렌더링
if search_btn or 'target_date' in st.session_state:
    df = fetch_data(st.session_state.target_date)
    if not df.empty:
        target_wd = str(st.session_state.target_date.weekday() + 1)
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            
            # 당일 대관
            t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            if show_today and not t_ev.empty:
                for _, row in t_ev.iterrows():
                    st.markdown(f"""<div class="event-card">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>📄 {row['eventNm']}</div>""", unsafe_allow_html=True)
            
            # 기간 대관 (요일 필터링)
            p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            if show_period and not p_ev.empty:
                for _, row in p_ev.iterrows():
                    allow = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                    if target_wd in allow:
                        wd_info = f"({', '.join([WEEKDAY_MAP.get(d) for d in allow if d in WEEKDAY_MAP])})"
                        st.markdown(f"""<div class="event-card">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>📄 {row['eventNm']}<br><small style="color:#d63384;">🗓️ {row['startDt']} ~ {row['endDt']} {wd_info}</small></div>""", unsafe_allow_html=True)

st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center>", unsafe_allow_html=True)
