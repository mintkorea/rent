import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 유지
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

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

# 2. CSS 스타일 (성공했던 3개 셀 밀착 디자인)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 15px !important; font-weight: 800; color: #2E5077; margin-top: 15px !important; display: block; margin-bottom: 5px; }

    /* 3개 셀 간격 제거 */
    div[data-testid="stHorizontalBlock"] { gap: 0rem !important; align-items: stretch !important; }
    
    .stButton > button {
        border-radius: 0px !important;
        height: 56px !important;
        width: 100% !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #F8FAFC !important;
        color: #1E3A5F !important;
        font-weight: bold !important;
        margin: 0 !important;
    }
    
    div[data-testid="column"]:nth-child(1) button { border-top-left-radius: 12px !important; border-bottom-left-radius: 12px !important; border-right: none !important; }
    div[data-testid="column"]:nth-child(3) button { border-top-right-radius: 12px !important; border-bottom-right-radius: 12px !important; border-left: none !important; }

    .title-center-unit {
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

# 3. 입력 필터 영역
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
p_date = st.date_input("date", value=st.session_state.search_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
c1, c2 = st.columns(2)
with c1:
    bu_0 = st.checkbox(ALL_BU[0], value=True)
    bu_2 = st.checkbox(ALL_BU[2], value=False)
    bu_4 = st.checkbox(ALL_BU[4], value=False)
    bu_6 = st.checkbox(ALL_BU[6], value=False)
with c2:
    bu_1 = st.checkbox(ALL_BU[1], value=True)
    bu_3 = st.checkbox(ALL_BU[3], value=False)
    bu_5 = st.checkbox(ALL_BU[5], value=False)

selected_bu = [ALL_BU[i] for i, v in enumerate([bu_0, bu_1, bu_2, bu_3, bu_4, bu_5, bu_6]) if v]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
ct1, ct2 = st.columns(2)
with ct1: show_today = st.checkbox("당일 대관 보기", value=True)
with ct2: show_period = st.checkbox("기간 대관 보기", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_date = p_date
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

# 5. 결과 출력 (성공했던 요일 필터 로직 적용)
if st.session_state.triggered:
    st.write("---")
    curr = st.session_state.search_date
    w_idx = curr.weekday()
    target_wd = str(w_idx + 1) # API 요일 기준 (월=1, 일=7)
    t_color = "#FF0000" if w_idx == 6 else ("#0000FF" if w_idx == 5 else "#1E3A5F")
    
    res_l, res_c, res_r = st.columns([1, 6, 1])
    with res_l:
        if st.button("◀", key="nav_prev"):
            st.session_state.search_date -= timedelta(days=1)
            st.rerun()
    with res_c:
        st.markdown(f'<div class="title-center-unit"><div style="font-size: 14px; font-weight: 800; color: #1E3A5F;">📋 대관 현황</div><div style="font-size: 14px; font-weight: 700; color: {t_color};">[{curr.strftime("%Y.%m.%d")}({WEEKDAY_KR[w_idx]}) | {get_shift_group(curr)}]</div></div>', unsafe_allow_html=True)
    with res_r:
        if st.button("▶", key="nav_next"):
            st.session_state.search_date += timedelta(days=1)
            st.rerun()

    df = fetch_data(st.session_state.search_date)
    if not df.empty:
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            for _, row in bu_df.iterrows():
                is_today = (row['startDt'] == row['endDt'])
                # 성공했던 요일 필터링 로직: allowDay에 현재 요일이 포함되어 있는지 확인
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                status = row.get('statusNm', '')

                if (is_today and show_today) or (not is_today and show_period and target_wd in allow_days):
                    p_info = f"<br><small style='color:#d63384;'>🗓️ 기간: {row['startDt']}~{row['endDt']} ({', '.join([WEEKDAY_MAP.get(d) for d in allow_days if d in WEEKDAY_MAP])})</small>" if not is_today else ""
                    st.markdown(f"""
                        <div class="event-card">
                            <div style="float:right; font-size:12px; color:#666; font-weight:bold;">[{status}]</div>
                            📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                            📄 {row['eventNm']} {p_info}
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")
