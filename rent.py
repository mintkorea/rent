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

# [화살표 & 링크 로직] 날짜 이동 처리
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": st.session_state.target_date -= timedelta(days=1)
    if params["nav"] == "next": st.session_state.target_date += timedelta(days=1)
    if params["nav"] == "today": st.session_state.target_date = today_kst()
    st.session_state.search_performed = True 
    st.query_params.clear()
    st.rerun()

# 2. CSS 스타일 (어제 소스 유지 + 링크 바 스타일 추가)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* 날짜 박스 상단 곡률 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px 10px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    .date-row { display: flex; align-items: center; justify-content: center; gap: 15px; }
    .nav-arrow { font-size: 32px !important; font-weight: bold; color: #1E3A5F !important; text-decoration: none !important; line-height: 1; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    
    /* [추가] 텍스트 링크 바 (박스 아래 밀착) */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 25px !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 14px !important;
    }
    .nav-item:last-child { border-right: none !important; }

    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; line-height: 1.4 !important; }
    .status-badge { display: inline-block; padding: 1px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 입력 UI (어제 소스 그대로)
st.markdown('<span style="font-size:18px; font-weight:800; color:#2E5077;">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('<span style="font-size:18px; font-weight:800; color:#2E5077;">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"vfinal_{b}")]

st.markdown('<span style="font-size:18px; font-weight:800; color:#2E5077;">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today_final")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_final")

st.write(" ")
st.markdown('<div id="btn-anchor"></div>', unsafe_allow_html=True)
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (어제 소스)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (링크 바 위치 수정 완료)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    # [위치 수정] 날짜 박스 (상단)
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-row">
            <a href="./?nav=prev" target="_self" class="nav-arrow">←</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">→</a>
        </div>
    </div>
    <div class="nav-link-bar">
        <a href="./?nav=prev" target="_self" class="nav-item">Before</a>
        <a href="./?nav=today" target="_self" class="nav-item">Today</a>
        <a href="./?nav=next" target="_self" class="nav-item">Next</a>
    </div>
    """, unsafe_allow_html=True)

    # 스크롤 이동
    components.html(f"<script>var element = window.parent.document.getElementById('btn-anchor'); if (element) {{ element.scrollIntoView({{behavior: 'smooth', block: 'start'}}); }}</script>", height=0)

    target_weekday = str(d.weekday() + 1)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [day.strip() for day in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                
                for ev_df, title in [(t_ev, "📌 당일 대관"), (v_p_ev, "🗓️ 기간 대관")]:
                    if not ev_df.empty:
                        has_bu_content = True
                        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
                        for _, row in ev_df.sort_values(by='startTime').iterrows():
                            s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                            st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div style="font-size:16px; font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div><div style="color:#FF4B4B; font-weight:bold; font-size:15px; margin:4px 0;">⏰ {row['startTime']} ~ {row['endTime']}</div><div style="font-size:14px; color:#333;">📄 {row['eventNm']}</div><div style="font-size:12px; color:#666; margin-top:8px; border-top:1px solid #f0f0f0; padding-top:6px;">👥 {row['mgDeptNm']}</div></div>""", unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div style="color:#999; text-align:center; padding:15px; border:1px dashed #eee; border-radius:8px;">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

st.markdown('<div style="margin-bottom: 100px;"></div>', unsafe_allow_html=True)
st.markdown("""<div style="position:fixed; bottom:25px; right:20px; z-index:999;"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white !important; width:45px; height:45px; line-height:45px; text-align:center; border-radius:50%; font-size:12px; font-weight:bold; text-decoration:none !important; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)
