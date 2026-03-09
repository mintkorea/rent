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

def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# [유틸] allowDay 숫자 -> 한글 요일 변환
def get_weekday_names(allow_day_str):
    if not allow_day_str: return ""
    days_map = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}
    day_list = [days_map.get(d.strip()) for d in allow_day_str.split(',') if d.strip() in days_map]
    return f"({','.join(day_list)})" if day_list else ""

# 2. CSS 스타일 (날짜 버튼 디자인 + 하단 여백)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 검색 버튼 (빨간색) */
    div.stButton > button[kind="primary"] {
        background-color: #FF5252 !important; color: white !important;
        border-radius: 8px !important; height: 50px !important; font-weight: bold !important;
    }

    /* 날짜 선택 영역 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 15px; border: 1px solid #E1E8F0; margin: 20px 0;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* 날짜 이동 버튼 (이미지 반영: 하늘색 사각형) */
    div.stButton > button:not([kind="primary"]) {
        background-color: #A3D2F3 !important; 
        border: none !important; 
        color: white !important; 
        font-size: 24px !important; 
        font-weight: bold !important; 
        border-radius: 4px !important; 
        width: 100% !important; 
        height: 45px !important;
        display: flex; align-items: center; justify-content: center;
    }

    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; line-height: 45px; }
    .sat { color: #0000FF !important; } 
    .sun { color: #FF0000 !important; }

    /* 결과 카드 및 하단 여백 */
    .building-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px; }
    .event-card { border: 1px solid #E8E8E8; border-left: 5px solid #1E3A5F; padding: 12px; border-radius: 8px; margin-bottom: 12px; background-color: white; position: relative; }
    .info-sub { font-size: 13px; color: #666; display: flex; justify-content: space-between; margin-top: 10px; border-top: 1px solid #F0F0F0; padding-top: 8px; }

    /* TOP 버튼 및 하단 여백 처리 */
    .top-floating {
        position: fixed; bottom: 25px; right: 20px; background-color: #1E3A5F;
        color: white !important; width: 55px; height: 55px; border-radius: 50%;
        text-align: center; line-height: 55px; font-weight: bold; z-index: 1000;
        text-decoration: none; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .footer-spacer { height: 80px; } /* 하단에 2줄 정도의 빈 공간 확보 */
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 메인 UI 설정
st.session_state.target_date = st.date_input("날짜 선택", value=st.session_state.target_date)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]))]
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True
    components.html("<script>window.parent.document.getElementById('result-start').scrollIntoView({behavior:'smooth'});</script>", height=0)

# 데이터 로딩 함수
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

if st.session_state.search_performed:
    st.markdown('<div id="result-start"></div>', unsafe_allow_html=True)
    df_raw = get_data(st.session_state.target_date)
    
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 결과 상단 날짜 이동 바 (디자인 수정됨)
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("⬅️", key="p_btn"): change_date(-1); st.rerun()
    with c2:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="n_btn"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    target_weekday_num = str(w_idx + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)]
            
            # 당일 대관
            if show_today:
                t_df = bu_df[bu_df['startDt'] == bu_df['endDt']]
                for _, r in t_df.iterrows():
                    has_content = True
                    st.markdown(f"""
                    <div class="event-card">
                        <div class="place-name">📍 {r['placeNm']}</div>
                        <div class="card-row"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                        <div class="card-row">📄 {r['eventNm']}</div>
                        <div class="info-sub"><span>🗓️ {r['startDt']}</span><span>👥 {r.get('mgDeptNm','')}</span></div>
                    </div>""", unsafe_allow_html=True)

            # 기간 대관 (요일 표시 포함)
            if show_period:
                p_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday_num, na=False))]
                for _, r in p_df.iterrows():
                    has_content = True
                    weekdays = get_weekday_names(r.get('allowDay', ''))
                    st.markdown(f"""
                    <div class="event-card">
                        <div class="place-name">📍 {r['placeNm']}</div>
                        <div class="card-row"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                        <div class="card-row">📄 {r['eventNm']}</div>
                        <div class="info-sub"><span>🗓️ {r['startDt']} ~ {r['endDt']} <b style="color:#1E3A5F;">{weekdays}</b></span><span>👥 {r.get('mgDeptNm','')}</span></div>
                    </div>""", unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div style="color:gray; padding:10px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    # 하단 여백 추가 (TOP 버튼이 카드 글자를 가리지 않게 함)
    st.markdown('<div class="footer-spacer"></div>', unsafe_allow_html=True)

st.markdown('<a href="#top-anchor" class="top-floating">TOP</a>', unsafe_allow_html=True)
