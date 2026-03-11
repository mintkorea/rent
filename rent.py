import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

url_params = st.query_params
if "d" in url_params:
    try:
        url_d = datetime.strptime(url_params["d"], "%Y-%m-%d").date()
        st.session_state.target_date = url_d
        st.session_state.search_performed = True
    except: pass

st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .stForm { border: 1px solid #D1D9E6 !important; border-radius: 12px !important; padding: 20px !important; }
    .header-box { border: 1px solid #D1D9E6; border-radius: 12px; padding: 15px; text-align: center; background-color: #F8FAFF; margin-bottom: 10px; }
    .header-title { font-size: 22px; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .header-date { font-size: 19px; font-weight: 700; color: #333; }
    .sat { color: #0000FF; } .sun { color: #FF0000; }
    .nav-bar { display: flex; border: 1px solid #D1D9E6; border-radius: 12px; overflow: hidden; margin-bottom: 30px; background: white; }
    .nav-btn { flex: 1; text-align: center; padding: 10px 0; text-decoration: none; color: #1E3A5F; font-weight: bold; font-size: 14px; border-right: 1px solid #D1D9E6; }
    .nav-btn:last-child { border-right: none; }
    .bu-title { font-size: 18px; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 8px; margin: 25px 0 15px 0; }
    .res-card { border: 1px solid #E0E0E0; border-radius: 10px; padding: 15px; margin-bottom: 15px; background: white; position: relative; }
    .res-badge { position: absolute; top: 15px; right: 15px; background: #FFF4E5; color: #B25E09; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .res-place { font-size: 17px; font-weight: 800; color: #1E3A5F; margin-bottom: 8px; }
    .res-info { display: flex; align-items: flex-start; margin-bottom: 4px; font-size: 15px; color: #333; line-height: 1.4; }
    .res-time { color: #FF4B4B; font-weight: bold; }
    .res-dept { font-size: 13px; color: #888; margin-top: 8px; border-top: 1px solid #f0f0f0; padding-top: 8px; display: flex; align-items: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

with st.form("search_form"):
    selected_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu_list = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]
    c1, c2 = st.columns(2)
    show_t, show_p = c1.checkbox("당일", value=True), c2.checkbox("기간", value=True)
    if st.form_submit_button("🔍 검색하기", use_container_width=True):
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True
        st.query_params.clear()
        st.rerun()

@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return pd.DataFrame(res.json().get('res', [])) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

if st.session_state.search_performed:
    st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
    components.html("""<script>setTimeout(function(){window.parent.document.getElementById('result-anchor').scrollIntoView({behavior:'auto',block:'start'});},10);</script>""", height=0)
    d = st.session_state.target_date
    df_raw = get_data(d)
    prev_d, next_d, today_d = (d - timedelta(1)).strftime('%Y-%m-%d'), (d + timedelta(1)).strftime('%Y-%m-%d'), today_kst().strftime('%Y-%m-%d')
    w_str, w_class = ['월','화','수','목','금','토','일'][d.weekday()], ("sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else ""))
    st.markdown(f'<div class="header-box"><span class="header-title">성의교정 대관 현황</span><span class="header-date">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nav-bar"><a href="./?d={prev_d}" target="_self" class="nav-btn">◀ Before</a><a href="./?d={today_d}" target="_self" class="nav-btn">Today</a><a href="./?d={next_d}" target="_self" class="nav-btn">Next ▶</a></div>', unsafe_allow_html=True)
    target_wd = str(d.weekday() + 1)
    for bu in selected_bu_list:
        st.markdown(f'<div class="bu-title">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_t else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_p else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_wd in [day.strip() for day in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                final_df = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                if not final_df.empty:
                    has_content = True
                    for _, row in final_df.iterrows():
                        st.markdown(f"""
                        <div class="res-card">
                            <span class="res-badge">예약확정</span>
                            <div class="res-place">📍 {row['placeNm']}</div>
                            <div class="res-info"><span style="width:25px;">⏰</span><span class="res-time">{row['startTime']} ~ {row['endTime']}</span></div>
                            <div class="res-info"><span style="width:25px;">📄</span><span>{row['eventNm']}</span></div>
                            <div class="res-dept"><span style="width:25px;">👥</span><span>{row['mgDeptNm']}</span></div>
                        </div>""", unsafe_allow_html=True)
        if not has_content:
            st.markdown('<div style="color:#999; text-align:center; padding:15px; border:1px dashed #eee; font-size:13px;">대관 내역 없음</div>', unsafe_allow_html=True)

st.markdown("""<div style="position:fixed; bottom:25px; right:20px; z-index:999;"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white !important; width:45px; height:45px; line-height:45px; text-align:center; border-radius:50%; font-size:12px; font-weight:bold; text-decoration:none !important; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)
