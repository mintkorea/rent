import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 시간 함수
KST = ZoneInfo("Asia/Seoul")

def today_kst():
    return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- [중요] URL 파라미터 및 세션 상태 관리 ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()

if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# URL에서 날짜(?d=YYYY-MM-DD) 읽어오기
query_params = st.query_params
if "d" in query_params:
    d_str = query_params["d"]
    try:
        url_date = datetime.strptime(d_str, "%Y-%m-%d").date()
        if st.session_state.target_date != url_date:
            st.session_state.target_date = url_date
            st.session_state.search_performed = True # 링크 클릭 시 자동 검색
            st.rerun()
    except:
        pass

# 2. CSS 스타일 (원본 디자인 유지 + 링크 바 최적화)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* Before Today Next 링크 바 (모바일 가로 고정) */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 10px !important; 
        margin: 15px 0 !important; overflow: hidden !important;
    }
    .nav-link {
        flex: 1 !important; text-align: center !important; padding: 12px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 14px !important;
    }
    .nav-link:last-child { border-right: none !important; }
    .nav-link:active { background-color: #F0F4FA !important; }

    /* 날짜 표시 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* 카드 디자인 */
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
st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 3. 입력부 (날짜 및 건물 선택)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('**🏢 건물 선택**')
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"vfinal_{b}")]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [핵심] Before / Today / Next 링크 생성 (NameError 방지를 위해 내부에서 timedelta 사용)
    p_d = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    n_d = (d + timedelta(days=1)).strftime("%Y-%m-%d")
    t_d = today_kst().strftime("%Y-%m-%d")
    
    st.markdown(f"""
        <div class="nav-link-bar">
            <a href="./?d={p_d}" target="_self" class="nav-link">Before</a>
            <a href="./?d={t_d}" target="_self" class="nav-link">Today</a>
            <a href="./?d={n_d}" target="_self" class="nav-link">Next</a>
        </div>
    """, unsafe_allow_html=True)

    # 날짜 정보 박스
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 로딩 함수
    @st.cache_data(ttl=300)
    def get_data(selected_date):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
        try:
            res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            return pd.DataFrame(res.json().get('res', []))
        except: return pd.DataFrame()

    df_raw = get_data(d)
    
    if not df_raw.empty:
        st.success(f"📅 {d} 조회 결과입니다.")
        # 여기에 카드 반복문 로직을 추가하시면 됩니다.
    else:
        st.info("조회된 내역이 없습니다.")

# 5. TOP 버튼
st.markdown("""<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>""", unsafe_allow_html=True)
