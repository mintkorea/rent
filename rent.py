import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. 한국 시간 및 공휴일 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# 3. CSS 스타일: 타이틀 박스 보존 및 하단 컨트롤러 슬림화
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 15px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 5px; display: block; }

    /* 타이틀 박스 (기존 디자인 복구) */
    .result-box-container {
        margin-top: 35px; 
        background-color: #F8FAFF;
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .result-title { font-size: 19px; font-weight: 800; color: #1E3A5F; margin-bottom: 5px; display: block; }
    .result-date { font-size: 17px; font-weight: 700; }
    
    /* 요일 색상 */
    .blue-date { color: #0047FF !important; }
    .red-date { color: #FF0000 !important; }
    .black-date { color: #333333 !important; }

    /* 하단 슬림 컨트롤러 (버튼) */
    div[data-testid="stColumn"] button { 
        height: 32px !important; 
        min-height: 32px !important;
        padding: 0px !important;
        font-size: 14px !important;
    }

    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin: 15px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 8px; background: white; line-height: 1.4; }
    .no-data-text { color: #999; font-size: 13px; padding: 12px; text-align: center; background: #fcfcfc; border: 1px dashed #ddd; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 4. 입력 UI (기존 로직 유지)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

col_bu, col_ty = st.columns(2)
with col_bu:
    st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
    ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"s_{b}")]
with col_ty:
    st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
    show_today = st.checkbox("당일 대관", value=True)
    show_period = st.checkbox("기간 대관", value=True)

st.write("")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 데이터 로직 (기존 로직 유지)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 요일 색상 클래스 결정
    color_class = "black-date"
    if w_idx == 5: color_class = "blue-date"
    elif w_idx == 6 or is_holiday(d): color_class = "red-date"

    # [디자인] 타이틀 박스 (내부에 날짜 표시)
    st.markdown(f"""
    <div class="result-box-container">
        <span class="result-title">성의교정 대관 현황</span>
        <span class="result-date {color_class}">{d.strftime('%Y.%m.%d')}.({w_str})</span>
    </div>
    """, unsafe_allow_html=True)
    
    # [디자인] 박스 외부 컨트롤러: [ ◀ ] [ 오늘 ] [ ▶ ]
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("◀", key="prev_day", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("오늘", key="go_today", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
    with c3:
        if st.button("▶", key="next_day", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    df_raw = get_data(st.session_state.target_date)
    target_weekday = str(d.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [day.strip() for day in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                combined = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                if not combined.empty:
                    has_content = True
                    for _, row in combined.iterrows():
                        st.markdown(f"""<div class="event-card"><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
