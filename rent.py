import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 유지 (날짜 이동 시 초기화 방지)
if 'search_date' not in st.session_state:
    st.session_state.search_date = date(2026, 3, 12)
if 'triggered' not in st.session_state:
    st.session_state.triggered = False

# 요일 및 근무조 계산
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# 2. CSS: 3개 셀 밀착 레이아웃 (버튼과 타이틀 높이 일치)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    [data-testid="stHorizontalBlock"] { gap: 0rem !important; align-items: stretch !important; }
    
    .stButton > button {
        border-radius: 0px !important;
        height: 56px !important;
        width: 100% !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #F8FAFC !important;
        margin: 0 !important;
    }
    
    /* 왼쪽/오른쪽 버튼 모서리 처리 */
    div[data-testid="column"]:nth-child(1) button { border-top-left-radius: 12px !important; border-bottom-left-radius: 12px !important; border-right: none !important; }
    div[data-testid="column"]:nth-child(3) button { border-top-right-radius: 12px !important; border-bottom-right-radius: 12px !important; border-left: none !important; }

    .title-cell {
        background-color: #F1F5F9;
        border-top: 1px solid #CBD5E1;
        border-bottom: 1px solid #CBD5E1;
        height: 56px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    
    .building-header { font-size: 17px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px; background-color: #ffffff; }
    .time-highlight { color: #FF4B4B; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 필터
st.markdown('### 🏫 성의교정 시설 대관 현황')
picked_date = st.date_input("조회 날짜", value=st.session_state.search_date)

ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [bu for bu in ALL_BU if st.checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"]))]

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_date = picked_date
    st.session_state.triggered = True

# 4. 데이터 로드 함수
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (성공했던 요일 필터링 로직)
if st.session_state.triggered:
    st.write("---")
    curr = st.session_state.search_date
    w_idx = curr.weekday()
    target_wd = str(w_idx + 1) # 성공 로직 핵심: 월=1, 일=7
    t_color = "#FF0000" if w_idx == 6 else ("#0000FF" if w_idx == 5 else "#1E3A5F")

    # [3분할 네비게이션 셀]
    c1, c2, c3 = st.columns([1, 6, 1])
    with c1:
        if st.button("◀", key="p_nav"):
            st.session_state.search_date -= timedelta(days=1)
            st.rerun()
    with c2:
        st.markdown(f"""
            <div class="title-cell">
                <div style="font-size:14px; font-weight:800; color:#1E3A5F;">📋 대관 현황</div>
                <div style="font-size:14px; font-weight:700; color:{t_color};">
                    [{curr.strftime('%Y.%m.%d')}({WEEKDAY_KR[w_idx]}) | {get_shift_group(curr)}]
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        if st.button("▶", key="n_nav"):
            st.session_state.search_date += timedelta(days=1)
            st.rerun()

    df = fetch_data(st.session_state.search_date)
    if not df.empty:
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            for _, row in bu_df.iterrows():
                # 성공했던 필터링 로직 적용
                is_today = (row['startDt'] == row['endDt'])
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                
                # 당일 대관이거나 기간 대관 중 해당 요일인 경우만 노출
                if is_today or (target_wd in allow_days):
                    st.markdown(f"""
                        <div class="event-card">
                            <div style="float:right; font-size:12px; color:#666;">[{row.get('statusNm', '')}]</div>
                            📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                            📄 {row['eventNm']}
                        </div>
                    """, unsafe_allow_html=True)
