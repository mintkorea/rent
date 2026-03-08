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

# 요일/근무조 로직
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS: 최소한의 스타일만 적용 (가독성 중심)
st.markdown("""
<style>
    .block-container { padding: 1.5rem !important; max-width: 550px !important; }
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 25px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 20px; display: block; }
    
    /* 결과 타이틀 박스 디자인 */
    .nav-title-box {
        background-color: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        height: 55px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    
    /* 대관 정보 카드 */
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px; background-color: #f9f9f9; }
    .time-tag { color: #FF4B4B; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 입력 영역 (항상 노출)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택
st.markdown('<span class="sub-label">📅 조회 날짜</span>', unsafe_allow_html=True)
picked_date = st.date_input("날짜선택", value=st.session_state.search_date, label_visibility="collapsed")

# 건물 선택 (간결하게 배치)
st.markdown('<span class="sub-label">🏢 조회 건물</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [bu for bu in ALL_BU if st.checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"]))]

st.write(" ")
# 검색 버튼
if st.button("🔍 위 조건으로 검색하기", use_container_width=True):
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

# 4. 결과 출력 영역 (검색 버튼을 눌러야 나타남)
if st.session_state.triggered:
    st.markdown("---")
    
    # 3개의 셀로 구성된 네비게이션 (좌버튼 | 타이틀 | 우버튼)
    c1, c2, c3 = st.columns([1, 4, 1])
    
    with c1:
        if st.button("◀", key="prev_day", use_container_width=True):
            st.session_state.search_date -= timedelta(days=1)
            st.rerun()
            
    with c2:
        curr = st.session_state.search_date
        w_idx = curr.weekday()
        t_color = "#FF0000" if w_idx == 6 else ("#0000FF" if w_idx == 5 else "#1E3A5F")
        st.markdown(f"""
            <div class="nav-title-box">
                <div style="font-size: 14px; font-weight: 800; color: #1E3A5F;">📋 대관 현황</div>
                <div style="font-size: 14px; font-weight: 700; color: {t_color};">
                    {curr.strftime('%Y.%m.%d')} ({WEEKDAY_KR[w_idx]}) | {get_shift_group(curr)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with c3:
        if st.button("▶", key="next_day", use_container_width=True):
            st.session_state.search_date += timedelta(days=1)
            st.rerun()

    # 데이터 표시
    df = fetch_data(st.session_state.search_date)
    if not df.empty:
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if bu_df.empty: continue
            
            st.markdown(f"#### 🏢 {bu}")
            for _, row in bu_df.iterrows():
                st.markdown(f"""
                <div class="event-card">
                    📍 {row['placeNm']} <span class="time-tag">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                    📄 {row['eventNm']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("해당 날짜에 대관 내역이 없습니다.")

    st.markdown("<br><center><a href='#main-title' style='color:#777; font-size:12px;'>맨 위로 이동</a></center>", unsafe_allow_html=True)
