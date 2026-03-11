import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")

def today_kst():
    return datetime.now(KST).date()

# 공휴일 체크 함수 (색상 로직용)
def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정
st.set_page_config(
    page_title="성의교정 대관 조회",
    layout="centered"
)

# 3. 세션 상태 초기화
if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()

if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# 4. CSS 스타일 (요청 사항 반영)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 15px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 5px; display: block; }

    /* [수정] 검색결과 박스 위쪽 여백 및 슬림화 */
    .result-box-container {
        margin-top: 35px; /* 위쪽 여백 추가 */
        background-color: #F8FAFF;
        border: 1px solid #D1D9E6;
        border-radius: 10px;
        padding: 8px 10px; /* 내부 여백 축소(슬림) */
        text-align: center;
        margin-bottom: 15px;
    }
    .result-title { font-size: 17px; font-weight: 800; color: #1E3A5F; margin-bottom: 5px; display: block; }
    
    /* [수정] 버튼 슬림화 및 텍스트 색상 제어 */
    div[data-testid="stColumn"] button { 
        height: 35px !important; 
        padding: 0px !important; 
        min-height: 35px !important;
    }
    .blue-text p { color: #0047FF !important; font-weight: 800 !important; }
    .red-text p { color: #FF0000 !important; font-weight: 800 !important; }
    .normal-text p { font-weight: 700 !important; }

    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin: 15px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 8px; background: white; line-height: 1.4; }
    .no-data-text { color: #999; font-size: 13px; padding: 12px; text-align: center; background: #fcfcfc; border: 1px dashed #ddd; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 5. 입력 영역
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"sel_{b}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

st.write("")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 6. 데이터 로직
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 7. 결과 출력
if st.session_state.search_performed:
    # [수정] 박스 슬림화 및 상단 여백
    st.markdown('<div class="result-box-container"><span class="result-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # [수정] 하단 버튼 구조: < 오늘(날짜/요일) >
    c1, c2, c3 = st.columns([0.6, 3, 0.6])
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 요일 색상 클래스
    t_class = "normal-text"
    if w_idx == 5: t_class = "blue-text"
    elif w_idx == 6 or is_holiday(d): t_class = "red-text"

    with c1:
        if st.button("◀", key="p_btn", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        st.markdown(f'<div class="{t_class}">', unsafe_allow_html=True)
        if st.button(f"{d.strftime('%Y.%m.%d')}.({w_str})", key="today_btn", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        if st.button("▶", key="n_btn", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    df_raw = get_data(st.session_state.target_date)
    target_weekday = str(d.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                combined = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                if not combined.empty:
                    has_bu_content = True
                    for _, row in combined.iterrows():
                        st.markdown(f"""<div class="event-card"><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
