import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 앱 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(
    page_title="성의교정 대관 현황(M)", 
    page_icon="🏫", 
    layout="centered"
)

# --- 세션 상태 및 자동 조회 설정 ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = True

# 2. CSS 스타일 (모바일 최적화 레이아웃)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none; line-height: 1.2 !important;
    }
    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 4px; }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 25px !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important; font-weight: bold !important; 
        border-right: 1px solid #F0F0F0 !important; font-size: 13px !important;
    }
    .nav-item:last-child { border-right: none !important; }
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# --- [항상 노출되는 검색 부분] ---
with st.form("search_form"):
    selected_date = st.date_input("조회 날짜", value=st.session_state.target_date)
    
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    
    # 2번째 이미지처럼 체크박스 나열
    selected_bu_list = []
    cols = st.columns(1) # 모바일 대응 한 줄 나열
    for b in ALL_BU:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}"):
            selected_bu_list.append(b)
    
    st.markdown('**🗓️ 대관 유형**')
    c1, c2 = st.columns(2)
    show_t = c1.checkbox("당일", value=True, key="chk_t")
    show_p = c2.checkbox("기간", value=True, key="chk_p")
    
    submit = st.form_submit_button("🔍 검색", use_container_width=True)
    if submit:
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True

# --- [슬라이딩으로 접었다 폈다 하는 링크 부분] ---
with st.expander("🔗 빠른 링크 바로가기", expanded=False):
    st.markdown(f"""
        <div style="line-height: 2.5; font-size: 15px;">
            <a href="https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do" target="_blank" style="text-decoration: none; color: #1E3A5F; font-weight: bold;">🏫 성의교정 대관신청현황</a><br>
            <a href="https://scube.s-tec.co.kr/sso/user/login/view" target="_blank" style="text-decoration: none; color: #1E3A5F; font-weight: bold;">🔐 S-CUBE 통합인증(SSO)</a><br>
            <a href="https://pms.s-tec.co.kr/mainfrm.php" target="_blank" style="text-decoration: none; color: #1E3A5F; font-weight: bold;">📂 S-tec 개인정보관리</a><br>
            <a href="https://www.onsafe.co.kr/" target="_blank" style="text-decoration: none; color: #1E3A5F; font-weight: bold;">📖 온세이프(법정교육)</a><br>
            <a href="https://todayshift.com/" target="_blank" style="text-decoration: none; color: #1E3A5F; font-weight: bold;">📅 오늘근무(교대달력)</a>
        </div>
    """, unsafe_allow_html=True)

# --- 데이터 처리 및 출력 로직 ---
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

if st.session_state.search_performed:
    d = st.session_state.target_date
    df_raw = get_data(d)
    
    # 날짜 표시 네비게이션바 (이전/오늘/다음)
    prev_d, next_d, today_d = (d - timedelta(1)), (d + timedelta(1)), today_kst()
    w_idx = d.weekday()
    w_str, w_class = ['월','화','수','목','금','토','일'][w_idx], ("sat" if w_idx == 5 else ("sun" if w_idx == 6 else ""))

    st.markdown(f"""
    <div class="date-display-box" style="margin-top:20px;">
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    """, unsafe_allow_html=True)

    # 대관 내역 반복 출력 (올려주신 디자인 형태)
    target_wd = str(d.weekday() + 1)
    for bu in selected_bu_list:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # ... (이후 데이터 출력 로직은 동일) ...
        # [중략된 출력 코드는 위에서 드린 로직과 동일하게 작동합니다]
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                # 당일/기간 필터링 및 출력
                for title, ev_df in [("📌 당일 대관", bu_df[bu_df['startDt'] == bu_df['endDt']] if show_t else pd.DataFrame()), 
                                     ("🗓️ 기간 대관", bu_df[bu_df['startDt'] != bu_df['endDt']] if show_p else pd.DataFrame())]:
                    if not ev_df.empty:
                        st.write(f"**{title}**")
                        for _, row in ev_df.iterrows():
                            st.markdown(f'<div class="event-card">📍 {row["placeNm"]}<br>⏰ {row["startTime"]}~{row["endTime"]}<br>📄 {row["eventNm"]}</div>', unsafe_allow_html=True)
            else:
                st.write("내역 없음")

# 하단 TOP 버튼
st.markdown("""<div style="position:fixed; bottom:25px; right:20px; z-index:999;"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white; width:45px; height:45px; line-height:45px; text-align:center; border-radius:50%; font-size:12px; font-weight:bold; text-decoration:none; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)
