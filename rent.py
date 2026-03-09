
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 상태 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [기능] 날짜 변경 함수
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (사용자님의 성공한 디자인 100% 복제)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 25px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* 파란색 화살표 버튼 (성공 버전) */
    div.stButton > button {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 20px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 55px !important; height: 40px !important;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 카드 디자인 (📍, ⏰ 등 원본 디자인 복구용 기초) */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-top: 20px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background: white; position: relative; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

# 건물 선택 (조회 실패 방지를 위해 기본값 설정)
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크"] if st.checkbox(b, value=True)]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. [중요] 데이터 조회 로직 (이게 살아있어야 데이터가 나옵니다)
@st.cache_data(ttl=60)
def get_rental_data(q_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": q_date.strftime('%Y-%m-%d'), "end": q_date.strftime('%Y-%m-%d')}
    try:
        r = requests.get(url, params=params, timeout=10)
        return pd.DataFrame(r.json().get('res', []))
    except:
        return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    df = get_rental_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_str = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [박스 및 화살표 버튼]
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("⬅️", key="p_btn"): change_date(-1); st.rerun()
    with c2:
        st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="n_btn"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 매칭 및 출력
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # 건물명 필터링 (공백 제거 후 비교)
        b_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)] if not df.empty else pd.DataFrame()
        
        if b_df.empty:
            st.write("대관 내역이 없습니다.")
        else:
            for _, r in b_df.iterrows():
                st.markdown(f"""
                <div class="event-card">
                    <div style="font-weight:bold; color:#1E3A5F;">📍 {r['placeNm']}</div>
                    <div style="color:#FF4B4B; font-weight:bold;">⏰ {r['startTime']} ~ {r['endTime']}</div>
                    <div style="font-size:14px;">📄 {r['eventNm']}</div>
                    <div style="font-size:12px; color:gray; margin-top:5px;">👥 {r['mgDeptNm']}</div>
                </div>
                """, unsafe_allow_html=True)
