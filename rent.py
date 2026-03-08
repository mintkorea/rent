import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [세션 상태 관리] 날짜 변경 시 페이지 상단 이동 방지
if 'search_date' not in st.session_state:
    st.session_state.search_date = date(2026, 3, 12)
if 'triggered' not in st.session_state:
    st.session_state.triggered = False

# 요일 및 근무조 계산 로직
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS: 3개 셀을 하나로 묶어주는 스타일
st.markdown("""
<style>
    /* 1. 컬럼 간 강제 밀착 (gap 제거) */
    [data-testid="stHorizontalBlock"] {
        gap: 0rem !important;
        align-items: stretch !important;
    }
    
    /* 2. 버튼 스타일: 높이를 고정하고 테두리를 타이틀과 연결 */
    .stButton > button {
        border-radius: 0px !important;
        height: 60px !important; /* 타이틀 박스와 동일한 높이 */
        width: 100% !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #F8FAFC !important;
        margin: 0 !important;
    }
    
    /* 왼쪽 버튼: 왼쪽 모서리만 둥글게 */
    div[data-testid="column"]:nth-child(1) button {
        border-top-left-radius: 12px !important;
        border-bottom-left-radius: 12px !important;
    }
    
    /* 오른쪽 버튼: 오른쪽 모서리만 둥글게 */
    div[data-testid="column"]:nth-child(3) button {
        border-top-right-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
    }

    /* 3. 중앙 타이틀 셀 전용 스타일 */
    .title-cell {
        background-color: #F1F5F9;
        border-top: 1px solid #CBD5E1;
        border-bottom: 1px solid #CBD5E1;
        height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# (필터 영역 생략 - 이전과 동일)
st.markdown('### 🏫 성의교정 시설 대관 현황')
# ...

# 4. 결과 출력: 3개의 셀(Column) 생성
if st.session_state.triggered:
    st.write("---")
    curr = st.session_state.search_date
    w_idx = curr.weekday()
    t_color = "#0000FF" if w_idx == 5 else ("#FF0000" if w_idx == 6 else "#1E3A5F")

    # [핵심] 3개의 셀로 분할 (좌버튼 | 타이틀 | 우버튼)
    col1, col2, col3 = st.columns([1, 6, 1])

    with col1: # 첫 번째 셀: 왼쪽 버튼
        if st.button("◀", key="btn_prev"):
            st.session_state.search_date -= timedelta(days=1)
            st.rerun()

    with col2: # 두 번째 셀: 타이틀 텍스트
        st.markdown(f"""
            <div class="title-cell">
                <div style="font-size:14px; font-weight:800; color:#1E3A5F;">📋 성의교정 대관 현황</div>
                <div style="font-size:14px; font-weight:700; color:{t_color};">
                    [{curr.strftime('%Y.%m.%d')}({WEEKDAY_KR[w_idx]}) | {get_shift_group(curr)}]
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3: # 세 번째 셀: 오른쪽 버튼
        if st.button("▶", key="btn_next"):
            st.session_state.search_date += timedelta(days=1)
            st.rerun()
    
    # ... (데이터 출력 로직 생략)
