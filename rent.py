import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 날짜 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 3, 13)

# 쿼리 파라미터 확인 (버튼 클릭 시 날짜 변경용)
if "d" in st.query_params:
    try:
        p_date = datetime.strptime(st.query_params["d"], "%Y-%m-%d").date()
        if st.session_state.target_date != p_date:
            st.session_state.target_date = p_date
    except: pass

# 2. 근무조 계산 (3/13 금요일 = A조 기준)
def get_shift(d):
    anchor = date(2026, 3, 13)
    diff = (d - anchor).days
    shifts = [
        {"n": "A조", "bg": "#FF9800"}, # 주황
        {"n": "B조", "bg": "#E91E63"}, # 빨강
        {"n": "C조", "bg": "#2196F3"}  # 파랑
    ]
    return shifts[diff % 3]

# 3. CSS (원본 디자인 100% 유지)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .res-main-title { font-size: 20px; font-weight: 800; color: #1E3A5F; display: block; }
    .nav-link-bar {
        display: flex; width: 100%; background: white; border: 1px solid #D1D9E6; 
        border-radius: 0 0 10px 10px; margin-bottom: 25px;
    }
    .nav-item {
        flex: 1; text-align: center; padding: 10px 0; text-decoration: none; 
        color: #1E3A5F; font-weight: bold; font-size: 13px; border-right: 1px solid #F0F0F0;
    }
    .nav-item:last-child { border-right: none; }
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin: 15px 0 12px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px; background: white; }
    .badge { float: right; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; background: #FFF4E5; color: #B25E09; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 4. 입력 폼
with st.form("search"):
    d_input = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
    st.write("**🏢 건물 선택**")
    bus = ["성의회관", "의생명산업연구원", "옴니버스 파크", "서울성모별관"]
    sel_bus = [b for b in bus if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]
    if st.form_submit_button("🔍 검색", use_container_width=True):
        st.session_state.target_date = d_input
        st.query_params["d"] = d_input.strftime("%Y-%m-%d")
        st.rerun()

# 5. 결과 상단 (날짜/근무조/이동버튼)
d = st.session_state.target_date
s = get_shift(d)
w_str = ['월','화','수','목','금','토','일'][d.weekday()]

st.markdown(f"""
<div class="date-display-box">
    <span class="res-main-title">성의교정 대관 현황</span>
    <div style="font-size:18px; font-weight:700; color:#333; margin-top:5px;">
        {d.strftime("%Y.%m.%d")}.({w_str})
        <span style="background:{s['bg']}; color:white; padding:2px 8px; border-radius:15px; font-size:14px; margin-left:8px;">근무 : {s['n']}</span>
    </div>
</div>
<div class="nav-link-bar">
    <a href="./?d={(d-timedelta(1)).strftime('%Y-%m-%d')}" target="_self" class="nav-item">◀ Before</a>
    <a href="./?d={date(2026,3,13).strftime('%Y-%m-%d')}" target="_self" class="nav-item">Today</a>
    <a href="./?d={(d+timedelta(1)).strftime('%Y-%m-%d')}" target="_self" class="nav-item">Next ▶</a>
</div>
""", unsafe_allow_html=True)

# 6. 데이터 출력
@st.cache_data(ttl=60)
def get_df(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    p = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        r = requests.get(url, params=p, timeout=5)
        return pd.DataFrame(r.json().get('res', []))
    except: return pd.DataFrame()

df = get_df(d)
for b in sel_bus:
    st.markdown(f'<div class="building-header">🏢 {b}</div>', unsafe_allow_html=True)
    if not df.empty:
        b_df = df[df['buNm'].str.contains(b, na=False)]
        if not b_df.empty:
            for _, row in b_df.iterrows():
                st.markdown(f"""
                <div class="event-card">
                    <span class="badge">예약확정</span>
                    <div style="font-weight:bold; color:#1E3A5F; font-size:16px;">📍 {row['placeNm']}</div>
                    <div style="color:#FF4B4B; font-weight:bold; margin-top:4px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                    <div style="font-size:14px; margin-top:4px;">📄 {row['eventNm']}</div>
                </div>
                """, unsafe_allow_html=True)
        else: st.write("내역 없음")
