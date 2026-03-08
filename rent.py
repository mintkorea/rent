import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 및 근무조 로직 (원본 동일)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return ['A조', 'B조', 'C조'][(diff + 1) % 3]

# 2. CSS (성공했던 카드 스타일만 유지)
st.markdown("""
<style>
    .block-container { padding: 1rem; max-width: 500px; }
    .building-header { font-size: 17px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; margin-bottom: 10px; }
    .event-card { border: 1px solid #ddd; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 8px; }
    .time-txt { color: #FF4B4B; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 영역
st.title("🏫 성의교정 시설 대관 현황")
picked_date = st.date_input("날짜 선택", value=date(2026, 3, 12))

ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [bu for bu in ALL_BU if st.checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"]))]

# 4. 데이터 로드 (API 호출 원본)
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    return pd.DataFrame(res.json().get('res', []))

# 5. [중요] 성공했던 데이터 표출 로직 (이 부분이 원본입니다)
if st.button("조회하기", use_container_width=True):
    st.write("---")
    w_idx = picked_date.weekday()
    target_wd = str(w_idx + 1) # 월=1, 화=2...
    
    st.info(f"📅 {picked_date.strftime('%Y.%m.%d')} ({WEEKDAY_KR[w_idx]}) | {get_shift_group(picked_date)}")

    df = fetch_data(picked_date)
    if not df.empty:
        # 각 건물별로 그룹화하여 출력
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            
            for _, row in bu_df.iterrows():
                # [성공 원본 필터 조건]
                is_today = (row['startDt'] == row['endDt'])
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                
                # 기간대관 중 오늘 요일이 없으면 건너뜀 (성공 로직의 핵심)
                if not is_today and (target_wd not in allow_days):
                    continue
                
                # 화면에 뿌려주는 HTML 구조 (원본 그대로)
                st.markdown(f"""
                    <div class="event-card">
                        <div style="float:right; font-size:12px; font-weight:bold;">[{row.get('statusNm', '')}]</div>
                        📍 {row['placeNm']} <span class="time-txt">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                        📄 {row['eventNm']}
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")
