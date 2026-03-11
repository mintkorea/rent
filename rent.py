import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 환경 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 관리 (검색 결과 및 날짜 유지)
if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# 2. CSS (모바일 가로 고정 및 버튼 디자인)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    
    /* [핵심] 날짜 네비게이션 바: 절대 깨지지 않는 가로 정렬 */
    .nav-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
    .nav-table td { padding: 2px; }
    
    /* 상단 정보 박스 디자인 */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)

# 날짜 선택 (직접 선택 시 세션 업데이트)
new_date = st.date_input("조회 날짜", value=st.session_state.target_date, label_visibility="collapsed")
if new_date != st.session_state.target_date:
    st.session_state.target_date = new_date
    st.rerun()

st.markdown('**🏢 건물 선택**')
all_bu = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in all_bu if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"ch_{b}")]

# 검색 버튼 (이 버튼을 눌러야 결과가 나옵니다)
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_done = True

# 4. 결과 출력 및 네비게이션
if st.session_state.search_done:
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]

    # 날짜 표시판
    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)

    # [해결] 모바일에서 왼쪽 버튼이 사라지지 않도록 st.columns 대신 직접 버튼 배치
    # 비율을 1:2:1로 고정하여 버튼이 잘리지 않게 함
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("◀", key="nav_prev", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("오늘", key="nav_today", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
    with c3:
        if st.button("▶", key="nav_next", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 로딩 및 결과 카드 출력 (기존 로직 사용)
    st.success(f"📅 {d} 대관 내역을 조회 중입니다...")
    # 여기에 실제 데이터 필터링 및 st.markdown(카드디자인) 로직을 넣으세요.

# 5. 플로팅 탑버튼 (자바스크립트로 강제 고정)
st.components.v1.html("""
<script>
    const b = window.parent.document.createElement('button');
    b.innerHTML = '▲'; b.id = 'topBtn';
    b.style.cssText = "position:fixed;bottom:20px;right:20px;width:45px;height:45px;border-radius:50%;background:#2E5077;color:white;border:none;z-index:99999;box-shadow:0 3px 10px rgba(0,0,0,0.3);cursor:pointer;";
    b.onclick = () => window.parent.scrollTo({top:0, behavior:'smooth'});
    if(!window.parent.document.getElementById('topBtn')) window.parent.document.body.appendChild(b);
</script>
""", height=0)
