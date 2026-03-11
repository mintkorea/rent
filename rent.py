import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 세션 초기화
KST = ZoneInfo("Asia/Seoul")

def today_kst():
    return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [핵심] URL 파라미터로 날짜 제어 로직 (버튼 대신 링크 방식)
params = st.query_params
if "d" in params:
    try:
        st.session_state.target_date = datetime.strptime(params["d"], "%Y-%m-%d").date()
        st.session_state.search_performed = True # 링크 클릭 시 자동 검색 효과
    except:
        st.session_state.target_date = today_kst()
elif 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()

if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS 스타일 (기존 스타일 유지 + 링크 바 추가)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* [추가] 가로 3분할 링크 바 디자인 */
    .nav-link-bar {
        display: flex; width: 100%; background: white; 
        border: 1px solid #D1D9E6; border-radius: 10px; 
        margin: 15px 0; overflow: hidden;
    }
    .nav-link {
        flex: 1; text-align: center; padding: 12px 0;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold; border-right: 1px solid #F0F0F0; font-size: 14px;
    }
    .nav-link:last-child { border-right: none; }
    .nav-link:active { background: #F0F4FA; }

    /* 날짜 박스 스타일 유지 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 카드 디자인 유지 */
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; 
        line-height: 1.4 !important; 
    }
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 4px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 입력 UI (건물 선택 등)
st.markdown('**🏢 건물 선택**')
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"vlink_{b}")]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 영역
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [수정] Before / Today / Next 링크 바 생성
    prev_d = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    next_d = (d + timedelta(days=1)).strftime("%Y-%m-%d")
    today_d = today_kst().strftime("%Y-%m-%d")
    
    st.markdown(f"""
        <div class="nav-link-bar">
            <a href="./?d={prev_d}" target="_self" class="nav-link">Before</a>
            <a href="./?d={today_d}" target="_self" class="nav-link">Today</a>
            <a href="./?d={next_d}" target="_self" class="nav-link">Next</a>
        </div>
    """, unsafe_allow_html=True)

    # 날짜 정보 표시
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 로직 (기존 함수 호출)
    @st.cache_data(ttl=300)
    def get_data(selected_date):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
        try:
            res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            return pd.DataFrame(res.json().get('res', []))
        except: return pd.DataFrame()

    df_raw = get_data(d)
    
    # (이하 카드 출력 로직은 기존 소스와 동일하게 유지하시면 됩니다)
    st.write(f"✅ {d.strftime('%Y-%m-%d')} 데이터를 조회 중입니다...")

# 5. TOP 버튼
st.markdown("""<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>""", unsafe_allow_html=True)
