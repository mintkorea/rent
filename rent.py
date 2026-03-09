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

# [기능] 날짜 변경 함수 (세션 안전하게 업데이트)
def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. [디자인 수정] 줄간격 축소 + 검색버튼 간격 확대 + 화살표 정렬
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 0.5rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 1. 첫 페이지 요소들 사이의 줄간격(Margin) 대폭 축소 */
    [data-testid="stVerticalBlock"] > div { margin-bottom: -18px !important; }
    
    /* 2. 검색 버튼 하단에 충분한 여백을 주어 타이틀 박스와 분리 */
    div.stButton > button[kind="primary"] { 
        margin-bottom: 35px !important; 
        height: 50px !important;
        font-weight: bold !important;
    }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* 타이틀 박스 디자인 유지 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-top: 10px !important;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 12px; }
    
    /* 3. [화살표 조정] 박스 내부 중앙 정렬 및 디자인 */
    .arrow-wrapper { display: flex; align-items: center; justify-content: space-between; padding: 0 15px; }
    div.stButton > button.arrow-btn {
        background: none !important; border: none !important; 
        font-size: 28px !important; font-weight: bold !important; 
        color: #1E3A5F !important; padding: 0 !important;
    }
    
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; line-height: 1.5; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 17px !important; font-weight: 800; color: #2E5077; display: block; margin-top: 15px !important;}
    
    /* 카드 디자인 (기존 스타일 유지) */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-top: 12px !important; background-color: #ffffff; }
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; }
    .status-badge { float: right; font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: bold; background-color: #F0F2F6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 3. 메인 UI (줄간격이 좁아진 상태)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v4_{b}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today")
show_period = st.checkbox("기간 대관", value=True, key="chk_period")

st.write(" ") # 미세 간격 조정
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (기존 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (화살표를 타이틀 박스 안으로 완벽 통합)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    # [수정] 박스 내부 레이아웃 및 화살표 버튼
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        # ◀ 버튼: 클릭 시 move_date(-1) 실행
        st.button("◀", key="btn_prev", on_click=move_date, args=(-1,))
    with col2:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col3:
        # ▶ 버튼: 클릭 시 move_date(1) 실행
        st.button("▶", key="btn_next", on_click=move_date, args=(1,))
        
    st.markdown('</div>', unsafe_allow_html=True)

    # 건물별 리스팅 (기존 로직 유지)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)] if not df_raw.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div class="no-data-text" style="color:#888; font-size:14px; padding:10px 5px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                if (is_p and show_period) or (not is_p and show_today):
                    st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge">{row['status']}</span>
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:14px; color:#555; margin-top:5px;">📄 {row['eventNm']}</div>
                        </div>
                    """, unsafe_allow_html=True)
