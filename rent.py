import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 세션 상태 초기화 (날짜와 검색 상태를 메모리에 고정)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [핵심] 화살표 클릭 시 세션 날짜를 직접 계산 (누를 때마다 1일씩 증감)
params = st.query_params
if "nav" in params:
    nav_action = params["nav"]
    if nav_action == "prev":
        st.session_state.target_date -= timedelta(days=1)
    elif nav_action == "next":
        st.session_state.target_date += timedelta(days=1)
    
    # 화살표 클릭 시 검색 결과창을 즉시 노출하도록 설정
    st.session_state.search_performed = True
    st.query_params.clear() # 파라미터 중복 실행 방지
    st.rerun()

# 2. CSS 스타일 (메모 속 큰 글씨 + 화살표 밀착)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    
    /* 결과 박스 디자인 (메모의 사각형) */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* 화살표와 날짜를 한 줄로 밀착시키는 Flexbox */
    .date-row { display: flex; align-items: center; justify-content: center; gap: 20px; } 
    .nav-arrow { font-size: 38px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; line-height: 1; }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 10px !important; display: block; }
    .building-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 3px solid #1E3A5F; padding-bottom: 5px; margin-top: 25px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #1E3A5F; padding: 12px; border-radius: 8px; margin-bottom: 12px; background: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI (입력부)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 위젯 (세션 날짜와 연동되어 화살표 누르면 같이 변함)
st.markdown('<span class="sub-label">📅 날짜 직접 선택</span>', unsafe_allow_html=True)
d_input = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = d_input

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v7_{b}")]

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 4. 결과 출력 및 데이터 로직
if st.session_state.search_performed:
    # 현재 세션에 저장된 날짜 기준 데이터 호출
    d = st.session_state.target_date
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params_api = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    
    try:
        res = requests.get(url, params=params_api, timeout=10)
        df_raw = pd.DataFrame(res.json().get('res', []))
    except:
        df_raw = pd.DataFrame()

    # 요일 설정
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [성공 로직] 메모의 사각형 박스 + 한 줄 밀착 화살표
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-row">
            <a href="./?nav=prev" target="_self" class="nav-arrow">←</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">→</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 출력
    if not selected_bu:
        st.warning("건물을 선택해주세요.")
    elif df_raw.empty:
        st.info(f"{d.strftime('%Y-%m-%d')}에 대관 정보가 없습니다.")
    else:
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
                for _, row in bu_df.iterrows():
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="font-weight:bold; color:#1E3A5F; font-size:17px;">📍 {row['placeNm']}</div>
                        <div style="color:#FF4B4B; font-weight:bold;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="margin-top:5px;">📄 {row['eventNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
