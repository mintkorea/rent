import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [세션 상태 관리]
if 'search_date' not in st.session_state:
    st.session_state.search_date = date(2026, 3, 12)
if 'triggered' not in st.session_state:
    st.session_state.triggered = False

# 요일 및 근무조 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS 스타일 적용 (image_7f4e49.png 구조 반영)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 22px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 15px !important; display: block; margin-bottom: 5px; }
    
    /* 결과 헤더 박스 디자인 */
    .result-header-box {
        background-color: #F0F2F6; padding: 12px; border-radius: 12px;
        border: 1px solid #D1D9E6; text-align: center; margin-bottom: 10px;
    }
    .title-text { font-size: 17px; font-weight: 800; color: #1E3A5F; margin-bottom: 8px; }
    .nav-container { display: flex; align-items: center; justify-content: center; gap: 15px; }
    .date-info-text { font-size: 16px; font-weight: 800; }
    
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px; background-color: #ffffff; }
    .time-highlight { color: #FF4B4B; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 필터 영역 (image_9bde43.png)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
picked_date = st.date_input("날짜선택", value=st.session_state.search_date, key="input_date", label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for i, b in enumerate(ALL_BU) if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{i}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c_t1, c_t2 = st.columns(2)
with c_t1: show_today = st.checkbox("당일 대관 보기", value=True, key="chk_t")
with c_t2: show_period = st.checkbox("기간 대관 보기", value=True, key="chk_p")

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True, key="main_search"):
    st.session_state.search_date = picked_date
    st.session_state.triggered = True

# 3. 데이터 로드 함수
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력 섹션 (타이틀 아래 화살표 배치)
if st.session_state.triggered:
    st.write("---")
    
    curr = st.session_state.search_date
    w_idx = curr.weekday()
    t_color = "#0000FF" if w_idx == 5 else ("#FF0000" if w_idx == 6 else "#1E3A5F")
    shift = get_shift_group(curr)

    # 타이틀 박스 (상단: 텍스트 / 하단: 버튼 3개 나란히)
    st.markdown(f'<div class="result-header-box"><div class="title-text">📋 성의교정 대관 현황</div></div>', unsafe_allow_html=True)
    
    # 화살표와 날짜 정보를 한 줄에 배치
    c_left, c_mid, c_right = st.columns([1, 4, 1])
    
    with c_left:
        if st.button("◀", key="arrow_prev", use_container_width=True):
            st.session_state.search_date -= timedelta(days=1)
            st.rerun()

    with c_mid:
        # 중앙 날짜 정보 표시
        st.markdown(f"""
            <div style="background-color: #F0F2F6; padding: 7px; border-radius: 8px; border: 1px solid #D1D9E6; text-align: center;">
                <span style="color:{t_color}; font-weight:800; font-size:16px;">
                    [ {curr.strftime('%Y.%m.%d')}({WEEKDAY_KR[w_idx]}) | {shift} ]
                </span>
            </div>
        """, unsafe_allow_html=True)

    with c_right:
        if st.button("▶", key="arrow_next", use_container_width=True):
            st.session_state.search_date += timedelta(days=1)
            st.rerun()

    # 데이터 출력 로직
    df = fetch_data(st.session_state.search_date)
    if not df.empty:
        target_wd = str(st.session_state.search_date.weekday() + 1)
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            
            t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            if show_today and not t_ev.empty:
                for _, row in t_ev.iterrows():
                    st.markdown(f"""<div class="event-card">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>📄 {row['eventNm']}</div>""", unsafe_allow_html=True)
            
            p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            if show_period and not p_ev.empty:
                for _, row in p_ev.iterrows():
                    allow = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                    if target_wd in allow:
                        wd_info = f"({', '.join([WEEKDAY_MAP.get(d) for d in allow if d in WEEKDAY_MAP])})"
                        st.markdown(f"""<div class="event-card">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>📄 {row['eventNm']}<br><small style="color:#d63384;">🗓️ {row['startDt']} ~ {row['endDt']} {wd_info}</small></div>""", unsafe_allow_html=True)

    st.markdown("<br><center><a href='#input_date' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center>", unsafe_allow_html=True)
