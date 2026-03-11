import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 시간 및 기본 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [핵심] URL 파라미터로 날짜 제어 (버튼 클릭 시 URL이 변경됨)
params = st.query_params
if "d" in params:
    curr_date = datetime.strptime(params["d"], "%Y-%m-%d").date()
else:
    curr_date = today_kst()

# 2. CSS (디자인 복구 및 가로 한 줄 고정)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 3분할 링크 바 디자인 */
    .link-bar {
        display: flex;
        justify-content: space-between;
        background: white;
        border: 1px solid #D1D9E6;
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    .nav-link {
        flex: 1;
        text-align: center;
        padding: 12px 0;
        text-decoration: none !important;
        color: #1E3A5F !important;
        font-weight: bold;
        border-right: 1px solid #F0F0F0;
        font-size: 14px;
    }
    .nav-link:last-child { border-right: none; }
    .nav-link:active { background: #F0F4FA; }

    /* 기존 날짜 박스 디자인 유지 */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 제목 및 네비게이션
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)

# 날짜 계산
prev_d = (curr_date - timedelta(days=1)).strftime("%Y-%m-%d")
next_d = (curr_date + timedelta(days=1)).strftime("%Y-%m-%d")
today_d = today_kst().strftime("%Y-%m-%d")

# [해결] Before / Today / Next 링크 바
st.markdown(f"""
    <div class="link-bar">
        <a href="./?d={prev_d}" target="_self" class="nav-link">Before</a>
        <a href="./?d={today_d}" target="_self" class="nav-link">Today</a>
        <a href="./?d={next_d}" target="_self" class="nav-link">Next</a>
    </div>
""", unsafe_allow_html=True)

# 4. 날짜 정보 표시
w_str = ['월','화','수','목','금','토','일'][curr_date.weekday()]
st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
st.markdown(f'<div class="date-display-box">{curr_date.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)

# 5. 건물 선택 및 검색 (사용자님 원본 로직)
with st.expander("🏢 건물 및 유형 선택", expanded=True):
    bu_list = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관"]
    selected_bu = [b for b in bu_list if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"c_{b}")]
    
    if st.button("🔍 이 날짜로 검색하기", use_container_width=True, type="primary"):
        st.session_state.do_search = True

# 6. 결과 출력 (예시)
if st.session_state.get("do_search"):
    st.info(f"📅 {curr_date} 데이터를 조회하고 있습니다...")
    # 여기에 기존의 데이터 로딩 및 카드 출력 코드를 붙여넣으시면 됩니다.

# 7. 플로팅 탑버튼 (단순 앵커 방식)
st.markdown('<a href="#" style="position:fixed;bottom:20px;right:20px;width:45px;height:45px;background:#2E5077;color:white;border-radius:50%;text-align:center;line-height:45px;text-decoration:none;z-index:999;box-shadow:0 3px 10px rgba(0,0,0,0.3);">▲</a>', unsafe_allow_html=True)
