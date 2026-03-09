import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화 (날짜 상태 유지의 핵심)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [기능] 날짜 변경 함수 (이걸 거쳐야 화면이 새로고침되면서 바뀝니다)
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (화살표를 버튼으로 만들면서 투명하게 처리)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* 날짜 표시 글씨 */
    .date-text { font-size: 22px !important; font-weight: 700; color: #333; line-height: 1.5; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* [중요] 화살표 버튼을 투명하게 만들어 텍스트처럼 보이게 함 */
    div.stButton > button.arrow-style {
        background: none !important;
        border: none !important;
        color: #1E3A5F !important;
        font-size: 30px !important;
        font-weight: bold !important;
        padding: 0 !important;
        margin: 0 !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }
    
    /* 카드 및 기타 레이아웃 */
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 10px; display: block; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-top: 10px; background-color: #ffffff; position: relative; }
    .status-badge { position: absolute; right: 12px; top: 12px; font-size: 12px; color: #888; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI (날짜 선택 및 검색)
st.markdown('<div style="font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"sel_{b}")]

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 데이터 로딩 함수
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 화면 (화살표 기능 핵심 부분)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 박스 내부 구성
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # [수정] st.columns를 사용하여 화살표와 날짜를 박스 안에서 한 줄로 정렬
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        # 버튼 클래스(arrow-style)를 지정하여 텍스트처럼 보이게 함
        if st.button("⬅️", key="btn_prev", on_click=change_date, args=(-1,)):
            pass 
    with col2:
        st.markdown(f'<div style="text-align:center; padding-top:5px;"><span class="date-text">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col3:
        if st.button("➡️", key="btn_next", on_click=change_date, args=(1,)):
            pass
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 출력 부분 (카드 디자인 유지)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # ... (이후 기존 카드 반복 출력 로직 동일)
        bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)] if not df_raw.empty else pd.DataFrame()
        if bu_df.empty:
            st.markdown('<div style="padding:10px; color:#888;">내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            for _, row in bu_df.iterrows():
                st.markdown(f"""
                <div class="event-card">
                    <span class="status-badge">{row['status']}</span>
                    <div style="font-size: 16px; font-weight: bold; color: #1E3A5F;">📍 {row['placeNm']}</div>
                    <div style="font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 4px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                    <div style="font-size: 14px; color: #333; margin-top: 6px;">📄 {row['eventNm']}</div>
                </div>
                """, unsafe_allow_html=True)
