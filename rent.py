import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# 1. 기본 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(
    page_title="성의교정 대관 현황(M)", 
    page_icon="🏫", 
    layout="centered"
)

# 세션 상태 초기화
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()

# 2. 초기 스타일 (간격 조정 전 원본)
st.markdown("""
<style>
    .main-title { 
        font-size: 24px !important; 
        font-weight: 800; 
        text-align: center; 
        color: #1E3A5F; 
        margin-bottom: 30px !important; 
    }
    .building-header { 
        font-size: 18px; 
        font-weight: bold; 
        color: #2E5077; 
        margin-top: 30px; 
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 5px; 
    }
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 5px solid #2E5077; 
        padding: 15px; 
        border-radius: 5px; 
        margin-bottom: 15px; 
        background-color: #ffffff; 
    }
    .date-display-box { 
        text-align: center; 
        background-color: #F8FAFF; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #D1D9E6; 
    }
    .sat { color: blue; }
    .sun { color: red; }
</style>
""", unsafe_allow_html=True)

# 제목 표시
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 조회 설정 영역 (Form)
with st.form("search_form"):
    selected_date = st.date_input("조회 날짜", value=st.session_state.target_date)
    
    st.markdown("### 🏢 건물 선택")
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    
    # 건물 선택 체크박스
    cols = st.columns(2)
    selected_bu_list = []
    for i, bu in enumerate(ALL_BU):
        with cols[i % 2]:
            if st.checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"])):
                selected_bu_list.append(bu)
                
    submit = st.form_submit_button("🔍 검색", use_container_width=True)
    if submit:
        st.session_state.target_date = selected_date

# 4. 데이터 로드 함수
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {
        "mode": "getReservedData", 
        "start": d.strftime('%Y-%m-%d'), 
        "end": d.strftime('%Y-%m-%d')
    }
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code == 200:
            return pd.DataFrame(res.json().get('res', []))
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# 5. 결과 출력
d = st.session_state.target_date
df_raw = get_data(d)

# 상단 날짜 박스
w_idx = d.weekday()
w_str = ['월','화','수','목','금','토','일'][w_idx]
w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

st.markdown(f"""
<div class="date-display-box">
    <div style="font-size: 20px; font-weight: bold;">{d.strftime("%Y년 %m월 %d일")}</div>
    <div style="font-size: 18px;" class="{w_class}">({w_str}요일)</div>
</div>
""", unsafe_allow_html=True)

# 건물별 내역 출력
if not selected_bu_list:
    st.warning("조회할 건물을 하나 이상 선택해주세요.")
else:
    for bu in selected_bu_list:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        has_data = False
        if not df_raw.empty:
            # 건물명 매칭 (공백 제거 후 비교)
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            if not bu_df.empty:
                for _, row in bu_df.iterrows():
                    has_data = True
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="font-size: 17px; font-weight: bold; color: #1E3A5F;">📍 {row['placeNm']}</div>
                        <div style="font-size: 16px; color: #FF4B4B; font-weight: bold; margin: 5px 0;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="font-size: 15px;">📄 {row['eventNm']}</div>
                        <div style="font-size: 13px; color: #666; margin-top: 10px; border-top: 1px solid #eee; padding-top: 5px;">
                            👥 {row['mgDeptNm']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        if not has_data:
            st.info(f"{bu}에 예정된 대관 내역이 없습니다.")
