import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# 1. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()

# 버튼 클릭 로직 처리
query_params = st.query_params
if "nav" in query_params:
    nav = query_params["nav"]
    if nav == "prev": st.session_state.target_date -= timedelta(days=1)
    elif nav == "today": st.session_state.target_date = today_kst()
    elif nav == "next": st.session_state.target_date += timedelta(days=1)
    st.query_params.clear()
    st.rerun()

# 3. CSS (원본 디자인 보존 + HTML 버튼바 + 플로팅 탑)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 날짜 박스 디자인 */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; margin-top: 10px; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 5px; }

    /* [해결] HTML 3분할 셀 버튼바 */
    .nav-card-container {
        display: flex !important;
        width: 100% !important;
        background: white !important;
        border: 1px solid #D1D9E6 !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
        overflow: hidden !important;
    }
    .nav-cell {
        flex: 1 !important;
        text-align: center !important;
        padding: 12px 0 !important;
        cursor: pointer !important;
        text-decoration: none !important;
        color: #1E3A5F !important;
        font-weight: bold !important;
        border-right: 1px solid #F0F0F0 !important;
    }
    .nav-cell:last-child { border-right: none !important; }
    .nav-cell:active { background-color: #F0F4FA !important; }

    /* 플로팅 탑버튼 (최상위 레이어 고정) */
    .floating-top-anchor {
        position: fixed !important; bottom: 30px !important; right: 20px !important;
        width: 45px !important; height: 45px !important;
        background-color: #2E5077 !important; color: white !important;
        border-radius: 50% !important; text-align: center !important;
        line-height: 45px !important; font-size: 20px !important;
        z-index: 999999 !important; text-decoration: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. 상단 UI
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)

# 5. [해결] HTML로 만든 가로 3개 셀 (링크 방식)
# 버튼을 누르면 URL 파라미터를 통해 페이지를 새로고침하며 날짜를 바꿉니다.
st.markdown(f"""
    <div class="nav-card-container">
        <a href="./?nav=prev" target="_self" class="nav-cell">◀</a>
        <a href="./?nav=today" target="_self" class="nav-cell">오늘</a>
        <a href="./?nav=next" target="_self" class="nav-cell">▶</a>
    </div>
""", unsafe_allow_html=True)

# 원본 날짜 박스 표시
d = st.session_state.target_date
w_str = ['월','화','수','목','금','토','일'][d.weekday()]
st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
st.markdown(f'<div class="date-display-box">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)

# 6. 나머지 원본 기능 (건물 선택 등)
st.markdown('**🏢 건물 선택**')
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크"] if st.checkbox(b, value=True, key=f"cb_{b}")]

# (데이터 로딩 및 카드 출력 로직은 동일하므로 생략하거나 기존 소스 사용)
st.info("선택하신 날짜의 데이터를 조회 중입니다...")

# 7. 플로팅 탑버튼 (HTML 방식)
st.markdown('<a href="#top" class="floating-top-anchor">▲</a>', unsafe_allow_html=True)
