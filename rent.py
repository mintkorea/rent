import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 요일 및 근무조 계산 함수
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# 2. CSS: 깔끔한 리스트와 카드 디자인만 남김
st.markdown("""
<style>
    .block-container { padding: 1.5rem !important; max-width: 550px !important; }
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 25px; }
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px; background-color: #ffffff; }
    .time-highlight { color: #FF4B4B; font-weight: 800; }
    .result-info { background-color: #F1F5F9; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 영역
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

picked_date = st.date_input("📅 조회 날짜 선택", value=date(2026, 3, 12))

ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
st.write("🏢 **조회 건물 선택**")
cols = st.columns(2)
selected_bu = []
for i, bu in enumerate(ALL_BU):
    with cols[i % 2]:
        if st.checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"])):
            selected_bu.append(bu)

# 4. 데이터 로드 함수
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (원본 필터 로직)
if st.button("🔍 조회하기", use_container_width=True):
    st.write("---")
    w_idx = picked_date.weekday()
    target_wd = str(w_idx + 1) # 월=1 ~ 일=7
    
    # 상단 요일 정보 표시
    st.markdown(f"""
        <div class="result-info">
            {picked_date.strftime('%Y.%m.%d')} ({WEEKDAY_KR[w_idx]}) | {get_shift_group(picked_date)}
        </div>
    """, unsafe_allow_html=True)

    df = fetch_data(picked_date)
    if not df.empty:
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            for _, row in bu_df.iterrows():
                # [원본 필터링 핵심]
                is_today = (row['startDt'] == row['endDt'])
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                
                # 당일 대관이거나, 기간 대관 중 오늘 요일이 포함된 경우만 노출
                if is_today or (target_wd in allow_days):
                    st.markdown(f"""
                        <div class="event-card">
                            <div style="float:right; font-size:12px; color:#666;">[{row.get('statusNm', '')}]</div>
                            📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                            📄 {row['eventNm']}
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")
