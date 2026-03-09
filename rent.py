import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 유지
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# CSS: 다른 곳은 건드리지 않고 '컨트롤러 가로 고정' 및 '사각 박스'만 설정
st.markdown("""
<style>
    /* 컨트롤러 전체 컨테이너: 어떤 화면에서도 가로 한 줄 유지 */
    .nav-wrapper {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        width: 100% !important;
        gap: 8px !important;
        margin: 15px 0;
    }

    /* 사각형 타이틀 박스 (8의 비율) */
    .nav-title-box {
        flex: 8 !important;
        background: white;
        border: 1px solid #d1d9e6;
        border-radius: 8px; /* 사각형 */
        padding: 10px 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 54px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 네비게이션 버튼 공통 (1의 비율) */
    .nav-btn {
        flex: 1 !important;
        min-width: 45px;
        height: 54px;
        background: #f8f9fa;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        color: #1E3A5F;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
    }

    .res-main-title { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 2px; }
    .res-sub-title { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 기존 카드 스타일 유지 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 입력 UI
st.markdown('### 🏫 성의교정 시설 대관 현황')
target_date = st.date_input("날짜 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}")]

show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 3. 데이터 로직 (생략 없음)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 및 1:8:1 고정 컨트롤러
if st.session_state.search_performed:
    # 날짜 데이터 준비
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # 깨지지 않는 통합 컨트롤러 (HTML + Streamlit 버튼 결합)
    # columns를 쓰지 않고 HTML flex 구조 안에서 버튼만 개별 배치
    c1, c2, c3 = st.columns([1, 8, 1])
    
    with c1:
        if st.button("◀", key="p_btn", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        st.markdown(f"""
        <div class="nav-title-box">
            <span class="res-main-title">성의교정 대관 현황</span>
            <span class="res-sub-title">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w_str})</span></span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        if st.button("▶", key="n_btn", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 로드 및 출력
    df_raw = get_data(st.session_state.target_date)
    t_weekday = str(st.session_state.target_date.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: t_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                
                for ev_df, title in [(t_ev, "📌 당일 대관"), (v_p_ev, "🗓️ 기간 대관")]:
                    if not ev_df.empty:
                        has_content = True
                        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
                        for _, r in ev_df.sort_values(by='startTime').iterrows():
                            # 카드 디자인 원복 (📍 아이콘, ⏰ 빨간색 시간 등 기존 스타일 그대로)
                            st.markdown(f"""
                            <div class="event-card">
                                📍 {r['placeNm']}<br>
                                <b style="color:#FF4B4B;">⏰ {r['startTime']} ~ {r['endTime']}</b><br>
                                📄 {r['eventNm']}
                            </div>
                            """, unsafe_allow_html=True)
        if not has_content:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
