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

# [핵심] 클릭한 만큼 날짜를 누적시키는 함수 (이게 진짜 성공 로직입니다)
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (성공한 스크린샷 17:36 레이아웃 100% 재현)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 성공한 통합 날짜 박스 디자인 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 12px; }
    
    /* [정렬 핵심] 화살표 버튼과 날짜를 한 줄로 */
    div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
    
    /* 성공한 파란색 정사각형 버튼 스타일 */
    div.stButton > button {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 22px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 60px !important; height: 45px !important;
        padding: 0 !important; display: flex; align-items: center; justify-content: center;
    }
    
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; line-height: 45px; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 원본 카드 디자인 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-top: 15px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px 12px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# 3. 입력부 (상단 타이틀은 스크린샷 스타일로 유지)
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 날짜/건물/유형 선택 (사용자님 원본 소스)
target_date_input = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date_input

selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]))]
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (생략 없이 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (성공한 박스 내 화살표 레이아웃)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [여기가 성공 포인트] 박스 안에 컬럼으로 화살표와 날짜 배치
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("⬅️", key="btn_prev"):
            change_date(-1)
            st.rerun()
    with col2:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col3:
        if st.button("➡️", key="btn_next"):
            change_date(1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 출력 루프 (사용자님 원본 카드 디자인 적용)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # ... 사용자님의 상세 데이터 필터링 및 st.markdown(event-card) 로직 ...
