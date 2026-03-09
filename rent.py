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

# [핵심] 클릭한 만큼 날짜를 누적시키는 함수
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (박스 정렬 및 원본 카드 디자인)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [성공 정렬] 통합 날짜 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* 파란색 화살표 버튼 스타일 (성공 버전) */
    div.stButton > button.arrow-btn {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 20px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 55px !important; height: 40px !important;
        padding: 0 !important; line-height: 1 !important;
    }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 원본 카드 디자인 레이아웃 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px !important; background-color: #ffffff; }
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 2px; }
    .event-name { font-size: 14px; margin-top: 4px; color: #333; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 5px; display: flex; justify-content: space-between; }
    .status-badge { float: right; padding: 1px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI 및 검색
st.markdown('<div style="font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]))]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (원본 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (박스 내부에 버튼식 화살표 배치)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = {0:'월',1:'화',2:'수',3:'목',4:'금',5:'토',6:'일'}[w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [박스 시작]
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # 버튼-날짜-버튼 수평 배치
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("⬅️", key="prev_v5", help="전날", use_container_width=True):
            change_date(-1)
            st.rerun()
    with c2:
        st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="next_v5", help="다음날", use_container_width=True):
            change_date(1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 이후 데이터 출력 (사용자님의 원본 카드 로직...)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # (생략: 사용자님의 원본 카드 루프 및 필터링 소스...)
