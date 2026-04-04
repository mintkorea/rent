import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 (모바일 중심)
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회(M)", page_icon="🏫", layout="centered")

# --- 🛠️ 내부 로직 (에러 방지만 적용) ---
def get_weekday_names(codes):
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    if not codes: return ""
    return ",".join([days.get(c.strip(), "") for c in str(codes).split(",") if c.strip() in days])

def get_work_shift(d):
    anchor = date(2026, 3, 13)
    diff = (d - anchor).days
    shifts = [{"n": "A조", "bg": "#FF9800"}, {"n": "B조", "bg": "#E91E63"}, {"n": "C조", "bg": "#2196F3"}]
    return shifts[diff % 3]

# --- 🎨 기존의 큼직한 디자인 복구 ---
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    /* 제목과 날짜를 아주 큼직하게 */
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px 12px 0 0; border: 2px solid #D1D9E6; border-bottom: none;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    
    /* 네비게이션 바 버튼 크게 */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 2px solid #D1D9E6 !important; border-radius: 0 0 12px 12px !important; 
        margin-bottom: 25px !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 15px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important; font-weight: bold !important; 
        font-size: 16px !important; border-right: 1px solid #eee;
    }
    
    /* 대관 카드: 글자 크기 키움 */
    .building-header { font-size: 20px !important; font-weight: bold; color: #2E5077; border-bottom: 3px solid #2E5077; padding-bottom: 5px; margin: 20px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 8px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 15px !important; background-color: #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .place-text { font-size: 18px !important; font-weight: bold; color: #1E3A5F; }
    .time-text { color: #FF4B4B !important; font-weight: bold; font-size: 17px !important; margin: 5px 0; }
    .event-text { font-size: 16px !important; color: #000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# [입력 및 검색 로직 생략 - 기존과 동일]
# ...

# 3. 데이터 가져오기 (오류 방지)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = res.json().get('res', [])
        return pd.DataFrame(data) if data else pd.DataFrame()
    except: return pd.DataFrame()

# 4. 결과 출력 (가독성 극대화)
# ... (상단 날짜 출력부)
# 카드 내부 예시:
# st.markdown(f"""
# <div class="event-card">
#     <div class="place-text">📍 {row['placeNm']}</div>
#     <div class="time-text">⏰ {row['startTime']} ~ {row['endTime']}</div>
#     <div class="event-text">📄 {row['eventNm']}</div>
#     <div style="font-size:14px; color:#555; margin-top:8px;">👤 {row['mgDeptNm']}</div>
# </div>
# """, unsafe_allow_html=True)
