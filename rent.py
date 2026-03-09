import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 2. 세션 상태 초기화 (날짜 및 검색 유지 핵심)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# CSS 스타일 (메모의 큰 글씨와 정렬 반영)
st.markdown("""
<style>
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 5px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 10px;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 버튼 스타일 조정 */
    div.stButton > button { width: 100%; border-radius: 8px; }
    .nav-btn-container { display: flex; align-items: center; justify-content: center; gap: 10px; }
    
    .building-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 3px solid #1E3A5F; padding-bottom: 5px; margin-top: 25px; }
    .event-card { border: 1px solid #ddd; border-left: 6px solid #1E3A5F; padding: 12px; border-radius: 8px; margin-top: 10px; background: white; text-align: left; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 직접 선택 (세션 상태와 상호작용)
st.write("**📅 날짜 직접 선택**")
d_input = st.date_input("날짜선택", value=st.session_state.target_date, label_visibility="collapsed")
if d_input != st.session_state.target_date:
    st.session_state.target_date = d_input

# 건물 선택
st.write("**🏢 건물 선택**")
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
# 세션 기반으로 체크박스 상태 유지 가능하게 설정
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}")]

# 대관 유형 선택
st.write("**🗓️ 대관 유형 선택**")
col_t1, col_t2 = st.columns(2)
with col_t1: show_today = st.checkbox("당일 대관", value=True, key="type_today")
with col_t2: show_period = st.checkbox("기간 대관", value=True, key="type_period")

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력부 (에러 방지를 위한 내부 버튼 로직)
if st.session_state.search_performed:
    curr_d = st.session_state.target_date
    w_idx = curr_d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [수정] 화살표 버튼 레이아웃 - 컬럼을 사용하여 클릭 횟수만큼 날짜 변경 보장
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span></div>', unsafe_allow_html=True)
    
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav1:
        if st.button("◀ 이전", key="btn_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with col_nav2:
        st.markdown(f"""
            <div style="text-align:center; padding-top:5px;">
                <span class="res-sub-title">{curr_d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            </div>
        """, unsafe_allow_html=True)
    with col_nav3:
        if st.button("다음 ▶", key="btn_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 호출 로직
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    api_params = {"mode": "getReservedData", "start": curr_d.strftime('%Y-%m-%d'), "end": curr_d.strftime('%Y-%m-%d')}
    
    try:
        res = requests.get(url, params=api_params, timeout=10)
        data = res.json().get('res', [])
        df = pd.DataFrame(data)
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        df = pd.DataFrame()

    # 결과 필터링 및 출력
    if df.empty:
        st.info(f"📍 {curr_d.strftime('%Y-%m-%d')} 대관 내역이 없습니다.")
    else:
        for bu in selected_bu:
            # 건물명 공백 제거 후 비교하여 정확도 향상
            bu_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            if not bu_df.empty:
                st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
                
                found_at_least_one = False
                for _, row in bu_df.iterrows():
                    is_period = row['startDt'] != row['endDt']
                    # 유형 필터 적용
                    if (is_period and show_period) or (not is_period and show_today):
                        found_at_least_one = True
                        st.markdown(f"""
                        <div class="event-card">
                            <div style="font-weight:bold; color:#1E3A5F; font-size:17px;">📍 {row['placeNm']}</div>
                            <div style="color:#FF4B4B; font-weight:bold;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="margin-top:5px; font-size:14px; color:#333;">📄 {row['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if not found_at_least_one:
                    st.write("선택한 유형의 대관 내역이 없습니다.")
