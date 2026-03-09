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

# 날짜 변경 함수
def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# CSS 스타일
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [수정 1] 첫 페이지 요소들 사이의 줄간격 축소 */
    [data-testid="stVerticalBlock"] > div { margin-bottom: -15px !important; }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* [수정 2] 검색 버튼 하단 여백 추가 (박스와의 간격 벌리기) */
    div.stButton > button[kind="secondary"] { margin-bottom: 30px !important; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* [수정 3] 박스 내 화살표 버튼 스타일 (투명하게) */
    div.stButton > button.arrow-btn {
        background: none !important; border: none !important; 
        font-size: 24px !important; color: #1E3A5F !important; padding: 0 !important;
    }
    
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; display: block; margin-top: 10px !important; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v_{b}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
# 검색 버튼 (CSS에서 하단 마진 30px 적용됨)
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

# 4. 결과 출력
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    # [수정 3] 타이틀 박스 안에 화살표 넣기
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.button("◀", key="p_btn", on_click=move_date, args=(-1,))
    with col2:
        st.markdown(f'<div style="margin-top:10px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col3:
        st.button("▶", key="n_btn", on_click=move_date, args=(1,))
        
    st.markdown('</div>', unsafe_allow_html=True)

    # 이후 데이터 렌더링 부분은 사용자님의 원본 로직을 그대로 사용하세요.
