import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 초기화
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# CSS 스타일 (디자인 깨짐 방지 핵심)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 통합 컨트롤러 디자인 (가로 한줄 고정) */
    .custom-nav-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        gap: 8px;
        margin: 15px 0;
    }

    /* 이미지와 같은 사각형 타이틀 박스 */
    .title-box {
        flex-grow: 1;
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 8px 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 56px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .res-main-title { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; }
    .res-sub-title { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 버튼 스타일 (디자인 깨짐 방지용 강제 설정) */
    .nav-btn {
        width: 45px !important;
        height: 56px !important;
        background: #f8f9fa;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: #1E3A5F;
    }

    /* 기존 카드 스타일 유지 */
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 15px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 8px; background: #fff; }
    .no-data-text { color: #888; font-size: 14px; padding: 15px 5px; text-align: center; border: 1px dashed #ddd; border-radius: 5px; margin-top: 5px; }
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; text-decoration: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# --- 입력 UI ---
st.markdown('<span class="sub-label">📅 날짜 직접 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# --- 데이터 로직 ---
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# --- 결과 및 통합 컨트롤러 ---
if st.session_state.search_performed:
    # 1. 날짜 정보 계산
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")
    
    # 2. 통합 레이아웃 (HTML 구조와 Streamlit 버튼 결합)
    # columns를 버리고 단일 column 안에서 가로 정렬 강제
    nav_col_1, nav_col_2, nav_col_3 = st.columns([1, 5, 1])
    
    with nav_col_1:
        if st.button("◀", key="p_day_v2", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
            
    with nav_col_2:
        st.markdown(f"""
        <div class="title-box">
            <span class="res-main-title">성의교정 대관 현황</span>
            <span class="res-sub-title">{d.strftime('%Y.%m.%d')}.<span class="{w_class}">({w_str})</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with nav_col_3:
        if st.button("▶", key="n_day_v2", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 로드
    df_raw = get_data(st.session_state.target_date)
    t_weekday = str(st.session_state.target_date.weekday() + 1)

    # 건물별 출력 로직
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: t_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                
                if not t_ev.empty or not v_p_ev.empty:
                    has_content = True
                    if not t_ev.empty:
                        st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                        for _, r in t_ev.sort_values(by='startTime').iterrows():
                            st.markdown(f'<div class="event-card"><div>📍 {r["placeNm"]}</div><div style="color:#FF4B4B; font-weight:bold;">⏰ {r["startTime"]} ~ {r["endTime"]}</div><div style="font-size:14px; margin-top:4px;">📄 {r["eventNm"]}</div></div>', unsafe_allow_html=True)
                    if not v_p_ev.empty:
                        st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                        for _, r in v_p_ev.sort_values(by='startTime').iterrows():
                            st.markdown(f'<div class="event-card"><div>📍 {r["placeNm"]}</div><div style="color:#FF4B4B; font-weight:bold;">⏰ {r["startTime"]} ~ {r["endTime"]}</div><div style="font-size:14px; margin-top:4px;">📄 {r["eventNm"]}</div></div>', unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
