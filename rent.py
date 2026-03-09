import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [날짜 변경] 에러를 유발하는 모든 부가 옵션을 제거한 핵심 로직
def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (사용자님의 박스 디자인 + 화살표 강제 고정)
st.markdown("""
<style>
    .block-container { padding: 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 15px;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 10px; }
    
    /* 화살표 버튼 위치 강제 고정 */
    div.stButton > button {
        background: none !important; border: none !important; 
        font-size: 26px !important; color: #1E3A5F !important;
        padding: 0px !important; line-height: 1 !important;
    }
    .res-sub-title { font-size: 19px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 결과 카드 디자인 */
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; margin: 15px 0 10px 0; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 8px; background-color: white; }
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 14px; font-weight: bold; color: #FF4B4B; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택기 (세션과 동기화)
d_input = st.date_input("날짜 선택", value=st.session_state.target_date, label_visibility="collapsed")
if d_input != st.session_state.target_date:
    st.session_state.target_date = d_input

# 건물 선택
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
st.write("**🏢 건물 선택**")
cols = st.columns(2)
selected_bu = []
for i, b in enumerate(ALL_BUILDINGS):
    if cols[i % 2].checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}"):
        selected_bu.append(b)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (데이터 못 찾는 문제 해결)
def get_data(target_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    date_str = target_date.strftime('%Y-%m-%d')
    try:
        # User-Agent를 추가하여 서버 차단 방지
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, params={"mode": "getReservedData", "start": date_str, "end": date_str}, headers=headers, timeout=10)
        if res.status_code == 200 and "res" in res.text:
            return pd.DataFrame(res.json().get('res', []))
    except Exception as e:
        st.error(f"데이터 통신 오류: {e}")
    return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    df = get_data(st.session_state.target_date)
    curr_d = st.session_state.target_date
    w_idx = curr_d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [디자인 고정] 박스 레이아웃 내부에 화살표 배치
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c_l, c_m, c_r = st.columns([1, 4, 1])
    with c_l: st.button("⬅", key="btn_prev", on_click=move_date, args=(-1,))
    with c_m: st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{curr_d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c_r: st.button("➡", key="btn_next", on_click=move_date, args=(1,))
    st.markdown('</div>', unsafe_allow_html=True)

    if df.empty:
        st.info(f"📍 {curr_d.strftime('%Y-%m-%d')}에 대관 내역이 없습니다.")
    else:
        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            # 건물명 매칭 로직 강화
            bu_df = df[df['buNm'].str.contains(bu.replace(" ", ""), na=False)]
            if bu_df.empty:
                st.write("대관 내역 없음")
            else:
                for _, row in bu_df.iterrows():
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge status-y">{row['status']}</span>
                        <div class="place-name">📍 {row['placeNm']}</div>
                        <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="font-size:13px; margin-top:5px;">📄 {row['eventNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
