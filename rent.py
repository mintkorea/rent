import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 세션 상태 관리
if 'search_active' not in st.session_state:
    st.session_state.search_active = False
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

# 화살표 클릭 시 날짜 변경
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
    .result-container {
        border: 2px solid #D1D9E6; border-radius: 15px; background-color: #F8FAFF;
        padding: 25px 10px; margin-bottom: 20px; text-align: center;
    }
    .res-head { font-size: 26px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 12px; }
    .date-wrapper { display: flex; align-items: center; justify-content: center; gap: 15px; }
    .arrow-btn { font-size: 32px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; }
    .res-date-text { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF; } .sun { color: #FF0000; }
    .bu-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 3px solid #1E3A5F; padding-bottom: 5px; margin-top: 25px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜 선택", value=st.session_state.target_date)

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v6_{b}")]

col_a, col_b = st.columns(2)
with col_a: type_day = st.checkbox("당일 대관", value=True)
with col_b: type_term = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_active = True

# 4. 결과 출력 로직
if st.session_state.search_active:
    st.markdown('<div id="scroll-target"></div>', unsafe_allow_html=True)
    components.html("<script>window.parent.document.getElementById('scroll-target').scrollIntoView({behavior:'smooth'});</script>", height=0)

    target_str = st.session_state.target_date.strftime('%Y-%m-%d')
    api_url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    
    try:
        # API 호출
        res = requests.get(api_url, params={"mode": "getReservedData", "start": target_str, "end": target_str}, timeout=10)
        raw_data = res.json().get('res', [])
        
        # 필터링 로직 강화 (공백 제거 및 키워드 포함 확인)
        final_list = []
        for item in raw_data:
            gubun = item.get('gubun', '').replace(" ", "")
            if not type_day and "당일" in gubun: continue
            if not type_term and "기간" in gubun: continue
            final_list.append(item)
        df = pd.DataFrame(final_list)
    except:
        df = pd.DataFrame()

    # 날짜 박스 출력 (메모 반영)
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    w_color = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

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

    if df.empty:
        st.warning(f"{target_str}에 검색된 데이터가 없습니다. (전체 수신 데이터: {len(raw_data)}건)")
    else:
        for bu in selected_bu:
            # 건물명 매칭 강화
            bu_df = df[df['placeNm'].str.contains(bu.replace(" ", ""), na=False) | df['roomNm'].str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                st.markdown(f'<div class="bu-header">🏢 {bu}</div>', unsafe_allow_html=True)
                for _, row in bu_df.iterrows():
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-left:6px solid #1E3A5F; padding:12px; border-radius:10px; margin-bottom:12px; background:white;">
                        <div style="color:#d9534f; font-weight:bold;">📌 {row['gubun']}</div>
                        <div style="font-size:18px; font-weight:bold;">📍 {row['roomNm']}</div>
                        <div style="color:#666;">⏰ {row['startDt']} ~ {row['endDt']}</div>
                        <div style="margin-top:6px;">📄 {row['title']}</div>
                    </div>
                    """, unsafe_allow_html=True)

