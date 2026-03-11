import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 세션 초기화
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [무한 이동 로직]
params = st.query_params
if "d" in params:
    try:
        new_date = datetime.strptime(params["d"], "%Y-%m-%d").date()
        if st.session_state.target_date != new_date:
            st.session_state.target_date = new_date
            st.session_state.search_performed = True
            st.rerun()
    except: pass

# 2. CSS 스타일 (디자인 복구 및 줄간격 축소)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 0.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 메인 타이틀 줄간 및 크기 */
    .main-title { font-size: 19px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 10px !important; line-height: 1.2; }
    
    /* 날짜 박스 및 링크 바 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 20px !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 8px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 13px !important;
    }
    .nav-item:last-child { border-right: none !important; }

    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 카드 디자인 복구 및 줄간 축소 */
    .building-header { font-size: 17px !important; font-weight: bold; color: #2E5077; margin-top: 10px; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin-bottom: 10px; }
    .section-title { font-size: 14px; font-weight: bold; color: #555; margin: 8px 0 5px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 10px 12px; border-radius: 5px; margin-bottom: 10px !important; 
        background-color: #ffffff; line-height: 1.2 !important; 
    }
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; margin-bottom: 2px; }
    .time-row { color: #FF4B4B; font-weight: bold; font-size: 14px; margin: 2px 0; }
    .event-name { font-size: 13px; color: #333; margin-top: 3px; }
    
    .bottom-info { 
        font-size: 11px; color: #666; margin-top: 6px; display: flex; 
        justify-content: space-between; border-top: 1px solid #f0f0f0; padding-top: 4px; 
        line-height: 1.1;
    }
    .status-badge { display: inline-block; padding: 1px 6px; font-size: 10px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 입력부
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
if target_date != st.session_state.target_date:
    st.session_state.target_date = target_date
    st.rerun()

st.markdown('**🏢 건물**')
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]

st.markdown('**🗓️ 유형**')
c1, c2 = st.columns(2)
show_t = c1.checkbox("당일", value=True, key="chk_t")
show_p = c2.checkbox("기간", value=True, key="chk_p")

st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직
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
    day_list = [days.get(d.strip()) for d in str(allow_day_str).split(",") if days.get(d.strip())]
    return f"({','.join(day_list)})" if day_list else ""

# 5. 결과 출력
if st.session_state.search_performed:
    components.html("""
        <script>
            var scrollTarget = window.parent.document.getElementById('result-anchor');
            if (scrollTarget) { scrollTarget.scrollIntoView({behavior: 'smooth', block: 'start'}); }
        </script>
    """, height=0)

    d = st.session_state.target_date
    df_raw = get_data(d)
    
    prev_d, next_d = (d - timedelta(1)).strftime('%Y-%m-%d'), (d + timedelta(1)).strftime('%Y-%m-%d')
    today_d = today_kst().strftime('%Y-%m-%d')
    
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    <div class="nav-link-bar">
        <a href="./?d={prev_d}" target="_self" class="nav-item">Before</a>
        <a href="./?d={today_d}" target="_self" class="nav-item">Today</a>
        <a href="./?d={next_d}" target="_self" class="nav-item">Next</a>
    </div>
    """, unsafe_allow_html=True)

    target_wd = str(d.weekday() + 1)
    for bu in selected_bu:
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
                        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
                        for _, row in ev_df.sort_values(by='startTime').iterrows():
                            s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                            day_info = get_weekday_names(row['allowDay']) if title == "🗓️ 기간 대관" else ""
                            period = f"{row['startDt']} ~ {row['endDt']} {day_info}" if title == "🗓️ 기간 대관" else row['startDt']
                            
                            st.markdown(f"""
                            <div class="event-card">
                                <span class="status-badge {s_cls}">{s_txt}</span>
                                <div class="place-name">📍 {row['placeNm']}</div>
                                <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                                <div class="event-name">📄 {row['eventNm']}</div>
                                <div class="bottom-info">
                                    <span>🗓️ {period}</span>
                                    <span>👥 {row['mgDeptNm']}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div style="color:#999; text-align:center; padding:10px; border:1px dashed #eee; font-size:12px;">내역 없음</div>', unsafe_allow_html=True)

st.markdown("""<div style="position:fixed; bottom:25px; right:20px; z-index:999;"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white !important; width:40px; height:40px; line-height:40px; text-align:center; border-radius:50%; font-size:11px; font-weight:bold; text-decoration:none !important; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)
