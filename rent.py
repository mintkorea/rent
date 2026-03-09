import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [핵심] 클릭하는 만큼 날짜가 계속 누적 변경되는 원본 로직
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": 
        st.session_state.target_date -= timedelta(days=1)
    elif params["nav"] == "next": 
        st.session_state.target_date += timedelta(days=1)
    st.session_state.search_performed = True 
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (화살표 박스 안착용 최적화)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [수정] 박스 내부 정렬용 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* [정렬 핵심] 화살표가 날짜와 한 줄에 나오도록 배치 */
    .date-nav-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 25px; /* 화살표와 날짜 사이 간격 */
    }
    .nav-arrow { font-size: 28px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }

    /* 카드 관련은 기본 형태만 유지 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-top: 15px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 10px; background: #fff; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 3. 입력부
st.markdown('<div style="font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"c_{b}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (박스 내부 화살표 정렬 성공 버전)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [수정] 화살표가 박스 안으로 완벽하게 들어가는 구조
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-nav-wrapper">
            <a href="./?nav=prev" target="_self" class="nav-arrow">⬅️</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">➡️</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 기본 출력 (나중에 사용자님 디자인으로 다시 덮어쓸 부분)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # ... 이하 데이터 출력 로직 ...
