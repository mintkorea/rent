import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 2. 세션 상태 초기화 (날짜 및 검색 상태)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 3. 화살표 클릭 시 날짜 가감 로직 (가장 정확한 방식)
params = st.query_params
if "nav" in params:
    nav_val = params["nav"]
    if nav_val == "prev":
        st.session_state.target_date -= timedelta(days=1)
    elif nav_val == "next":
        st.session_state.target_date += timedelta(days=1)
    
    st.session_state.search_performed = True
    st.query_params.clear()  # 파라미터 초기화 (무한루프 방지)
    st.rerun()

# CSS 스타일 (정렬 및 크기 최적화)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 5px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 10px; }
    .date-row { display: flex; align-items: center; justify-content: center; gap: 20px; width: 100%; }
    .nav-arrow { font-size: 35px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .building-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 3px solid #1E3A5F; padding-bottom: 5px; margin-top: 25px; }
    .event-card { border: 1px solid #ddd; border-left: 6px solid #1E3A5F; padding: 12px; border-radius: 8px; margin-top: 10px; background: white; }
</style>
""", unsafe_allow_html=True)

# 4. 입력부 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 직접 선택 (세션과 완전 동기화)
st.write("**📅 날짜 직접 선택**")
d_input = st.date_input("날짜선택", value=st.session_state.target_date, label_visibility="collapsed")
if d_input != st.session_state.target_date:
    st.session_state.target_date = d_input
    st.session_state.search_performed = True

# 건물 선택
st.write("**🏢 건물 선택**")
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}")]

# 대관 유형 선택
st.write("**🗓️ 대관 유형 선택**")
col1, col2 = st.columns(2)
with col1: show_today = st.checkbox("당일 대관", value=True)
with col2: show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 5. 결과 출력부
if st.session_state.search_performed:
    curr_d = st.session_state.target_date
    w_idx = curr_d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [메모 반영] 화살표 밀착 박스
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-row">
            <a href="./?nav=prev" target="_self" class="nav-arrow">◀</a>
            <span class="res-sub-title">{curr_d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">▶</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API 데이터 호출
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params_api = {"mode": "getReservedData", "start": curr_d.strftime('%Y-%m-%d'), "end": curr_d.strftime('%Y-%m-%d')}
    
    try:
        res = requests.get(url, params=params_api, timeout=10)
        df = pd.DataFrame(res.json().get('res', []))
    except:
        df = pd.DataFrame()

    if df.empty:
        st.info(f"{curr_d.strftime('%Y-%m-%d')}에 검색 결과가 없습니다.")
    else:
        for bu in selected_bu:
            # 건물명 매칭 (공백 제거 후 포함 여부 확인)
            bu_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            if not bu_df.empty:
                st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
                
                for _, row in bu_df.iterrows():
                    # 유형별 필터링 (당일/기간)
                    is_period = row['startDt'] != row['endDt']
                    if is_period and not show_period: continue
                    if not is_period and not show_today: continue
                    
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="font-weight:bold; color:#1E3A5F; font-size:17px;">📍 {row['placeNm']}</div>
                        <div style="color:#FF4B4B; font-weight:bold;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="margin-top:5px;">📄 {row['eventNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
