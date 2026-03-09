import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [기능] 날짜 변경 함수
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (원본 카드 디자인 + TOP 버튼 + 애니메이션)
st.markdown("""
<style>
    /* 결과 화면 이동용 앵커 포인트 */
    #result-anchor { position: relative; top: -20px; }
    
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 원본 메인 타이틀 */
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* [성공 디자인] 날짜 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 12px; }
    
    /* 파란색 정사각형 화살표 버튼 */
    div.stButton > button:not([kind="primary"]) {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 22px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 60px !important; height: 45px !important;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; line-height: 45px; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* [원본 복구] 카드 디자인 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-top: 25px; margin-bottom: 12px; }
    .section-title { font-size: 17px; font-weight: bold; color: #333; margin: 15px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 12px; background-color: white; position: relative; }
    .status-badge { position: absolute; top: 12px; right: 12px; background-color: #FFF4E5; color: #B25E09; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; }
    
    /* 원본 카드 텍스트 정렬 */
    .place-name { font-size: 17px; font-weight: bold; color: #1E3A5F; margin-bottom: 5px; }
    .time-row { font-size: 16px; font-weight: bold; color: #FF4B4B; margin-bottom: 5px; }
    .event-name { font-size: 14px; color: #333; line-height: 1.4; }
    .dept-name { font-size: 12px; color: #777; margin-top: 8px; }

    /* TOP 버튼 스타일 */
    .top-btn {
        position: fixed; bottom: 80px; right: 20px; background-color: #1E3A5F;
        color: white !important; width: 45px; height: 45px; border-radius: 50%;
        text-align: center; line-height: 45px; font-weight: bold; font-size: 12px;
        z-index: 999; text-decoration: none; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 3. 입력부 (메인 화면)
st.markdown('<div id="top"></div>', unsafe_allow_html=True) # 맨 위로 가기용 앵커
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.session_state.target_date = st.date_input("날짜 선택", value=st.session_state.target_date)
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]))]
show_today = st.checkbox("📌 당일 대관", value=True)
show_period = st.checkbox("🗓️ 기간 대관", value=True)

# 검색 버튼 및 자동 이동 스크립트
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True
    # 검색 버튼 클릭 시 'result-anchor' 위치로 스크롤 이동
    components.html("""
        <script>
            window.parent.document.getElementById('result-anchor').scrollIntoView({behavior: 'smooth'});
        </script>
    """, height=0)

# 4. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    # 이동 타겟 앵커
    st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
    
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 결과 박스 (성공 디자인)
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("⬅️", key="prev"): change_date(-1); st.rerun()
    with c2:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="next"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 추출 루프 (카드 디자인 복구)
    target_weekday = str(d.weekday() + 1)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)]
            
            # 당일 대관
            if show_today:
                t_df = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not t_df.empty:
                    has_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, r in t_df.iterrows():
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge">예약확정</span>
                            <div class="place-name">📍 {r['placeNm']}</div>
                            <div class="time-row">⏰ {r['startTime']} ~ {r['endTime']}</div>
                            <div class="event-name">📄 {r['eventNm']}</div>
                            <div class="dept-name">👥 {r['mgDeptNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # 기간 대관
            if show_period:
                p_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday, na=False))]
                if not p_df.empty:
                    has_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, r in p_df.iterrows():
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge">예약확정</span>
                            <div class="place-name">📍 {r['placeNm']}</div>
                            <div class="time-row">⏰ {r['startTime']} ~ {r['endTime']}</div>
                            <div class="event-name">📄 {r['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)

        if not has_content:
            st.write("대관 내역이 없습니다.")

    # TOP 버튼 출력
    st.markdown('<a href="#top" class="top-btn">TOP</a>', unsafe_allow_html=True)
