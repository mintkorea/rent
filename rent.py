import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 세션 상태 초기화 (핵심: 검색 수행 여부를 저장)
if 'search_done' not in st.session_state:
    st.session_state.search_done = False
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

# URL 파라미터를 통한 날짜 이동 처리
params = st.query_params
if "nav" in params:
    nav_dir = params["nav"]
    if nav_dir == "prev":
        st.session_state.target_date -= timedelta(days=1)
    elif nav_dir == "next":
        st.session_state.target_date += timedelta(days=1)
    # 날짜를 이동해도 검색 결과가 계속 보이도록 설정
    st.session_state.search_done = True 
    st.query_params.clear()
    st.rerun()

# CSS 설정 (타이틀 확대 및 화살표 밀착)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 28px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* 메모 그림 형태의 통합 박스 */
    .integrated-date-box {
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        background-color: #F8FAFF;
        padding: 20px 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 10px; }
    
    /* 화살표와 날짜 한 줄 밀착 정렬 */
    .date-row { display: flex; align-items: center; justify-content: center; gap: 15px; }
    .nav-link { font-size: 32px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; }
    .res-sub-title { font-size: 21px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF; } .sun { color: #FF0000; }
    
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 10px; display: block; }
</style>
""", unsafe_allow_html=True)

# 2. UI 입력부
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
# 날짜 입력 위젯과 세션 연동
d_input = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = d_input

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}"):
        selected_bu.append(b)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_done = True

# 3. 결과 출력부 (검색이 수행되었거나 화살표를 눌렀을 때만 노출)
if st.session_state.search_done:
    # 데이터 가져오기 로직 (생략 없이 원본 유지)
    target_d = st.session_state.target_date
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params_api = {"mode": "getReservedData", "start": target_d.strftime('%Y-%m-%d'), "end": target_d.strftime('%Y-%m-%d')}
    
    try:
        res = requests.get(url, params=params_api, headers={"User-Agent": "Mozilla/5.0"})
        df_raw = pd.DataFrame(res.json().get('res', []))
    except:
        df_raw = pd.DataFrame()

    # 요일 처리
    w_list = ['월','화','수','목','금','토','일']
    w_idx = target_d.weekday()
    w_str = w_list[w_idx]
    w_cls = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [요청사항 반영] 메모 그림 디자인: 화살표를 날짜와 한 줄로 밀착
    st.markdown(f"""
    <div class="integrated-date-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-row">
            <a href="./?nav=prev" target="_self" class="nav-link">←</a>
            <span class="res-sub-title">{target_d.strftime("%Y.%m.%d")}.<span class="{w_cls}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-link">→</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 건물별 리스트 출력 (이하 원본 코드 로직)
    if not selected_bu:
        st.warning("건물을 하나 이상 선택해주세요.")
    else:
        for bu in selected_bu:
            # (여기에 기존의 건물별 필터링 및 카드 출력 코드를 그대로 넣으시면 됩니다)
            st.markdown(f"#### 🏢 {bu}")
            # ... 데이터 출력 로직 ...
