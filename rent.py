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

# [기능] 화살표 클릭 시 날짜 변경 함수
def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# [개선 핵심] CSS 스타일: 간격 및 화살표 디자인 조정
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 1. 첫 페이지 전체적인 요소 간격(줄간) 줄임 */
    [data-testid="stVerticalBlock"] > div { margin-bottom: -15px !important; }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* 2. [수정] 검색 버튼과 타이틀 박스 간격 벌리기 */
    .search-btn-container { margin-bottom: 40px !important; }
    
    /* 타이틀 박스 디자인 유지 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* 3. [수정] 화살표 디자인 조정: 조금 더 굵고 직관적으로 */
    div.stButton > button.date-nav-btn {
        background: none !important; border: none !important; 
        font-size: 36px !important; font-weight: 900 !important; /* 굵기 및 크기 증가 */
        color: #1E3A5F !important; padding: 0 !important; width: auto !important; height: auto !important;
    }
    
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; display: block; margin-top: 10px !important;}
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; line-height: 1.2 !important; }
    .today-card { background-color: #F8FAFF; } 
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 2px; }
    .event-name { font-size: 14px; margin-top: 4px; color: #333; font-weight: 500; }
    .status-badge { display: inline-block; padding: 1px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 입력 요소들의 간격을 줄이기 위해 markdown으로 라벨 표시 후 widget 배치
st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v4_{b}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today_4")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_4")

st.write(" ")
st.markdown('<div id="btn-anchor"></div>', unsafe_allow_html=True)

# [수정 포인트 2] 검색 버튼을 container로 감싸 하단 여백 주기
with st.container():
    st.markdown('<div class="search-btn-container">', unsafe_allow_html=True)
    if st.button("🔍 검색하기", use_container_width=True, type="primary"):
        st.session_state.search_performed = True
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 데이터 로직 (기존 소스 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    formatted_date = d.strftime("%Y.%m.%d")
    
    # [수정 포인트 3] 타이틀 박스 내부 화살표 디자인 및 배치 조정
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        # 사용자 소스 기반으로 help_type="date-nav-btn" 커스텀 스타일 적용
        st.button("◀", key="p_v9", on_click=move_date, args=(-1,), help_type="date-nav-btn")
    with c2:
        st.markdown(f'<div style="margin-top:10px;"><span class="res-sub-title">{formatted_date}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        # 사용자 소스 기반으로 help_type="date-nav-btn" 커스텀 스타일 적용
        st.button("▶", key="n_v9", on_click=move_date, args=(1,), help_type="date-nav-btn")
    st.markdown('</div>', unsafe_allow_html=True)

    # 결과 데이터 렌더링 (기존 소스 스타일 유지)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)] if not df_raw.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                if (is_p and show_period) or (not is_p and show_today):
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    st.markdown(f'<div class="event-card"><span class="status-badge {s_cls}">{row["status"]}</span><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div></div>', unsafe_allow_html=True)
