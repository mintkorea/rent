import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [세션 상태 관리] 날짜 변경 시 상단 튕김 방지 및 트리거 관리
if 'search_date' not in st.session_state:
    st.session_state.search_date = date(2026, 3, 12)
if 'triggered' not in st.session_state:
    st.session_state.triggered = False

# 요일 및 근무조 계산 로직
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS: 3개 셀 밀착 및 디자인 최적화
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    /* 메인 타이틀 스타일 */
    .main-title { font-size: 22px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 15px !important; font-weight: 800; color: #2E5077; margin-top: 15px !important; display: block; margin-bottom: 5px; }

    /* [중요] 3개 셀(Column) 간격 제거 및 높이 일치 */
    div[data-testid="stHorizontalBlock"] { gap: 0rem !important; align-items: stretch !important; }
    
    /* 버튼 스타일 정의 */
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
    
    /* 왼쪽 셀 버튼 둥글게 */
    div[data-testid="column"]:nth-child(1) button { border-top-left-radius: 10px !important; border-bottom-left-radius: 10px !important; border-right: none !important; }
    /* 오른쪽 셀 버튼 둥글게 */
    div[data-testid="column"]:nth-child(3) button { border-top-right-radius: 10px !important; border-bottom-right-radius: 10px !important; border-left: none !important; }

    /* 중앙 타이틀 셀 디자인 */
    .title-cell-box {
        background-color: #F1F5F9;
        border-top: 1px solid #CBD5E1;
        border-bottom: 1px solid #CBD5E1;
        height: 56px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        width: 100%;
    }
    
    /* 결과 카드 및 헤더 */
    .building-header { font-size: 17px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px; background-color: #ffffff; }
    .time-highlight { color: #FF4B4B; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 필터 영역 (이 부분이 보여야 함)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
picked_date = st.date_input("날짜", value=st.session_state.search_date, key="input_date", label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
# 체크박스를 2열로 배치하여 공간 절약
c_bu1, c_bu2 = st.columns(2)
with c_bu1:
    bu_0 = st.checkbox(ALL_BU[0], value=True)
    bu_2 = st.checkbox(ALL_BU[2], value=False)
    bu_4 = st.checkbox(ALL_BU[4], value=False)
    bu_6 = st.checkbox(ALL_BU[6], value=False)
with c_bu2:
    bu_1 = st.checkbox(ALL_BU[1], value=True)
    bu_3 = st.checkbox(ALL_BU[3], value=False)
    bu_5 = st.checkbox(ALL_BU[5], value=False)

selected_bu = []
for i, val in enumerate([bu_0, bu_1, bu_2, bu_3, bu_4, bu_5, bu_6]):
    if val: selected_bu.append(ALL_BU[i])

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

# 4. 결과 출력 섹션 (3개 셀 구조)
if st.session_state.triggered:
    st.write("---")
    curr = st.session_state.search_date
    w_idx = curr.weekday()
    t_color = "#0000FF" if w_idx == 5 else ("#FF0000" if w_idx == 6 else "#1E3A5F")
    shift = get_shift_group(curr)

    # [핵심] 3개의 셀(Column) 생성 및 각 셀에 요소 배치
    nav_col1, nav_col2, nav_col3 = st.columns([1, 6, 1])
    
    with nav_col1:
        if st.button("◀", key="arrow_prev"):
            st.session_state.search_date -= timedelta(days=1)
            st.rerun()

    with nav_col2:
        st.markdown(f"""
            <div class="title-cell-box">
                <div style="font-size: 14px; font-weight: 800; color: #1E3A5F; margin-bottom: 2px;">📋 성의교정 대관 현황</div>
                <div style="font-size: 14px; font-weight: 700; color: {t_color};">
                    [ {curr.strftime('%Y.%m.%d')}({WEEKDAY_KR[w_idx]}) | {shift} ]
                </div>
            </div>
        """, unsafe_allow_html=True)

    with nav_col3:
        if st.button("▶", key="arrow_next"):
            st.session_state.search_date += timedelta(days=1)
            st.rerun()

    # 데이터 출력
    df = fetch_data(st.session_state.search_date)
    if not df.empty:
        target_wd = str(st.session_state.search_date.weekday() + 1)
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            for _, row in bu_df.iterrows():
                # 당일 대관 및 기간 대관 통합 출력 (심플 로직)
                is_today = (row['startDt'] == row['endDt'])
                allow = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                
                if is_today or (target_wd in allow):
                    st.markdown(f"""
                        <div class="event-card">
                            📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                            📄 {row['eventNm']}
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br><center><a href='#input_date' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center>", unsafe_allow_html=True)
