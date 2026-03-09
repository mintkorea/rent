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

# [날짜 변경] on_click 함수
def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (사용자님의 디자인 100% 복구)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* 타이틀 박스 디자인 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* 화살표 버튼 투명 스타일 */
    div.stButton > button {
        background: none !important; border: none !important; 
        font-size: 28px !important; font-weight: bold !important; 
        color: #1E3A5F !important; padding: 0 !important; width: 100% !important; height: auto !important;
    }
    
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; line-height: 1.5; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 10px !important; display: block; }
    
    /* 결과 카드 정렬 디자인 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; position: relative; }
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; margin-bottom: 4px; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-bottom: 4px; }
    .event-name { font-size: 14px; color: #333; line-height: 1.4; }
    .status-badge { position: absolute; top: 12px; right: 12px; padding: 2px 10px; font-size: 12px; border-radius: 12px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

# 3. 메인 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v5_{b}")]

# [복구] 대관 유형 선택 UI
st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c_t1, c_t2 = st.columns(2)
with c_t1: show_today = st.checkbox("당일 대관", value=True, key="chk_today")
with c_t2: show_period = st.checkbox("기간 대관", value=True, key="chk_period")

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로딩 로직 (헤더 추가로 차단 방지)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, params={"mode": "getReservedData", "start": d, "end": d}, headers=headers, timeout=10)
        if res.status_code == 200 and res.text.strip().startswith('{'):
            return pd.DataFrame(res.json().get('res', []))
    except: pass
    return pd.DataFrame()

# 5. 결과 출력 (디자인 및 유형별 필터링 적용)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date.strftime('%Y-%m-%d'))
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 타이틀 박스 내부 화살표 배치
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 4, 1])
    with col_l: st.button("⬅", key="p_btn", on_click=move_date, args=(-1,))
    with col_m: st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col_r: st.button("➡", key="n_btn", on_click=move_date, args=(1,))
    st.markdown('</div>', unsafe_allow_html=True)

    # 필터링 및 정렬 출력
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        found = False
        if not df_raw.empty:
            # 건물명 매칭 (공백 제거 후 비교)
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            for _, row in bu_df.iterrows():
                # [복구] 당일/기간 대관 구분 로직
                is_period = row['startDt'] != row['endDt']
                if (is_period and show_period) or (not is_period and show_today):
                    found = True
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge {s_cls}">{row['status']}</span>
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        
        if not found:
            st.markdown('<div style="color:#888; padding:5px 0 15px 5px;">해당 조건의 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
