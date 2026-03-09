import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 세션 상태 초기화 (검색 설정값 유지)
if 'search_active' not in st.session_state:
    st.session_state.search_active = False
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

# URL 파라미터를 통한 날짜 이동 (결과 유지 핵심)
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": st.session_state.target_date -= timedelta(days=1)
    if params["nav"] == "next": st.session_state.target_date += timedelta(days=1)
    st.session_state.search_active = True 
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (메모 그림 완벽 반영: 큰 글씨 + 밀착 화살표)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* 메모의 사각형 박스 디자인 */
    .integrated-box {
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        background-color: #F8FAFF;
        padding: 20px 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .res-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* 화살표와 날짜 밀착 */
    .date-row { display: flex; align-items: center; justify-content: center; gap: 15px; }
    .nav-arrow { font-size: 30px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; }
    .res-date { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: blue; } .sun { color: red; }
    
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 10px; display: block; }
    .building-tag { font-size: 19px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin: 15px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI (대관 유형 선택 포함)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택
d_input = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = d_input

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}")]

st.markdown('<span class="sub-label">📅 대관 유형 선택</span>', unsafe_allow_html=True)
type_today = st.checkbox("당일 대관", value=True)
type_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_active = True

# 4. 검색 결과 출력
if st.session_state.search_active:
    # 검색 위치로 스크롤
    st.markdown('<div id="result-scroll"></div>', unsafe_allow_html=True)
    components.html("<script>window.parent.document.getElementById('result-scroll').scrollIntoView({behavior:'smooth'});</script>", height=0)

    # API 호출 및 필터링
    target_d_str = st.session_state.target_date.strftime('%Y-%m-%d')
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params_api = {"mode": "getReservedData", "start": target_d_str, "end": target_d_str}
    
    try:
        res = requests.get(url, params=params_api, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json().get('res', [])
        
        # [수정] 대관 유형 필터링 로직 추가
        filtered_data = []
        for item in data:
            if not type_today and item.get('gubun') == '당일대관': continue
            if not type_period and item.get('gubun') == '기간대관': continue
            filtered_data.append(item)
        df = pd.DataFrame(filtered_data)
    except:
        df = pd.DataFrame()

    # 요일 표시용
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [요청사항] 메모 그림 완벽 재현 박스
    st.markdown(f"""
    <div class="integrated-box">
        <span class="res-title">성의교정 대관 현황</span>
        <div class="date-row">
            <a href="./?nav=prev" target="_self" class="nav-arrow">←</a>
            <span class="res-date">{d.strftime("%Y.%m.%d")}.<span class="{w_cls}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">→</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 출력
    if df.empty:
        st.info("해당 조건의 대관 정보가 없습니다.")
    else:
        for bu in selected_bu:
            bu_df = df[df['placeNm'].str.contains(bu, na=False)]
            if not bu_df.empty:
                st.markdown(f'<div class="building-tag">🏢 {bu}</div>', unsafe_allow_html=True)
                for _, row in bu_df.iterrows():
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-left:5px solid #2E5077; padding:10px; border-radius:8px; margin-bottom:10px;">
                        <div style="font-weight:bold; color:#d9534f;">📌 {row['gubun']}</div>
                        <div style="font-size:16px; font-weight:bold;">📍 {row['roomNm']}</div>
                        <div style="color:#555;">⏰ {row['startDt']} ~ {row['endDt']}</div>
                        <div style="margin-top:5px;">📄 {row['title']}</div>
                    </div>
                    """, unsafe_allow_html=True)
