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

# CSS 스타일 (다른 부분은 건드리지 않고 컨트롤러 고정 레이아웃만 추가)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 1:8:1 가로 정렬 강제 레이아웃 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1),
    [data-testid="stHorizontalBlock"] > div:nth-child(3) {
        flex: 1 !important;
        min-width: 40px !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex: 8 !important;
    }

    /* 이미지 스타일의 사각 타이틀 박스 */
    .title-rect-box {
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 8px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 52px;
    }
    
    .res-main-title { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; line-height: 1.2; }
    .res-sub-title { font-size: 14px; font-weight: 700; color: #333; line-height: 1.2; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 버튼 스타일 고정 */
    .stButton > button {
        height: 52px !important;
        width: 100% !important;
        border-radius: 8px !important;
        border: 1px solid #d1d9e6 !important;
        background-color: #f8f9fa !important;
        color: #1E3A5F !important;
    }

    /* 기존 결과 카드 스타일 (변경 없음) */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px !important; background-color: #ffffff; line-height: 1.2 !important; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; }
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; }
    .no-data-text { color: #888; font-size: 14px; padding: 10px 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('### 🏫 성의교정 시설 대관 현황')

# 입력 영역
target_date = st.date_input("날짜", value=st.session_state.target_date)
st.session_state.target_date = target_date

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}"):
        selected_bu.append(b)

show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 결과 출력 (1:8:1 가로 고정 레이아웃)
if st.session_state.search_performed:
    col_l, col_m, col_r = st.columns([1, 8, 1])
    
    with col_l:
        if st.button("◀", key="p_btn"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
            
    with col_m:
        d = st.session_state.target_date
        w_list = ['월','화','수','목','금','토','일']
        w_str = w_list[d.weekday()]
        w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")
        st.markdown(f"""
        <div class="title-rect-box">
            <span class="res-main-title">성의교정 대관 현황</span>
            <span class="res-sub-title">{d.strftime('%Y.%m.%d')}.<span class="{w_class}">({w_str})</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        if st.button("▶", key="n_btn"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    df_raw = get_data(st.session_state.target_date)
    t_weekday = str(st.session_state.target_date.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: t_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                
                if not t_ev.empty:
                    has_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in t_ev.sort_values(by='startTime').iterrows():
                        st.markdown(f'<div class="event-card"><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div></div>', unsafe_allow_html=True)
                
                if not v_p_ev.empty:
                    has_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in v_p_ev.sort_values(by='startTime').iterrows():
                        st.markdown(f'<div class="event-card"><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div></div>', unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
