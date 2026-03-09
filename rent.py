import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화 (상태 유지의 핵심)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS 스타일 (모바일 최적화 및 메모 디자인 반영)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* 메모장에 그려주신 통합 사각형 박스 */
    .date-container-box {
        border: 2px solid #D1D9E6; border-radius: 15px;
        background-color: #F8FAFF; padding: 15px;
        text-align: center; margin-bottom: 10px;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 버튼 스타일 통일 (박스 안에서 흩어지지 않게) */
    div.stButton > button { 
        height: 45px; width: 100%; border-radius: 10px; font-weight: bold;
        border: 1px solid #D1D9E6 !important; background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI (상태 유지)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 직접 선택
d_input = st.date_input("📅 날짜 직접 선택", value=st.session_state.target_date)
if d_input != st.session_state.target_date:
    st.session_state.target_date = d_input

st.write("**🏢 건물 선택**")
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}")]

st.write("**🗓️ 대관 유형**")
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True, key="chk_today")
with c2: show_period = st.checkbox("기간 대관", value=True, key="chk_period")

# 검색 버튼 (한 번 누르면 이후로는 화살표로만 조작 가능)
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 노출 및 화살표 로직 (여기가 가장 중요합니다)
if st.session_state.search_performed:
    curr_d = st.session_state.target_date
    w_idx = curr_d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [디자인] 사각형 박스 안에 모든 요소를 정렬
    st.markdown('<div class="date-container-box">', unsafe_allow_html=True)
    st.markdown(f'<span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # 화살표 버튼 배치 (누를 때마다 세션 날짜를 하루씩 가감)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_l:
        if st.button("◀", key="nav_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with col_m:
        st.markdown(f'<div style="margin-top:8px;"><span class="res-sub-title">{curr_d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col_r:
        if st.button("▶", key="nav_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # [에러 해결] 서버 응답 예외 처리 (JSON 에러 방지)
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    api_params = {"mode": "getReservedData", "start": curr_d.strftime('%Y-%m-%d'), "end": curr_d.strftime('%Y-%m-%d')}
    
    df = pd.DataFrame()
    try:
        res = requests.get(url, params=api_params, timeout=5)
        # 응답이 비어있지 않고 JSON 형식이 맞는지 이중 체크
        if res.status_code == 200 and res.text.strip().startswith('{'):
            json_data = res.json()
            if 'res' in json_data:
                df = pd.DataFrame(json_data['res'])
    except:
        df = pd.DataFrame() # 에러 발생 시 빈 데이터로 처리하여 빨간 박스 방지

    # 결과 출력 (필터링 적용)
    if df.empty:
        st.info(f"📍 {curr_d.strftime('%Y-%m-%d')}에 검색 결과가 없습니다.")
    else:
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                st.markdown(f"#### 🏢 {bu}")
                for _, row in bu_df.iterrows():
                    is_period = row['startDt'] != row['endDt']
                    if (is_period and show_period) or (not is_period and show_today):
                        with st.container(border=True):
                            st.write(f"📍 **{row['placeNm']}**")
                            st.write(f"⏰ {row['startTime']} ~ {row['endTime']}")
                            st.write(f"📄 {row['eventNm']}")
