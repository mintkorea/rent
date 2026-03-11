# ... (상단 import 및 기본 세션 설정은 동일하게 유지) ...

# 1. CSS 스타일 (원본 스타일 유지 + 링크 바용 스타일 추가)
st.markdown("""
<style>
    /* [추가] 모바일 가로 고정을 위한 링크 바 스타일 */
    .nav-link-container {
        display: flex !important;
        width: 100% !important;
        background: white !important;
        border: 1px solid #D1D9E6 !important;
        border-radius: 10px !important;
        margin: 15px 0 !important;
        overflow: hidden !important;
    }
    .nav-link-item {
        flex: 1 !important;
        text-align: center !important;
        padding: 12px 0 !important;
        text-decoration: none !important;
        color: #1E3A5F !important;
        font-weight: bold !important;
        border-right: 1px solid #F0F0F0 !important;
        font-size: 14px !important;
    }
    .nav-link-item:last-child { border-right: none !important; }
    .nav-link-item:active { background-color: #F0F4FA !important; }
</style>
""", unsafe_allow_html=True)

# ... (건물 선택 및 검색하기 버튼 등 상단 UI 유지) ...

# 2. 결과 출력 영역 (검색 수행 후)
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [수정 포인트] Before / Today / Next 링크 바 구현
    # 기존의 st.columns([1,2,1]) 부분을 이 코드로 대체하세요.
    prev_d = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    next_d = (d + timedelta(days=1)).strftime("%Y-%m-%d")
    today_d = today_kst().strftime("%Y-%m-%d")
    
    st.markdown(f"""
        <div class="nav-link-container">
            <a href="./?d={prev_d}" target="_self" class="nav-link-item">Before</a>
            <a href="./?d={today_d}" target="_self" class="nav-link-item">Today</a>
            <a href="./?d={next_d}" target="_self" class="nav-link-item">Next</a>
        </div>
    """, unsafe_allow_html=True)

    # [중요] URL 파라미터를 읽어서 세션 날짜를 업데이트하는 로직 (코드 최상단에 추가 권장)
    query_params = st.query_params
    if "d" in query_params:
        target_param = query_params["d"]
        if str(st.session_state.target_date) != target_param:
            st.session_state.target_date = datetime.strptime(target_param, "%Y-%m-%d").date()
            st.rerun()

    # ... (이하 날짜 박스 및 건물별 카드 출력 원본 소스 그대로 사용) ...
