import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [기능] 날짜 변경 함수 (클릭 시마다 누적)
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (성공한 스크린샷 17:36 레이아웃 100% 반영)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 통합 날짜 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 12px; }
    
    /* 파란색 정사각형 버튼 */
    div.stButton > button {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 22px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 60px !important; height: 45px !important;
        padding: 0 !important;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 카드 디자인 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-top: 15px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px 12px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; }
    .status-badge { float: right; padding: 1px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]))]
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

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

# 5. 결과 출력 (데이터 추출 루프 포함)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 박스 내 화살표 정렬
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("⬅️", key="p_v6"): change_date(-1); st.rerun()
    with c2:
        st.markdown(f'<div style="text-align:center; margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="n_v6"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # [데이터 추출 핵심 루프]
    target_weekday = str(d.weekday() + 1)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            if show_today and not bu_df.empty:
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not today_ev.empty:
                    has_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        st.markdown(f'<div class="event-card"><span class="status-badge status-y">예약확정</span><div style="font-weight:bold; color:#1E3A5F;">📍 {row["placeNm"]}</div><div style="color:#FF4B4B; font-weight:bold;">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div style="font-size:14px; margin-top:4px;">📄 {row["eventNm"]}</div><div style="font-size:12px; color:gray; margin-top:5px;">👥 {row["mgDeptNm"]}</div></div>', unsafe_allow_html=True)

            if show_period and not bu_df.empty:
                period_ev = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday, na=False))]
                if not period_ev.empty:
                    has_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in period_ev.iterrows():
                        st.markdown(f'<div class="event-card"><span class="status-badge status-y">예약확정</span><div style="font-weight:bold; color:#1E3A5F;">📍 {row["placeNm"]}</div><div style="color:#FF4B4B; font-weight:bold;">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div style="font-size:14px; margin-top:4px;">📄 {row["eventNm"]}</div></div>', unsafe_allow_html=True)

        if not has_content:
            st.write("대관 내역이 없습니다.")
