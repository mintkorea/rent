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

# [기능] 날짜 변경 함수
def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (사용자님의 원본 디자인 절대 유지)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    
    /* 화살표 버튼 스타일 (박스 내부용) */
    div.stButton > button {
        background: none !important; border: 1px solid #D1D9E6 !important;
        border-radius: 8px !important; padding: 5px 10px !important;
    }

    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }
    
    /* 카드 디자인 복구 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 15px 0 8px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; position: relative; }
    .status-badge { position: absolute; right: 12px; top: 12px; font-size: 12px; font-weight: bold; padding: 2px 8px; border-radius: 10px; background: #eee; }
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 5px; }
    .event-name { font-size: 14px; margin-top: 5px; color: #333; }
    .period-info { font-size: 12px; color: #666; margin-top: 8px; border-top: 1px solid #eee; padding-top: 5px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 화면
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
selected_bu = []
for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (기본 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 화면 (화살표를 박스 안에 가두고 기능 연결)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 타이틀 박스 시작
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("⬅️", key="go_prev"): move_date(-1); st.rerun()
    with col2:
        st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col3:
        if st.button("➡️", key="go_next"): move_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 필터링 로직 및 카드 출력
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)] if not df_raw.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div style="color:#888; padding:10px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            # 당일 대관 출력
            if show_today:
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not today_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        st.markdown(f'<div class="event-card"><span class="status-badge">{row["status"]}</span><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div></div>', unsafe_allow_html=True)
            
            # 기간 대관 출력
            if show_period:
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                if not period_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in period_ev.iterrows():
                        st.markdown(f'<div class="event-card"><span class="status-badge">{row["status"]}</span><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div><div class="period-info">🗓️ {row["startDt"]} ~ {row["endDt"]}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
