import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 환경 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- URL 파라미터 및 세션 상태 관리 ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [해결] 링크 클릭 시 날짜 변경 로직
q_params = st.query_params
if "d" in q_params:
    d_str = q_params["d"]
    try:
        url_date = datetime.strptime(d_str, "%Y-%m-%d").date()
        if st.session_state.target_date != url_date:
            st.session_state.target_date = url_date
            st.session_state.search_performed = True
            st.rerun()
    except: pass

# 2. CSS 스타일 (원본 디자인 유지)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 10px !important; 
        margin: 15px 0 !important; overflow: hidden !important;
    }
    .nav-link {
        flex: 1 !important; text-align: center !important; padding: 12px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 14px !important;
    }
    .nav-link:last-child { border-right: none !important; }

    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }

    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; 
        line-height: 1.4 !important; 
    }
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; margin-bottom: 4px; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin: 4px 0; }
    .event-name { font-size: 14px; color: #333; font-weight: 500; margin-top: 6px; }
    .status-badge { display: inline-block; padding: 1px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
    .no-data-text { color: #999; font-size: 14px; padding: 15px; background-color: #fcfcfc; border-radius: 8px; border: 1px dashed #eee; text-align: center; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 3. 입력부 (조회 설정)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('**🏢 건물 선택**')
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]

show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 함수
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

def get_weekday_names(allow_day_str):
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    if not allow_day_str: return ""
    day_list = [days.get(d.strip()) for d in str(allow_day_str).split(",") if days.get(d.strip())]
    return f"({','.join(day_list)})"

# 5. 결과 출력 (반복문 포함)
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # Before Today Next 링크 바
    p_d = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    n_d = (d + timedelta(days=1)).strftime("%Y-%m-%d")
    t_d = today_kst().strftime("%Y-%m-%d")
    st.markdown(f'<div class="nav-link-bar"><a href="./?d={p_d}" target="_self" class="nav-link">Before</a><a href="./?d={t_d}" target="_self" class="nav-link">Today</a><a href="./?d={n_d}" target="_self" class="nav-link">Next</a></div>', unsafe_allow_html=True)

    # 날짜 박스
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    st.markdown(f'<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)

    df_raw = get_data(d)
    target_weekday = str(d.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                if not t_ev.empty:
                    has_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in t_ev.sort_values(by='startTime').iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)
                
                if not v_p_ev.empty:
                    has_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in v_p_ev.sort_values(by='startTime').iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

# 6. TOP 버튼
st.markdown('<a href="#top-anchor" style="position:fixed;bottom:25px;right:20px;width:45px;height:45px;background:#1E3A5F;color:white;border-radius:50%;text-align:center;line-height:45px;text-decoration:none;z-index:999;box-shadow:2px 4px 8px rgba(0,0,0,0.3);font-size:12px;font-weight:bold;">TOP</a>', unsafe_allow_html=True)
