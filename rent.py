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
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# 3. CSS (가로 정렬 강제 및 디자인 복구)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 버튼바 컨테이너: 모바일 강제 가로 정렬 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="column"] {
        flex: 1 !important;
        min-width: 0 !important;
    }
    
    /* 버튼 스타일 조정 */
    button[kind="secondary"] {
        width: 100% !important;
        padding: 0px !important;
        height: 45px !important;
        border: 1px solid #D1D9E6 !important;
    }

    /* 상단 정보 박스 */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; margin-top: 10px; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 5px; }

    /* 카드 디자인 */
    .event-card { border:1px solid #E0E0E0; border-left:8px solid #2E5077; padding:10px; border-radius:10px; margin-bottom:10px; background:white; position:relative; }
    .status-badge { position:absolute; top:10px; right:10px; background:#FFF3E0; color:#E65100; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# 4. 입력부
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
all_bu = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in all_bu if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"c_{b}")]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_done = True

# 5. 데이터 API
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력 영역
if st.session_state.search_done:
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]

    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)

    # [핵심] 모바일에서도 한 줄로 고정되는 버튼바
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀", key="prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with col2:
        if st.button("오늘", key="today"):
            st.session_state.target_date = today_kst()
            st.rerun()
    with col3:
        if st.button("▶", key="next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    df = get_data(st.session_state.target_date)
    # 이후 카드 출력 로직 (기존과 동일)
    if not df.empty:
        for bu in selected_bu:
            st.markdown(f"**🏢 {bu}**")
            # ... 필터링 로직 ...
    else:
        st.write("내역이 없습니다.")

# 7. 플로팅 탑버튼 (자바스크립트로 강제 삽입)
st.components.v1.html("""
<script>
    if (!window.parent.document.getElementById('float-top')) {
        const btn = window.parent.document.createElement('button');
        btn.id = 'float-top';
        btn.innerHTML = '▲';
        btn.style.cssText = "position:fixed;bottom:25px;right:20px;width:45px;height:45px;border-radius:50%;background:#2E5077;color:white;border:none;z-index:9999;box-shadow:0 3px 10px rgba(0,0,0,0.3);cursor:pointer;";
        btn.onclick = () => window.parent.scrollTo({top:0, behavior:'smooth'});
        window.parent.document.body.appendChild(btn);
    }
</script>
""", height=0)
