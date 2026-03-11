import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# 1. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

# 2. 페이지 설정 및 날짜 로직
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()

# URL 파라미터를 이용한 날짜 변경 처리 (HTML 링크 클릭 대응)
params = st.query_params
if "nav" in params:
    nav_type = params["nav"]
    if nav_type == "prev": st.session_state.target_date -= timedelta(days=1)
    elif nav_type == "today": st.session_state.target_date = today_kst()
    elif nav_type == "next": st.session_state.target_date += timedelta(days=1)
    st.query_params.clear() # 파라미터 초기화 후 재실행
    st.rerun()

# 3. CSS (image_ee23a5의 3분할 셀 디자인 및 플로팅 버튼)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 날짜 표시 박스 (원본 디자인) */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; margin-top: 10px; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 5px; }

    /* [해결] HTML 가로 3분할 네비게이션 바 */
    .nav-container {
        display: flex !important;
        width: 100% !important;
        background: white !important;
        border: 1px solid #D1D9E6 !important;
        border-radius: 10px !important;
        margin-bottom: 15px !important;
        overflow: hidden !important;
    }
    .nav-cell {
        flex: 1 !important;
        text-align: center !important;
        padding: 12px 0 !important;
        text-decoration: none !important;
        color: #1E3A5F !important;
        font-weight: bold !important;
        border-right: 1px solid #D1D9E6 !important;
        background-color: #FFFFFF !important;
    }
    .nav-cell:last-child { border-right: none !important; }
    .nav-cell:hover { background-color: #F8FAFC !important; }

    /* 플로팅 탑버튼 스타일 */
    #top-btn {
        position: fixed !important; bottom: 30px !important; right: 20px !important;
        width: 45px !important; height: 45px !important;
        background-color: #2E5077 !important; color: white !important;
        border-radius: 50% !important; text-align: center !important;
        line-height: 45px !important; font-size: 20px !important;
        z-index: 999999 !important; text-decoration: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        display: block !important; border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. 상단 레이아웃 (앵커)
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)

# 5. [수정] HTML 방식의 가로 고정 네비게이션 (image_ee23a5 형태)
st.markdown(f"""
    <div class="nav-container">
        <a href="./?nav=prev" target="_self" class="nav-cell">◀</a>
        <a href="./?nav=today" target="_self" class="nav-cell">오늘</a>
        <a href="./?nav=next" target="_self" class="nav-cell">▶</a>
    </div>
""", unsafe_allow_html=True)

# 6. 날짜 표시 (원본 디자인 복구)
d = st.session_state.target_date
w_str = ['월','화','수','목','금','토','일'][d.weekday()]
st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
st.markdown(f'<div class="date-display-box">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)

# 7. 건물 선택 및 검색 (디자인 유지)
st.markdown('**🏢 건물 선택**')
# (기존의 건물 선택 체크박스 로직 삽입)
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크"] if st.checkbox(b, value=True, key=f"cb_{b}")]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 8. [해결] 플로팅 탑버튼 (iframe 내부에서도 작동하게 구현)
st.components.v1.html("""
    <script>
        const btn = window.parent.document.createElement("button");
        btn.innerHTML = "▲";
        btn.style.cssText = "position:fixed; bottom:30px; right:20px; width:45px; height:45px; background:#2E5077; color:white; border-radius:50%; border:none; font-size:20px; z-index:999999; cursor:pointer; box-shadow:0 4px 10px rgba(0,0,0,0.3);";
        btn.onclick = () => { window.parent.scrollTo({top: 0, behavior: 'smooth'}); };
        if(!window.parent.document.getElementById("top-btn-fixed")) {
            btn.id = "top-btn-fixed";
            window.parent.document.body.appendChild(btn);
        }
    </script>
""", height=0)
