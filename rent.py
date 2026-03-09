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

# [기능] 날짜 이동 시에도 검색 상태 유지
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": st.session_state.target_date -= timedelta(days=1)
    if params["nav"] == "next": st.session_state.target_date += timedelta(days=1)
    st.session_state.search_performed = True 
    st.query_params.clear()
    st.rerun()

# CSS 스타일 (원본 스타일 유지 + 화살표 위치 고정)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* 타이틀 박스 내부에서 날짜와 화살표가 한 줄에 나오도록 수정 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    .date-navigation-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
    }
    .nav-arrow { font-size: 28px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }
    
    /* 원본 카드 디자인 그대로 유지 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; line-height: 1.2 !important; }
    .today-card { background-color: #F8FAFF; } 
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 2px; }
    .event-name { font-size: 14px; margin-top: 4px; color: #333; font-weight: 500; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 5px; display: flex; justify-content: space-between; align-items: flex-end; }
    .dept-label { text-align: right; flex-grow: 1; }
    .period-label { color: #d63384; font-weight: bold; white-space: nowrap; }
    .status-badge { display: inline-block; padding: 1px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
    
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 4px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 3. 데이터 로직 (원본 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    formatted_date = d.strftime("%Y.%m.%d")
    
    # [교정] 박스 내부에서 화살표를 감싸도록 HTML 구조 최적화
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-navigation-wrapper">
            <a href="./?nav=prev" target="_self" class="nav-arrow">⬅️</a>
            <span class="res-sub-title">{formatted_date}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">➡️</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 원본 카드 출력 로직 그대로 실행
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                # 당일/기간 필터링
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                
                if show_today and not today_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.sort_values(by='startTime').iterrows():
                        s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                        st.markdown(f'<div class="event-card today-card"><span class="status-badge {s_cls}">{row["status"]}</span><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div><div class="bottom-info"><span class="period-label">🗓️ {row["startDt"]}</span><span class="dept-label">👥 {row["mgDeptNm"]}</span></div></div>', unsafe_allow_html=True)

                if show_period and not period_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in period_ev.sort_values(by='startTime').iterrows():
                        s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                        st.markdown(f'<div class="event-card"><span class="status-badge {s_cls}">{row["status"]}</span><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div><div class="bottom-info"><span class="period-label">🗓️ {row["startDt"]} ~ {row["endDt"]}</span><span class="dept-label">👥 {row["mgDeptNm"]}</span></div></div>', unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div style="color:#888; padding:5px 0 15px 5px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown("""<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>""", unsafe_allow_html=True)
