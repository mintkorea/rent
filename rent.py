import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 환경 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- 세션 및 파라미터 제어 ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 네비게이션 버튼(Today 등) 클릭 시 즉시 반영
url_params = st.query_params
if "d" in url_params:
    try:
        url_d = datetime.strptime(url_params["d"], "%Y-%m-%d").date()
        st.session_state.target_date = url_d
        st.session_state.search_performed = True
    except: pass

# 2. CSS 디자인 (사진 image_e0f4e3.png의 UI 반영)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 15px !important; line-height: 1.1 !important; }
    .stCheckbox { margin-top: -10px !important; margin-bottom: -12px !important; }
    
    /* 상단 날짜 박스 */
    .date-display-box { text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none; }
    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 4px; }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 네비게이션 바 */
    .nav-link-bar { display: flex !important; width: 100% !important; background: white !important; border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; margin-bottom: 25px !important; overflow: hidden !important; }
    .nav-item { flex: 1 !important; text-align: center !important; padding: 10px 0 !important; text-decoration: none !important; color: #1E3A5F !important; font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 13px !important; }
    .nav-item:last-child { border-right: none !important; }

    /* 카드 스타일 (아이콘 포함 UI 반영) */
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; background-color: #ffffff; position: relative; }
    .status-badge { position: absolute; top: 12px; right: 14px; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; background-color: #FFF4E5; color: #B25E09; }
    
    .card-row { display: flex; align-items: flex-start; margin-bottom: 4px; line-height: 1.4; }
    .card-icon { margin-right: 8px; font-size: 16px; }
    .card-label { font-size: 14px; font-weight: bold; color: #333; }
    .card-value { font-size: 14px; color: #444; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 입력부
with st.form("search_form"):
    selected_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu_list = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]
    st.markdown('**🗓️ 대관 유형**')
    c1, c2 = st.columns(2)
    show_t, show_p = c1.checkbox("당일", value=True), c2.checkbox("기간", value=True)
    if st.form_submit_button("🔍 검색하기", use_container_width=True):
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True
        st.query_params.clear()
        st.rerun()

# 4. 데이터 로직
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return pd.DataFrame(res.json().get('res', [])) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

def get_weekday_names(allow_day_str):
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    day_list = [days.get(d.strip()) for d in str(allow_day_str).split(",") if days.get(d.strip())]
    return f"({','.join(day_list)})" if day_list else ""

# 5. 결과 출력
if st.session_state.search_performed:
    st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
    components.html("""<script>setTimeout(function(){window.parent.document.getElementById('result-anchor').scrollIntoView({behavior:'smooth',block:'start'});},50);</script>""", height=0)

    d = st.session_state.target_date
    df_raw = get_data(d)
    prev_d, next_d, today_d = (d - timedelta(1)).strftime('%Y-%m-%d'), (d + timedelta(1)).strftime('%Y-%m-%d'), today_kst().strftime('%Y-%m-%d')
    w_idx = d.weekday()
    w_str, w_class = ['월','화','수','목','금','토','일'][w_idx], ("sat" if w_idx == 5 else ("sun" if w_idx == 6 else ""))
    
    st.markdown(f'<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nav-link-bar"><a href="./?d={prev_d}" target="_self" class="nav-item">◀ Before</a><a href="./?d={today_d}" target="_self" class="nav-item">Today</a><a href="./?d={next_d}" target="_self" class="nav-item">Next ▶</a></div>', unsafe_allow_html=True)

    target_wd = str(d.weekday() + 1)
    for bu in selected_bu_list:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_t else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_p else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_wd in [day.strip() for day in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                
                for ev_df, title in [(t_ev, "📌 당일 대관"), (v_p_ev, "🗓️ 기간 대관")]:
                    if not ev_df.empty:
                        has_content = True
                        st.markdown(f'<div style="font-size:15px; font-weight:bold; color:#555; margin:10px 0 6px 0; padding-left:5px; border-left:4px solid #ccc;">{title}</div>', unsafe_allow_html=True)
                        for _, row in ev_df.sort_values(by='startTime').iterrows():
                            day_info = get_weekday_names(row['allowDay']) if title == "🗓️ 기간 대관" else ""
                            date_range = f"{row['startDt']} ~ {row['endDt']} {day_info}"
                            st.markdown(f"""
                            <div class="event-card">
                                <span class="status-badge">예약확정</span>
                                <div class="card-row" style="margin-bottom:8px;"><span class="card-icon">📍</span><span style="font-size:16px; font-weight:bold; color:#1E3A5F;">{row['placeNm']}</span></div>
                                <div class="card-row"><span class="card-icon">⏰</span><span class="card-label">시간:</span>&nbsp;<span style="color:#FF4B4B; font-weight:bold;">{row['startTime']} ~ {row['endTime']}</span></div>
                                <div class="card-row"><span class="card-icon">📅</span><span class="card-label">일정:</span>&nbsp;<span class="card-value">{date_range}</span></div>
                                <div class="card-row"><span class="card-icon">📝</span><span class="card-label">행사:</span>&nbsp;<span class="card-value"><strong>{row['eventNm']}</strong></span></div>
                                <div class="card-row" style="margin-top:4px; border-top:1px solid #f0f0f0; padding-top:4px;"><span class="card-icon">👥</span><span class="card-label">주관:</span>&nbsp;<span class="card-value">{row['mgDeptNm']}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
        if not has_content:
            st.markdown('<div style="color:#999; text-align:center; padding:15px; border:1px dashed #eee; font-size:13px;">내역 없음</div>', unsafe_allow_html=True)

st.markdown("""<div style="position:fixed; bottom:25px; right:20px; z-index:999;"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white !important; width:45px; height:45px; line-height:45px; text-align:center; border-radius:50%; font-size:12px; font-weight:bold; text-decoration:none !important; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)
