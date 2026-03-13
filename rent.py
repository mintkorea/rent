import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 현황(M)", page_icon="🏫", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = True

# 2. CSS 스타일 (간격 제로 최적화)
st.markdown("""
<style>
    /* 전체 여백 조절 */
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 550px !important; }
    header[data-testid="stHeader"] { background: rgba(255,255,255,0); }

    .main-title { 
        font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; 
        margin-bottom: 15px !important; scroll-margin-top: 100px;
    }

    /* 사이드바 링크 */
    .sidebar-link {
        display: block; padding: 12px 15px; margin-bottom: 8px;
        background-color: #F0F4F8; color: #1E3A5F !important;
        text-decoration: none !important; border-radius: 8px; font-weight: bold; font-size: 14px;
    }

    /* 건물 및 카드 통합 스타일 (간격 최소화) */
    .bu-container { margin-bottom: 5px !important; padding: 0 !important; }
    .building-header { 
        font-size: 17px; font-weight: bold; color: #2E5077; 
        margin: 5px 0 8px 0 !important;
        border-bottom: 2px solid #2E5077; padding-bottom: 3px; 
    }
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 10px; border-radius: 5px; margin-bottom: 5px !important; 
        background: #fff; line-height: 1.4;
    }
    .no-data { 
        color: #999; text-align: center; padding: 8px; 
        border: 1px dashed #eee; font-size: 12px; margin-bottom: 10px;
    }

    /* 상단 날짜 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 12px 10px 5px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .nav-link-bar {
        display: flex; width: 100%; background: white; 
        border: 1px solid #D1D9E6; border-radius: 0 0 10px 10px; 
        margin-bottom: 15px; overflow: hidden;
    }
    .nav-item { flex: 1; text-align: center; padding: 8px 0; text-decoration: none !important; color: #1E3A5F; font-weight: bold; font-size: 13px; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* Streamlit 요소 간 강제 간격 제거 */
    div[data-testid="stVerticalBlock"] > div { gap: 0rem !important; padding-top: 0px !important; padding-bottom: 0px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title" id="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 사이드바
with st.sidebar:
    st.markdown("### 🏢 바로가기 메뉴")
    st.markdown("""
        <a href="https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do" target="_blank" class="sidebar-link">🏫 성의교정 대관신청현황</a>
        <a href="https://scube.s-tec.co.kr/sso/user/login/view" target="_blank" class="sidebar-link">🔐 S-CUBE 통합인증(SSO)</a>
        <a href="https://pms.s-tec.co.kr/mainfrm.php" target="_blank" class="sidebar-link">📂 S-tec 개인정보관리</a>
        <a href="https://www.onsafe.co.kr/" target="_blank" class="sidebar-link">📖 온세이프(법정교육)</a>
        <a href="https://todayshift.com/" target="_blank" class="sidebar-link">📅 오늘근무(교대달력)</a>
    """, unsafe_allow_html=True)

# 4. 조회 폼
with st.form("search_form"):
    selected_date = st.date_input("조회 날짜", value=st.session_state.target_date)
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu_list = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]
    
    c1, c2 = st.columns(2)
    show_t = c1.checkbox("당일", value=True, key="chk_t")
    show_p = c2.checkbox("기간", value=True, key="chk_p")
    submit = st.form_submit_button("🔍 검색", use_container_width=True)
    if submit:
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True

# 5. 데이터 처리 및 출력
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
    d = st.session_state.target_date
    df_raw = get_data(d)
    
    prev_d, next_d, today_d = (d - timedelta(1)).strftime('%Y-%m-%d'), (d + timedelta(1)).strftime('%Y-%m-%d'), today_kst().strftime('%Y-%m-%d')
    w_idx = d.weekday()
    w_str, w_class = ['월','화','수','목','금','토','일'][w_idx], ("sat" if w_idx == 5 else ("sun" if w_idx == 6 else ""))
    
    # 상단 날짜 정보
    st.markdown(f"""
    <div class="date-display-box">
        <span style="font-size: 18px; font-weight: bold; color: #1E3A5F;">성의교정 대관 현황</span><br>
        <span style="font-size: 16px; font-weight: bold;">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    <div class="nav-link-bar">
        <a href="./?d={prev_d}" target="_self" class="nav-item">◀ Before</a>
        <a href="./?d={today_d}" target="_self" class="nav-item">Today</a>
        <a href="./?d={next_d}" target="_self" class="nav-item">Next ▶</a>
    </div>
    """, unsafe_allow_html=True)

    target_wd = str(d.weekday() + 1)
    
    # [핵심] 건물별로 루프를 돌며 HTML 통합 출력
    for bu in selected_bu_list:
        bu_html = f'<div class="bu-container"><div class="building-header">🏢 {bu}</div>'
        has_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_t else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_p else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_wd in str(x))] if not p_ev.empty else pd.DataFrame()
                
                for ev_df in [t_ev, v_p_ev]:
                    for _, row in ev_df.iterrows():
                        has_content = True
                        bu_html += f"""
                        <div class="event-card">
                            <div style="font-size:15px; font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="color:#FF4B4B; font-weight:bold; font-size:14px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:13px; color:#333; margin-top:2px;">📄 {row['eventNm']}</div>
                        </div>"""
        
        if not has_content:
            bu_html += '<div class="no-data">내역 없음</div>'
            
        bu_html += "</div>" # bu-container 닫기
        st.markdown(bu_html, unsafe_allow_html=True)

    components.html("""<script>window.parent.document.getElementById('result-anchor').scrollIntoView({behavior: 'smooth', block: 'start'});</script>""", height=0)

# 6. TOP 버튼
st.markdown(f"""
<div style="position:fixed; bottom:25px; right:20px; z-index:1000;">
    <a href="#main-title" target="_self" style="
        display:block; width:50px; height:50px; line-height:50px; 
        text-align:center; background:#1E3A5F; color:white !important; 
        border-radius:50%; font-weight:bold; text-decoration:none; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size:13px;
    ">TOP</a>
</div>
""", unsafe_allow_html=True)
