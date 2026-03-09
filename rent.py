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

# 날짜 이동 로직 (링크 클릭 시 세션 유지하며 이동)
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": st.session_state.target_date -= timedelta(days=1)
    if params["nav"] == "next": st.session_state.target_date += timedelta(days=1)
    st.session_state.search_performed = True # 날짜 이동 시에도 결과창 유지
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (글자 크기 키우기 및 날짜 밀착 레이아웃)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 1. 타이틀 글자 크기 확대 */
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    
    /* 2. 날짜와 화살표 밀착 박스 (메모 형태 반영) */
    .integrated-date-box {
        display: flex;
        justify-content: center; /* 중앙 정렬 */
        align-items: center;
        background-color: #F8FAFF;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #D1D9E6;
        gap: 15px; /* 화살표와 날짜 사이 간격 */
    }
    .nav-arrow {
        font-size: 28px !important; /* 화살표 크기 확대 */
        font-weight: bold;
        color: #1E3A5F !important;
        text-decoration: none !important;
        user-select: none;
    }
    .date-content-wrapper { text-align: center; }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; }
    .res-sub-title { font-size: 19px !important; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; }
    .no-data-text { color: #888; font-size: 14px; padding: 10px 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 3. 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date_input = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date_input

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v48_{b}"):
        selected_bu.append(b)

st.write(" ")
# 3. 검색버튼 누르면 결과값 노출을 위해 앵커 설치
st.markdown('<div id="result-scroll-point"></div>', unsafe_allow_html=True)
if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력
if st.session_state.search_performed:
    # 검색 시 해당 위치로 자동 스크롤
    components.html("<script>window.parent.document.getElementById('result-scroll-point').scrollIntoView({behavior:'smooth'});</script>", height=0)
    
    # 데이터 가져오기 (제공하신 get_data 함수 로직)
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params_api = {"mode": "getReservedData", "start": st.session_state.target_date.strftime('%Y-%m-%d'), "end": st.session_state.target_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params_api, headers={"User-Agent": "Mozilla/5.0"})
        df_raw = pd.DataFrame(res.json().get('res', []))
    except: df_raw = pd.DataFrame()

    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [수정] 메모 형태 반영: 화살표를 날짜와 같은 줄에 가깝게 배치
    st.markdown(f"""
    <div class="integrated-date-box">
        <a href="./?nav=prev" target="_self" class="nav-arrow">←</a>
        <div class="date-content-wrapper">
            <span class="res-main-title">성의교정 대관 현황</span>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
        </div>
        <a href="./?nav=next" target="_self" class="nav-arrow">→</a>
    </div>
    """, unsafe_allow_html=True)

    # 건물별 리스트 출력 (제공하신 소스 로직 그대로 유지)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # ... (이후 데이터 필터링 및 카드 출력 코드는 제공하신 원본과 동일하게 작동합니다) ...
        # (편의상 중략하나 실제 적용 시 원본 루프 코드를 그대로 넣으시면 됩니다)
