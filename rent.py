import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 날짜 변경 함수
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (스크린샷 18:13 디자인 100% 복제)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 검색하기 버튼 스타일 고정 */
    div.stButton > button[kind="primary"] {
        background-color: #FF4B4B !important; color: white !important;
        width: 100% !important; height: 45px !important; border-radius: 8px !important;
        font-weight: bold !important; margin-top: 10px !important;
    }

    /* 통합 날짜 박스 및 내부 버튼 정렬 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-top: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* 파란색 화살표 버튼 (정사각형 유지) */
    div.stButton > button:not([kind="primary"]) {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 20px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 55px !important; height: 45px !important;
    }
    
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; line-height: 45px; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 카드 디자인 (스크린샷 18:13:39 기준) */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-top: 25px; }
    .section-title { font-size: 17px; font-weight: bold; color: #333; margin: 15px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 12px; background-color: white; position: relative; }
    .status-badge { position: absolute; top: 12px; right: 12px; background-color: #FFF4E5; color: #B25E09; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .place-name { font-size: 17px; font-weight: bold; color: #1E3A5F; margin-bottom: 5px; }
    .time-row { font-size: 16px; font-weight: bold; color: #FF4B4B; margin-bottom: 5px; }
    .event-name { font-size: 14px; color: #444; line-height: 1.4; }
    .dept-name { font-size: 13px; color: #777; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏢 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

col_bu = st.columns(2)
with col_bu[0]:
    bu_sv = st.checkbox("성의회관", value=True)
    bu_bi = st.checkbox("의생명산업연구원", value=True)
with col_bu[1]:
    bu_op = st.checkbox("옴니버스 파크", value=False)
    bu_etc = st.checkbox("기타 건물", value=False)

st.write(" ")
show_today = st.checkbox("📌 당일 대관", value=True)
show_period = st.checkbox("🗓️ 기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [박스 레이아웃 복구]
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("⬅️", key="p_btn"): change_date(-1); st.rerun()
    with c2:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="n_btn"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 선택된 건물 필터링
    sel_names = []
    if bu_sv: sel_names.append("성의회관")
    if bu_bi: sel_names.append("의생명산업연구원")
    if bu_op: sel_names.append("옴니버스 파크")

    target_weekday = str(d.weekday() + 1)

    for bu in sel_names:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)] if not df_raw.empty else pd.DataFrame()
        
        # 당일 대관
        if show_today:
            t_df = bu_df[bu_df['startDt'] == bu_df['endDt']]
            if not t_df.empty:
                st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                for _, r in t_df.iterrows():
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge">예약확정</span>
                        <div class="place-name">📍 {r['placeNm']}</div>
                        <div class="time-row">⏰ {r['startTime']} ~ {r['endTime']}</div>
                        <div class="event-name">📄 {r['eventNm']}</div>
                        <div class="dept-name">👥 {r['mgDeptNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 기간 대관
        if show_period:
            p_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday, na=False))]
            if not p_df.empty:
                st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                for _, r in p_df.iterrows():
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge">예약확정</span>
                        <div class="place-name">📍 {r['placeNm']}</div>
                        <div class="time-row">⏰ {r['startTime']} ~ {r['endTime']}</div>
                        <div class="event-name">📄 {r['eventNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
