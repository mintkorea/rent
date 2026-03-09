import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 초기화
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (메인 페이지 줄간격 극소화 및 버튼 정렬)
st.markdown("""
<style>
    .block-container { padding: 0.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 줄간격 및 마진 극소화 */
    p, div, label { line-height: 1.1 !important; margin-bottom: 0px !important; }
    .stCheckbox { margin-bottom: -15px !important; }
    div[data-testid="stVerticalBlock"] > div { padding-bottom: 2px !important; }

    /* 메인 헤더 */
    .main-header { text-align: center; color: #1E3A5F; font-size: 20px !important; font-weight: 800; margin: 5px 0 10px 0 !important; }
    .section-title { font-size: 14px; font-weight: bold; color: #444; margin: 8px 0 2px 0 !important; }

    /* 화살표 버튼 수평 고정 레이아웃 */
    .nav-bar { display: flex; align-items: center; justify-content: space-between; background: #F8FAFF; padding: 5px 10px; border-radius: 8px; border: 1px solid #E1E8F0; margin: 10px 0; }
    .nav-date { font-size: 17px; font-weight: 700; color: #333; flex-grow: 1; text-align: center; }
    
    /* 버튼 스타일 조정 */
    .stButton > button { height: 35px !important; padding: 0 10px !important; }
    div.stButton > button[kind="primary"] { background-color: #FF5252 !important; color: white !important; font-weight: bold !important; border: none !important; width: 100%; margin-top: 10px; }

    /* 카드 디자인 */
    .building-header { font-size: 16px; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 1px; margin-top: 12px; margin-bottom: 5px; }
    .event-card { border: 1px solid #E8E8E8; border-left: 4px solid #1E3A5F; padding: 6px 10px; border-radius: 5px; margin-bottom: 4px; background: white; }
    .place-name { font-size: 14px; font-weight: 800; color: #1E3A5F; }
    .time-text { font-weight: bold; color: #E63946; font-size: 13px; }
    .info-sub { font-size: 10.5px; color: #888; display: flex; justify-content: space-between; margin-top: 4px; border-top: 1px solid #F8F8F8; padding-top: 2px; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 추출 함수 (성의회관 3건 모두 누락 없이 가져오기)
def fetch_rental_data(search_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {
        "mode": "getReservedData",
        "start": search_date.strftime('%Y-%m-%d'),
        "end": search_date.strftime('%Y-%m-%d')
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json().get('res', [])
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# 4. 메인 페이지 UI
st.markdown('<div class="main-header">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">📅 날짜 선택</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("d", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<div class="section-title">🏢 건물 선택</div>', unsafe_allow_html=True)
buildings = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in buildings if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}")]

st.markdown('<div class="section-title">📋 대관 유형</div>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", type="primary"):
    st.session_state.search_performed = True

# 5. 검색 결과 영역
if st.session_state.search_performed:
    df = fetch_rental_data(st.session_state.target_date)
    
    d = st.session_state.target_date
    w_str = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
    
    # [개선] 화살표 버튼 수평 고정 레이아웃
    col_prev, col_date, col_next = st.columns([1, 4, 1])
    with col_prev:
        if st.button("⬅️"): change_date(-1); st.rerun()
    with col_date:
        st.markdown(f'<div style="text-align:center; line-height:35px; font-weight:bold; font-size:17px;">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    with col_next:
        if st.button("➡️"): change_date(1); st.rerun()

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()
        
        # 필터링: 당일/기간 대관 구분
        if not bu_df.empty:
            found = False
            for _, r in bu_df.iterrows():
                is_today = r['startDt'] == r['endDt']
                if (is_today and show_today) or (not is_today and show_period):
                    found = True
                    s_cls = "background:#FFF2E6; color:#FF8C00;" if r['statNm'] == "예약확정" else "background:#E6F2FF; color:#007AFF;"
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span class="place-name">📍 {r['placeNm']}</span>
                            <span style="font-size:9px; padding:1px 5px; border-radius:4px; font-weight:bold; {s_cls}">{r['statNm']}</span>
                        </div>
                        <div style="margin:2px 0;"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                        <div style="font-size:12.5px; color:#333;">📄 {r['eventNm']}</div>
                        <div class="info-sub"><span>🗓️ {r['startDt']}</span><span>👥 {r['mgDeptNm']}</span></div>
                    </div>""", unsafe_allow_html=True)
            if not found:
                st.markdown('<div style="color:#999; font-size:12px; padding:5px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#999; font-size:12px; padding:5px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

st.markdown('<a href="#" style="position:fixed; bottom:20px; right:20px; background:#1E3A5F; color:white; width:40px; height:40px; border-radius:50%; text-align:center; line-height:40px; text-decoration:none; font-size:10px; font-weight:bold; z-index:999;">TOP</a>', unsafe_allow_html=True)
