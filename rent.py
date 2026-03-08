import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 위젯 컨테이너의 패딩과 마진을 직접 타격하여 간격 축소
st.markdown("""
<style>
    /* 전체 레이아웃 및 상단 여백 제거 */
    .block-container { 
        padding: 0.5rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }
    
    /* [핵심] 모든 위젯 컨테이너의 상하 여백을 0으로 강제 고정 */
    [data-testid="stVerticalBlock"] > div {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-bottom: 0.2rem !important; /* 최소한의 구분선 */
    }

    /* 메인 타이틀: 폰트 확대 유지 및 여백 제거 */
    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin: 0 !important;
        padding: 5px 0 !important;
    }

    /* 소제목: 아래 위젯과 바짝 붙임 */
    .sub-label {
        font-size: 18px !important;
        font-weight: 800;
        color: #2E5077;
        margin: 0 !important;
        padding: 2px 0 !important;
        display: block;
    }

    /* 체크박스: 컨테이너 높이 축소 및 폰트 확대 */
    .stCheckbox {
        padding: 0 !important;
        margin: 0 !important;
    }
    .stCheckbox label p { 
        font-size: 18px !important; 
        font-weight: 500 !important;
        margin: 0 !important;
    }
    
    /* 건물명 헤더: 여백을 이전의 절반 이하로 대폭 축소 */
    .building-header { 
        font-size: 20px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin: 10px 0 2px 0 !important; /* 위쪽 여백을 10px로 제한 */
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 2px;
    }

    /* 결과 타이틀 박스 (성공한 디자인 유지) */
    .result-title-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 8px !important;
        text-align: center;
        margin: 10px 0 !important;
    }
    .result-title-text {
        font-size: 20px !important;
        font-weight: 800;
        color: #1E3A5F;
    }

    /* 결과 카드: 카드 사이 간격 초밀착 */
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 6px solid #2E5077; 
        padding: 8px 12px; 
        border-radius: 8px; 
        margin-bottom: 4px !important;
        background-color: #ffffff;
    }
    .card-place { font-size: 18px !important; font-weight: 700; }
    .card-time { font-size: 17px !important; color: #FF4B4B; font-weight: 600; }
    .card-event { font-size: 16px !important; color: #333; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_B = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
for b in ALL_B:
    st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v34_{b}")

st.markdown('<span class="sub-label">🗓️ 대관 유형</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today_34")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_34")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직 (생략)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    p = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=p, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    # 필터 로직 동일
    # ... (중략) ...
    
    st.markdown(f"""
    <div class="result-title-box">
        <span class="result-title-text">
            🏥 성의교정 대관 현황({target_date.strftime("%m/%d")})
        </span>
    </div>
    """, unsafe_allow_html=True)

    # 선택된 건물 리스트 추출 (checkbox key 기반)
    selected_buildings = [b for b in ALL_B if st.session_state.get(f"v34_{b}")]

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        # 결과 카드 출력부 동일
        # ... (중략) ...
