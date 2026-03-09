import streamlit as st
from datetime import datetime, date, timedelta

# 1. 세션 초기화 (기존 로직 유지)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. 날짜 변경 로직 (HTML 링크 클릭 시 작동)
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": st.session_state.target_date -= timedelta(days=1)
    if params["nav"] == "next": st.session_state.target_date += timedelta(days=1)
    st.query_params.clear()
    st.rerun()

# 3. CSS: 타이틀 박스 안에 버튼을 완전히 가두기
st.markdown("""
<style>
    .integrated-title-box {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        padding: 10px;
        width: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 15px 0;
    }
    .nav-arrow {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #1E3A5F !important;
        text-decoration: none !important;
        padding: 0 15px;
        user-select: none;
    }
    .title-content {
        text-align: center;
        flex-grow: 1;
    }
    .main-t { font-size: 15px; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 2px; }
    .sub-t { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 4. 상단 UI (기존 소스 유지)
st.markdown('### 🏫 성의교정 시설 대관 현황')

# (여기에 기존의 date_input, 건물 체크박스, 검색하기 버튼 코드를 그대로 두세요)

# 5. 결과 출력 (타이틀 박스 내부에 화살표 포함)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_list = ['월','화','수','목','금','토','일']
    w_str = w_list[d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # 타이틀 박스 하나 안에 화살표와 날짜를 모두 넣었습니다.
    st.markdown(f"""
    <div class="integrated-title-box">
        <a href="/?nav=prev" target="_self" class="nav-arrow">←</a>
        <div class="title-content">
            <span class="main-t">성의교정 대관 현황</span>
            <span class="sub-t">{d.strftime('%Y.%m.%d')}.<span class="{w_cls}">({w_str})</span></span>
        </div>
        <a href="/?nav=next" target="_self" class="nav-arrow">→</a>
    </div>
    """, unsafe_allow_html=True)

    # --- 데이터 출력 로직 (기존 카드 디자인 📍, ⏰ 등 그대로 사용) ---
