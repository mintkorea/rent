import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 브라우저 및 언어 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(
    page_title="성의교정 대관 현황(M)", 
    page_icon="🏫", 
    layout="centered"
)

# --- 세션 상태 설정 (자동 조회 활성화) ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = True

# 2. CSS 스타일
st.markdown("""
<style>
    .main-title { 
        font-size: 24px !important; 
        font-weight: 800; 
        text-align: center; 
        color: #1E3A5F; 
        padding-top: 10px;
        margin-bottom: 25px !important; 
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 550px !important; }
    
    header[data-testid="stHeader"] { background: rgba(255,255,255,0); }
    
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .nav-link-bar {
        display: flex; width: 100%; background: white; 
        border: 1px solid #D1D9E6; border-radius: 0 0 10px 10px; 
        margin-bottom: 25px; overflow: hidden;
    }
    .nav-item {
        flex: 1; text-align: center; padding: 10px 0;
        text-decoration: none !important; color: #1E3A5F; font-weight: bold; 
        border-right: 1px solid #F0F0F0; font-size: 13px;
    }
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background: #fff; line-height: 1.5; }
    .sat { color: blue !important; }
    .sun { color: red !important; }
</style>
""", unsafe_allow_html=True)

# 메인 제목
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 상단 슬라이딩 링크 바
components.html("""
<style>
    .scroll-container { display: flex; overflow-x: auto; white-space: nowrap; padding: 10px 0; gap: 10px; scrollbar-width: none; -ms-overflow-style: none; }
    .scroll-container::-webkit-scrollbar { display: none; }
    .link-card { display: inline-block; padding: 8px 18px; background: #1E3A5F; color: white !important; border-radius: 20px; text-decoration: none; font-size: 13px; font-weight: bold; }
</style>
<div class="scroll-container">
    <a href="https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do" target="_blank" class="link-card">🏫 대관신청</a>
    <a href="https://scube.s-tec.co.kr/sso/user/login/view" target="_blank" class="link-card">🔐 S-CUBE</a>
    <a href="https://pms.s-tec.co.kr/mainfrm.php" target="_blank" class="link-card">📂 S-tec 관리</a>
    <a href="https://www.onsafe.co.kr/" target="_blank" class="link-card">📖 온세이프</a>
    <a href="https://todayshift.com/" target="_blank" class="link-card">📅 오늘근무</a>
</div>
""", height=60)

# 4. 조회 설정 폼
with st.form("search_form"):
    selected_date = st.date_input("조회 날짜", value=st.session_state.target_date)
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu_list = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]
    
    c1, c2 = st.columns(2)
    show_t = c1.checkbox("당일", value=True)
    show_p = c2.checkbox("기간", value=True)
    
    submit = st.form_submit_button("🔍 검색", use_container_width=True)
    if submit:
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True

# 5. 데이터 가져오기 및 출력
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return pd.DataFrame(res.json().get('res', [])) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

if st.session_state.search_performed:
    d = st.session_state.target_date
    df_raw = get_data(d)
    
    prev_d, next_d, today_d = (d - timedelta(1)).strftime('%Y-%m-%d'), (d + timedelta(1)).strftime('%Y-%m-%d'), today_kst().strftime('%Y-%m-%d')
    w_idx = d.weekday()
    w_str, w_class = ['월','화','수','목','금','토','일'][w_idx], ("sat" if w_idx == 5 else ("sun" if w_idx == 6 else ""))
    
    st.markdown(f"""
    <div class="date-display-box">
        <span style="font-size: 19px; font-weight: bold; color: #1E3A5F;">성과교정 대관 현황</span><br>
        <span style="font-size: 17px; font-weight: bold;">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    <div class="nav-link-bar">
        <a href="./?d={prev_d}" target="_self" class="nav-item">◀ Before</a>
        <a href="./?d={today_d}" target="_self" class="nav-item">Today</a>
        <a href="./?d={next_d}" target="_self" class="nav-item">Next ▶</a>
    </div>
    """, unsafe_allow_html=True)

    target_wd = str(d.weekday() + 1)
    for bu in selected_bu_list:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_t else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_p else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_wd in str(x))] if not p_ev.empty else pd.DataFrame()
                
                for ev_df in [t_ev, v_p_ev]:
                    for _, row in ev_df.iterrows():
                        has_content = True
                        st.markdown(f"""
                        <div class="event-card">
                            <div style="font-size:16px; font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="color:#FF4B4B; font-weight:bold; font-size:15px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:14px; color:#333; font-weight:bold; margin-top:3px;">📄 {row['eventNm']}</div>
                            <div style="font-size:12px; color:#666; border-top:1px solid #eee; margin-top:8px; padding-top:4px;">👥 {row['mgDeptNm']}</div>
                        </div>""", unsafe_allow_html=True)
        if not has_content:
            st.markdown('<div style="color:#999; text-align:center; padding:15px;">내역 없음</div>', unsafe_allow_html=True)

# 6. TOP 버튼
st.markdown("""
<div style="position:fixed; bottom:20px; right:20px; z-index:1000;">
    <a href="#" target="_self" style="
        display:block; width:50px; height:50px; line-height:50px; 
        text-align:center; background:#1E3A5F; color:white !important; 
        border-radius:50%; font-weight:bold; text-decoration:none; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size:13px;
    ">TOP</a>
</div>
""", unsafe_allow_html=True)
