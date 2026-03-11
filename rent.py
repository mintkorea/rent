import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. 한국 시간 및 공휴일 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

# 공휴일 체크 (빨간색 표시용)
def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# 3. CSS 스타일 (박스 슬림화 + 요일 색상 강제 지정)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 15px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 8px; display: block; }

    /* 결과 박스 슬림화 디자인 */
    .result-box-container {
        background-color: #F8FAFF;
        border: 1px solid #D1D9E6;
        border-radius: 10px;
        padding: 8px 10px;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .result-title { font-size: 17px; font-weight: 800; color: #1E3A5F; margin-bottom: 5px; display: block; }
    
    /* 요일별 버튼 텍스트 색상 (중앙 버튼 전용) */
    .blue-text p { color: #0047FF !important; font-weight: 800 !important; }
    .red-text p { color: #FF0000 !important; font-weight: 800 !important; }
    .normal-text p { font-weight: 700 !important; }

    /* 카드 및 헤더 디자인 */
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin: 15px 0 10px 0; }
    .section-title { font-size: 15px; font-weight: bold; color: #555; margin: 8px 0 4px 0; padding-left: 5px; border-left: 3px solid #ccc; }
    
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 10px 12px; border-radius: 5px; margin-bottom: 10px; 
        background: white; line-height: 1.4 !important; 
    }
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 14px; font-weight: bold; color: #FF4B4B; margin-top: 2px; }
    .event-name { font-size: 14px; margin-top: 4px; color: #333; font-weight: 500; }

    /* 내역 없음 스타일 */
    .no-data-text { color: #999; font-size: 13px; padding: 15px; text-align: center; background: #fcfcfc; border: 1px dashed #ddd; border-radius: 8px; margin-top: 5px; }

    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 4px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 4. 입력 UI
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

col_bu, col_ty = st.columns(2)
with col_bu:
    st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
    ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"sel_{b}")]
with col_ty:
    st.markdown('<span class="sub-label">🗓️ 유형 선택</span>', unsafe_allow_html=True)
    show_today = st.checkbox("당일 대관", value=True)
    show_period = st.checkbox("기간 대관", value=True)

st.write("")
st.markdown('<div id="btn-anchor"></div>', unsafe_allow_html=True)
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 데이터 로직
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
    # 스크롤 이동
    components.html(f"<script>var element = window.parent.document.getElementById('btn-anchor'); if (element) {{ element.scrollIntoView({{behavior: 'smooth', block: 'start'}}); }}</script>", height=0)

    # 슬림 결과 타이틀 박스
    st.markdown('<div class="result-box-container"><span class="result-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([0.8, 3, 0.8])
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 색상 클래스 결정 (토요일: 파랑 / 일요일,공휴일: 빨강)
    text_color_class = "normal-text"
    if w_idx == 5: text_color_class = "blue-text"
    elif w_idx == 6 or is_holiday(d): text_color_class = "red-text"

    with c1:
        if st.button("◀", key="prev_btn"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        # 중앙 버튼 (요일 색상 적용)
        st.markdown(f'<div class="{text_color_class}">', unsafe_allow_html=True)
        if st.button(f"{d.strftime('%Y.%m.%d')}.({w_str})", key="curr_btn", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        if st.button("▶", key="next_btn"):
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

                # 당일 대관
                if not t_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in t_ev.sort_values(by='startTime').iterrows():
                        st.markdown(f"""<div class="event-card"><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)
                
                # 기간 대관
                if not v_p_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in v_p_ev.sort_values(by='startTime').iterrows():
                        st.markdown(f"""<div class="event-card"><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:80px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
