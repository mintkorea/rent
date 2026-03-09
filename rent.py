import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 세션 상태 관리 (검색 결과 증발 방지)
if 'search_active' not in st.session_state:
    st.session_state.search_active = False
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

# 화살표 클릭 시 날짜 변경 로직
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": st.session_state.target_date -= timedelta(days=1)
    if params["nav"] == "next": st.session_state.target_date += timedelta(days=1)
    st.session_state.search_active = True 
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (타이틀 확대 + 화살표 밀착)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 28px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 25px; }
    
    /* 메모 그림의 사각형 결과 박스 */
    .result-container {
        border: 2px solid #D1D9E6;
        border-radius: 15px;
        background-color: #F8FAFF;
        padding: 25px 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .res-head { font-size: 26px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 12px; }
    
    /* 화살표를 날짜와 한 줄로 가깝게 배치 */
    .date-wrapper { display: flex; align-items: center; justify-content: center; gap: 15px; }
    .arrow-btn { font-size: 32px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; }
    .res-date-text { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF; } .sun { color: #FF0000; }
    
    .section-label { font-size: 19px !important; font-weight: 800; color: #2E5077; margin-top: 15px; display: block; }
    .bu-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 3px solid #1E3A5F; padding-bottom: 5px; margin-top: 25px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 직접 선택
st.session_state.target_date = st.date_input("날짜 선택", value=st.session_state.target_date)

st.markdown('<span class="section-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v5_{b}")]

st.markdown('<span class="section-label">✅ 대관 유형</span>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a: type_day = st.checkbox("당일 대관", value=True)
with col_b: type_term = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_active = True

# 4. 결과 출력 로직
if st.session_state.search_active:
    # 검색 시 결과창으로 자동 스크롤
    st.markdown('<div id="scroll-target"></div>', unsafe_allow_html=True)
    components.html("<script>window.parent.document.getElementById('scroll-target').scrollIntoView({behavior:'smooth'});</script>", height=0)

    # 실제 데이터 API 호출
    target_str = st.session_state.target_date.strftime('%Y-%m-%d')
    api_url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params_api = {"mode": "getReservedData", "start": target_str, "end": target_str}
    
    try:
        res = requests.get(api_url, params=params_api, timeout=10)
        raw_data = res.json().get('res', [])
        
        # 유형 필터링 적용 (이 부분이 누락되면 검색 결과가 안 보일 수 있음)
        final_list = []
        for item in raw_data:
            if not type_day and "당일" in item.get('gubun', ''): continue
            if not type_term and "기간" in item.get('gubun', ''): continue
            final_list.append(item)
        df = pd.DataFrame(final_list)
    except:
        df = pd.DataFrame()

    # 요일/색상 설정
    d = st.session_state.target_date
    w_names = ['월','화','수','목','금','토','일']
    w_str = w_names[d.weekday()]
    w_color = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [수정] 메모 그림 디자인 적용 박스
    st.markdown(f"""
    <div class="result-container">
        <span class="res-head">성의교정 대관 현황</span>
        <div class="date-wrapper">
            <a href="./?nav=prev" target="_self" class="arrow-btn">←</a>
            <span class="res-date-text">{d.strftime("%Y.%m.%d")}.<span class="{w_color}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="arrow-btn">→</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 뿌려주기
    if df.empty:
        st.warning("선택하신 날짜와 유형에 해당하는 대관 정보가 없습니다.")
    else:
        for bu in selected_bu:
            bu_df = df[df['placeNm'].str.contains(bu, na=False)]
            if not bu_df.empty:
                st.markdown(f'<div class="bu-header">🏢 {bu}</div>', unsafe_allow_html=True)
                for _, row in bu_df.iterrows():
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-left:6px solid #1E3A5F; padding:12px; border-radius:10px; margin-bottom:12px; background:white;">
                        <div style="color:#d9534f; font-weight:bold; font-size:15px;">📌 {row['gubun']}</div>
                        <div style="font-size:18px; font-weight:bold; margin:4px 0;">📍 {row['roomNm']}</div>
                        <div style="color:#666; font-size:15px;">⏰ {row['startDt']} ~ {row['endDt']}</div>
                        <div style="margin-top:6px; font-size:16px;">📄 {row['title']}</div>
                    </div>
                    """, unsafe_allow_html=True)
