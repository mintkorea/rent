import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태에 날짜 보관 (이게 있어야 클릭할 때마다 누적됨)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [핵심] 날짜 변경 함수 (클릭 수만큼 계속 바뀜)
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (사용자님의 스크린샷 디자인 100% 복구)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 25px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .res-main-title { font-size: 26px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 20px; }
    
    /* [복구] 파란색 화살표 버튼 스타일 */
    div.stButton > button.arrow-btn {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 24px !important; font-weight: bold !important;
        border-radius: 5px !important; width: 50px !important; height: 40px !important;
        padding: 0 !important; line-height: 1 !important;
    }

    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 카드 디자인 (📍, ⏰, 📄, 👥 아이콘 및 배치) */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 15px 0 8px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; position: relative; }
    .status-badge { position: absolute; right: 12px; top: 12px; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 12px; background: #FFF4E5; color: #B25E09; }
    .place-name { font-size: 17px; font-weight: bold; color: #1E3A5F; margin-bottom: 4px; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; }
    .event-name { font-size: 14px; margin-top: 5px; color: #333; }
    .info-row { font-size: 13px; color: #666; margin-top: 8px; display: flex; justify-content: space-between; align-items: center; }
    
    /* TOP 버튼 */
    .top-btn { position: fixed; bottom: 80px; right: 20px; background: #1E3A5F; color: white !important; width: 45px; height: 45px; border-radius: 50%; text-align: center; line-height: 45px; font-weight: bold; text-decoration: none; font-size: 12px; z-index: 1000; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 3. 입력 영역
st.markdown('<div style="font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택 (세션과 연동)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

# 건물 선택
buildings = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in buildings if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"sel_{b}")]

# 대관 유형
st.markdown('**🗓️ 대관 유형 선택**')
col_t, col_p = st.columns(2)
with col_t: show_today = st.checkbox("당일 대관", value=True)
with col_p: show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 조회 함수
@st.cache_data(ttl=300)
def get_data(q_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": q_date.strftime('%Y-%m-%d'), "end": q_date.strftime('%Y-%m-%d')}
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(r.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 화면
if st.session_state.search_performed:
    df = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_str = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [핵심] 클릭 수만큼 날짜 변경되는 박스 + 파란 버튼
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1: 
        if st.button("⬅️", key="btn_prev"): change_date(-1); st.rerun()
    with c2: 
        st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3: 
        if st.button("➡️", key="btn_next"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 카드 출력 로직 (원본 디자인)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu.replace(" ", ""), na=False)] if not df.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div style="padding:10px; color:gray;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            if show_today:
                t_df = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not t_df.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, r in t_df.iterrows():
                        st.markdown(f'<div class="event-card"><span class="status-badge">{r["status"]}</span><div class="place-name">📍 {r["placeNm"]}</div><div class="time-row">⏰ {r["startTime"]} ~ {r["endTime"]}</div><div class="event-name">📄 {r["eventNm"]}</div><div class="info-row"><span>🗓️ {r["startDt"]}</span><span>👥 {r["mgDeptNm"]}</span></div></div>', unsafe_allow_html=True)
            if show_period:
                p_df = bu_df[bu_df['startDt'] != bu_df['endDt']]
                if not p_df.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, r in p_df.iterrows():
                        st.markdown(f'<div class="event-card"><span class="status-badge">{r["status"]}</span><div class="place-name">📍 {r["placeNm"]}</div><div class="time-row">⏰ {r["startTime"]} ~ {r["endTime"]}</div><div class="event-name">📄 {r["eventNm"]}</div><div class="info-row"><span>🗓️ {r["startDt"]} ~ {r["endDt"]}</span><span>👥 {r["mgDeptNm"]}</span></div></div>', unsafe_allow_html=True)

    st.markdown('<a href="#top-anchor" class="top-btn">TOP</a>', unsafe_allow_html=True)
