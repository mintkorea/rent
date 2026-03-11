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

# 세션 상태 초기화 (검색 결과 유지를 위해 필수)
if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# 3. CSS (버튼 가로 정렬 강제 및 디자인 고정)
st.markdown("""
<style>
    /* 상단 앵커 (탑버튼용) */
    #top-anchor { position: absolute; top: -100px; }

    /* [중요] 모바일에서도 버튼 3개를 무조건 가로로 나란히 배치 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        gap: 5px !important;
    }
    [data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
    }
    
    /* 버튼 내부 텍스트 중앙 정렬 및 높이 고정 */
    .stButton > button {
        width: 100% !important;
        height: 40px !important;
        padding: 0px !important;
        border: 1px solid #D1D9E6 !important;
        background-color: white !important;
    }

    /* 날짜 박스 디자인 */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; margin-top: 10px; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 4. 입력부 (상단)
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)

# 날짜 입력 및 건물 선택
st.session_state.target_date = st.date_input("조회 날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
bu_list = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in bu_list if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}")]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_done = True

# 5. 결과 영역 (검색 버튼을 눌렀을 때만 표시)
if st.session_state.search_done:
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]

    # 날짜 헤더
    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)

    # [핵심] 가로로 나란한 화살표 버튼 바
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("◀", key="prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("오늘", key="today"):
            st.session_state.target_date = today_kst()
            st.rerun()
    with c3:
        if st.button("▶", key="next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 로딩 및 카드 출력 부분은 기존 로직을 그대로 사용하시면 됩니다.
    st.write(f"✅ {d.strftime('%Y-%m-%d')} 데이터를 불러오는 중입니다...")

# 6. 플로팅 탑버튼 (자바스크립트 방식)
st.components.v1.html("""
<script>
    const btn = window.parent.document.createElement('button');
    btn.innerHTML = '▲';
    btn.style.cssText = "position:fixed;bottom:25px;right:20px;width:45px;height:45px;border-radius:50%;background:#2E5077;color:white;border:none;z-index:9999;box-shadow:0 3px 10px rgba(0,0,0,0.3);cursor:pointer;";
    btn.onclick = () => window.parent.scrollTo({top:0, behavior:'smooth'});
    if (!window.parent.document.getElementById('float-top-btn')) {
        btn.id = 'float-top-btn';
        window.parent.document.body.appendChild(btn);
    }
</script>
""", height=0)
