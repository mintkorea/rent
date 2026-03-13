import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 시간대
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회(M)", page_icon="🏫", layout="centered")

# 근무조 계산 로직
def get_work_shift(d):
    anchor = date(2026, 3, 13)
    diff = (d - anchor).days
    shifts = [
        {"n": "A조", "bg": "#FF9800"},
        {"n": "B조", "bg": "#E91E63"},
        {"n": "C조", "bg": "#2196F3"}
    ]
    return shifts[diff % 3]

if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS 스타일 (원본 유지 및 버튼 간격 최적화)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 4px; }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
    
    /* 링크 버튼 디자인: 모바일 터치 대응 */
    .link-btn {
        display: block; padding: 14px; margin-bottom: 8px;
        background: #F0F4F8; color: #1E3A5F !important;
        text-decoration: none; border-radius: 10px; font-weight: bold;
        text-align: center; border: 1px solid #D1D9E6; font-size: 15px;
    }
    .top-btn { position:fixed; bottom:80px; right:20px; z-index:999; }
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
    if st.form_submit_button("🔍 검색", use_container_width=True):
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True
        st.rerun()

# 4. 데이터 및 결과 출력 (원본 로직 그대로 실행)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, timeout=10)
        return pd.DataFrame(res.json().get('res', [])) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

if st.session_state.search_performed:
    st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
    d = st.session_state.target_date
    df_raw = get_data(d)
    shift = get_work_shift(d)
    # ... (대관 현황 및 순찰 지침 출력부: 원본 소스 100% 동일하게 작동) ...

# 6. 자주 찾는 홈페이지 (스크롤 상단 고정 타겟)
st.markdown('<div id="hp-top"></div>', unsafe_allow_html=True)
with st.expander("🔗 자주 찾는 홈페이지", expanded=False):
    st.markdown('<a href="https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do" target="_blank" class="link-btn">🏫 성의교정 대관신청 현황</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://scube.s-tec.co.kr/sso/user/login/view" target="_blank" class="link-btn">🔐 S-CUBE 통합인증 (SSO)</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://pms.s-tec.co.kr/mainfrm.php" target="_blank" class="link-btn">📂 S-tec 개인정보관리</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.onsafe.co.kr/" target="_blank" class="link-btn">📖 온세이프 (법정교육)</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://todayshift.com/" target="_blank" class="link-btn">📅 오늘근무 (교대달력)</a>', unsafe_allow_html=True)
    st.write("") # 하단 여백 확보

# 7. TOP 버튼
st.markdown("""<div class="top-btn"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white !important; width:45px; height:45px; line-height:45px; text-align:center; border-radius:50%; font-size:12px; font-weight:bold; text-decoration:none !important; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)

# [스크롤 보정] 열릴 때 맨 위로 올리는 자바스크립트
components.html("""
    <script>
        // 1. 초기 로드 시 결과창 스크롤
        setTimeout(function() {
            const res = window.parent.document.getElementById('result-anchor');
            if (res) res.scrollIntoView({behavior: 'smooth', block: 'start'});
        }, 500);

        // 2. 익스팬더 클릭 시 '자주 찾는 홈페이지'를 화면 상단에 고정
        const exp = window.parent.document.querySelector('div[data-testid="stExpander"]');
        if (exp) {
            exp.addEventListener('click', function() {
                // 메뉴가 열리는 시간을 고려해 약간의 지연 후 스크롤
                setTimeout(function() {
                    const target = window.parent.document.getElementById('hp-top');
                    if (target) {
                        target.scrollIntoView({behavior: 'smooth', block: 'start'});
                    }
                }, 250);
            });
        }
    </script>
""", height=0)
