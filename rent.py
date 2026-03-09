import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 2. 세션 상태 초기화 (날짜 고정 및 에러 방지)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# CSS 스타일 (메모의 큰 글씨와 박스 디자인 완벽 반영)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* 결과 박스: 메모 속 사각형 디자인 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 5px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 15px;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 10px; }
    
    /* 날짜와 요일 폰트 크기 */
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 버튼 정렬 및 스타일 */
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    .building-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 3px solid #1E3A5F; padding-bottom: 5px; margin-top: 25px; }
    .event-card { border: 1px solid #ddd; border-left: 6px solid #1E3A5F; padding: 12px; border-radius: 8px; margin-top: 10px; background: white; text-align: left; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 직접 선택
st.write("**📅 날짜 직접 선택**")
d_input = st.date_input("날짜선택", value=st.session_state.target_date, label_visibility="collapsed")
if d_input != st.session_state.target_date:
    st.session_state.target_date = d_input

# 건물 및 유형 선택 (상태 유지)
st.write("**🏢 건물 선택**")
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}")]

st.write("**🗓️ 대관 유형 선택**")
col_t1, col_t2 = st.columns(2)
with col_t1: show_today = st.checkbox("당일 대관", value=True, key="t_today")
with col_t2: show_period = st.checkbox("기간 대관", value=True, key="t_period")

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 및 날짜 변경 로직
if st.session_state.search_performed:
    curr_d = st.session_state.target_date
    w_idx = curr_d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [수정] 박스 안에 타이틀, 날짜, 화살표 버튼을 안정적으로 배치
    st.markdown(f'<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span></div>', unsafe_allow_html=True)
    
    # 화살표 버튼을 날짜 양옆에 배치 (클릭 시 1일씩 증감)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("◀ 이전", key="nav_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with nav_col2:
        st.markdown(f'<div style="text-align:center; padding-top:5px;"><span class="res-sub-title">{curr_d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with nav_col3:
        if st.button("다음 ▶", key="nav_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 호출 (에러 방지 처리 강화)
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    api_params = {"mode": "getReservedData", "start": curr_d.strftime('%Y-%m-%d'), "end": curr_d.strftime('%Y-%m-%d')}
    
    try:
        res = requests.get(url, params=api_params, timeout=10)
        # JSON 응답이 올바른지 확인
        if res.status_code == 200 and res.text.strip():
            data = res.json().get('res', [])
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame()
    except:
        df = pd.DataFrame()

    # 결과 필터링 및 출력
    if df.empty:
        st.info(f"📍 {curr_d.strftime('%Y-%m-%d')} 대관 내역이 없습니다.")
    else:
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
                for _, row in bu_df.iterrows():
                    is_period = row['startDt'] != row['endDt']
                    if (is_period and show_period) or (not is_period and show_today):
                        st.markdown(f"""
                        <div class="event-card">
                            <div style="font-weight:bold; color:#1E3A5F; font-size:17px;">📍 {row['placeNm']}</div>
                            <div style="color:#FF4B4B; font-weight:bold;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="margin-top:5px; font-size:14px;">📄 {row['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
