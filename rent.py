import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 초기화
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# CSS 스타일: 1:8:1 비율 강제 및 모바일 줄바꿈 방지
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 핵심: 모바일에서도 무조건 가로 한 줄 유지 */
    .flex-container {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        gap: 5px !important;
        margin: 20px 0;
    }

    /* 사각형 타이틀 박스 (8의 비율) */
    .title-box-fixed {
        flex: 8 !important; /* 비율 8 */
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 10px 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 55px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* 버튼 스타일 (1의 비율) */
    .nav-btn-fixed {
        flex: 1 !important; /* 비율 1 */
        min-width: 45px;
        height: 55px;
        background: #f8f9fa;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-weight: bold;
        color: #1E3A5F;
    }

    .res-main-title { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 2px; }
    .res-sub-title { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 결과 카드 스타일 */
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 8px; background: #fff; line-height: 1.4; }
    .no-data-text { color: #888; font-size: 14px; padding: 15px; text-align: center; border: 1px dashed #ddd; border-radius: 5px; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 검색 UI (기존 로직 유지)
st.markdown('### 🏫 성의교정 시설 대관 현황')
target_date = st.date_input("날짜", value=st.session_state.target_date)
st.session_state.target_date = target_date

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"key_{b}")]

show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 3. 데이터 로직 (생략 없이 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 1:8:1 가로 한 줄 컨트롤러 (가장 중요한 부분)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # 레이아웃 깨짐을 방지하기 위해 columns 대신 단일 row에 배치
    # 화살표 버튼은 Streamlit 버튼의 기능을 위해 투명하게 겹치거나 columns 비율을 고정해야 함
    # 여기서는 columns가 모바일에서 깨지지 않도록 CSS로 강제 조정된 columns를 사용합니다.
    
    col_l, col_m, col_r = st.columns([1, 8, 1])
    
    with col_l:
        if st.button("◀", key="p_btn"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
            
    with col_m:
        st.markdown(f"""
        <div class="title-box-fixed">
            <span class="res-main-title">성의교정 대관 현황</span>
            <span class="res-sub-title">{d.strftime('%Y.%m.%d')}.<span class="{w_class}">({w_str})</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        if st.button("▶", key="n_btn"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 결과 데이터 출력
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
                
                final_ev = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                if not final_ev.empty:
                    has_content = True
                    for _, r in final_ev.iterrows():
                        st.markdown(f'<div class="event-card">📍 {r["placeNm"]}<br><b style="color:#FF4B4B;">⏰ {r["startTime"]} ~ {r["endTime"]}</b><br>📄 {r["eventNm"]}</div>', unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
