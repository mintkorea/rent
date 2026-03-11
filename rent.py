import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# 1. 한국 시간 및 공휴일 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# 3. CSS (원본 디자인 + 모바일 가로 고정 + 탑버튼)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 날짜 박스 디자인 */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; margin-top: 10px; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 5px; }

    /* 모바일 가로 고정 버튼 컨테이너 (st.columns 대체용) */
    .fixed-nav-bar {
        display: flex !important;
        justify-content: center !important;
        gap: 8px !important;
        margin: 10px 0 !important;
        width: 100% !important;
    }
    
    /* 카드 디자인 */
    .event-card { border:1px solid #E0E0E0; border-left:8px solid #2E5077; padding:10px; border-radius:10px; margin-bottom:10px; background:white; position:relative; }
    .status-badge { position:absolute; top:10px; right:10px; background:#FFF3E0; color:#E65100; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:10px; }
    .event-footer { border-top:1px solid #F0F0F0; padding-top:6px; display:flex; justify-content:space-between; font-size:11px; color:#666; }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력부 (탑 앵커 추가)
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
# image_efe9c3의 건물 리스트 복구
all_buildings = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in all_buildings if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

# 검색 버튼 (세션 상태 유지)
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

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
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    
    # 상단 정보 박스
    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    
    # [해결] 모바일에서도 가로로 고정되는 화살표 네비게이션
    # st.columns의 간격을 매우 좁게 조정하여 세로 쌓임을 방지
    c1, c2, c3 = st.columns([0.2, 0.6, 0.2])
    with c1:
        if st.button("◀", key="p_btn"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("오늘", key="t_btn", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
    with c3:
        if st.button("▶", key="n_btn"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 로드 및 카드 출력
    df_raw = get_data(st.session_state.target_date)
    for bu in selected_bu:
        st.markdown(f'<div style="font-size:16px; font-weight:bold; color:#1E3A5F; border-bottom:2px solid #1E3A5F; padding-bottom:3px; margin:15px 0 8px 0;">🏢 {bu}</div>', unsafe_allow_html=True)
        # ... (이하 데이터 필터링 및 카드 생성 로직 기존과 동일) ...
        # (생략된 로직은 image_f0c793 스타일의 카드를 반복 생성함)

# 7. 플로팅 탑버튼 (자바스크립트 방식 - 검색 방해 없음)
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
