import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 브라우저 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(
    page_title="성의교정 대관 현황(M)", 
    page_icon="🏫", 
    layout="centered"
)

# --- 세션 상태 설정 ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = True

# 2. CSS 스타일 (제목 가림 방지 및 모바일 최적화)
st.markdown("""
<style>
    /* 1. TOP 버튼 클릭 시 제목이 가려지지 않도록 최상단에 투명 여백 생성 */
    #top-anchor { 
        display: block; 
        position: relative; 
        top: -100px; /* 제목보다 100px 위로 타겟을 잡음 */
        visibility: hidden; 
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; max-width: 550px !important; }
    
    /* Streamlit 기본 헤더가 제목을 가리지 않도록 조정 */
    header[data-testid="stHeader"] { background: rgba(255,255,255,0); }
    
    .main-title { 
        font-size: 24px !important; 
        font-weight: 800; 
        text-align: center; 
        color: #1E3A5F; 
        padding-top: 10px;
        margin-bottom: 25px !important; 
    }
    
    /* 사이드바 링크 스타일 */
    .sidebar-link {
        display: block;
        padding: 12px 15px;
        margin-bottom: 8px;
        background-color: #F0F4F8;
        color: #1E3A5F !important;
        text-decoration: none !important;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        transition: 0.3s;
    }
    .sidebar-link:hover { background-color: #D1D9E6; }

    /* 대관 내역 카드 스타일 */
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
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background: #fff; }
</style>
""", unsafe_allow_html=True)

# TOP 버튼이 가리킬 실제 위치 (보이지 않는 앵커)
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 메인 제목
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 사이드바 (깔끔한 버튼 형태 링크)
with st.sidebar:
    st.markdown("### 🏢 바로가기 메뉴")
    st.markdown(f"""
        <a href="https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do" target="_blank" class="sidebar-link">🏫 대관신청현황</a>
        <a href="https://scube.s-tec.co.kr/sso/user/login/view" target="_blank" class="sidebar-link">🔐 S-CUBE 통합인증</a>
        <a href="https://pms.s-tec.co.kr/mainfrm.php" target="_blank" class="sidebar-link">📂 S-tec 개인정보관리</a>
        <a href="https://www.onsafe.co.kr/" target="_blank" class="sidebar-link">📖 온세이프(법정교육)</a>
        <a href="https://todayshift.com/" target="_blank" class="sidebar-link">📅 오늘근무(교대달력)</a>
    """, unsafe_allow_html=True)

# 4. 메인 조회 폼
with st.form("search_form"):
    selected_date = st.date_input("조회 날짜", value=st.session_state.target_date)
    
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu_list = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]
    
    st.markdown('**🗓️ 대관 유형**')
    c1, c2 = st.columns(2)
    show_t = c1.checkbox("당일", value=True, key="chk_t")
    show_p = c2.checkbox("기간", value=True, key="chk_p")
    
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
    
    # 상단 네비게이션바
    prev_d, next_d, today_d = (d - timedelta(1)).strftime('%Y-%m-%d'), (d + timedelta(1)).strftime('%Y-%m-%d'), today_kst().strftime('%Y-%m-%d')
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    
    st.markdown(f"""
    <div class="date-display-box">
        <span style="font-size: 18px; font-weight: bold;">{d.strftime("%Y.%m.%d")}({w_str}) 대관 현황</span>
    </div>
    <div class="nav-link-bar">
        <a href="./?d={prev_d}" target="_self" class="nav-item">◀ Before</a>
        <a href="./?d={today_d}" target="_self" class="nav-item">Today</a>
        <a href="./?d={next_d}" target="_self" class="nav-item">Next ▶</a>
    </div>
    """, unsafe_allow_html=True)

    # 내역 출력 부분
    target_wd = str(d.weekday() + 1)
    if not selected_bu_list:
        st.info("조회할 건물을 선택해 주세요.")
    else:
        for bu in selected_bu_list:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            has_data = False
            if not df_raw.empty:
                bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
                if not bu_df.empty:
                    # 필터링 로직 (당일/기간)
                    t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_t else pd.DataFrame()
                    p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_p else pd.DataFrame()
                    v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_wd in str(x))] if not p_ev.empty else pd.DataFrame()
                    
                    for ev_df in [t_ev, v_p_ev]:
                        for _, row in ev_df.iterrows():
                            has_data = True
                            st.markdown(f"""
                            <div class="event-card">
                                <div style="font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                                <div style="color:#FF4B4B; font-size:14px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                                <div style="font-size:14px; margin-top:4px;">📄 {row['eventNm']}</div>
                            </div>""", unsafe_allow_html=True)
            if not has_data:
                st.markdown('<div style="color:#999; text-align:center; padding:10px;">내역 없음</div>', unsafe_allow_html=True)

# 6. 최하단 TOP 버튼
st.markdown("""
<div style="position:fixed; bottom:20px; right:20px; z-index:1000;">
    <a href="#top-anchor" target="_self" style="
        display:block; width:50px; height:50px; line-height:50px; 
        text-align:center; background:#1E3A5F; color:white !important; 
        border-radius:50%; font-weight:bold; text-decoration:none; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size:13px;
    ">TOP</a>
</div>
""", unsafe_allow_html=True)
