import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [필수] 세션 상태에 날짜 저장 (이게 있어야 클릭할 때마다 누적 변경됨)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [핵심 로직] 클릭 횟수만큼 날짜가 무한 변경되는 소스
# URL 파라미터를 이용해 전날/다음날을 계속 계산합니다.
params = st.query_params
if "nav" in params:
    if params["nav"] == "prev": 
        st.session_state.target_date -= timedelta(days=1)
    elif params["nav"] == "next": 
        st.session_state.target_date += timedelta(days=1)
    
    # 변경된 날짜로 즉시 검색 결과 표시
    st.session_state.search_performed = True 
    st.query_params.clear() # 파라미터 중복 방지용 삭제
    st.rerun() # 즉시 화면 갱신

# 2. CSS 스타일 (박스 내부 화살표 정렬 성공 버전)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 날짜 표시 박스 디자인 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 25px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* [박스 내부 정렬] 화살표와 날짜를 한 줄에 배치 */
    .date-nav-wrapper {
        display: flex; align-items: center; justify-content: center; gap: 20px;
    }
    /* 성공했던 텍스트 링크형 화살표 스타일 */
    .nav-arrow { 
        font-size: 32px !important; font-weight: bold; color: #1E3A5F !important; 
        text-decoration: none !important; cursor: pointer;
    }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 입력부
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 날짜 선택기도 세션과 동기화하여 수동 선택 시에도 작동하게 함
st.session_state.target_date = st.date_input("날짜 선택", value=st.session_state.target_date, label_visibility="collapsed")

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 (박스 내부 화살표 안착 버전)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [성공했던 그 구조] 화살표 링크를 박스 내 날짜 양옆에 배치
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div class="date-nav-wrapper">
            <a href="./?nav=prev" target="_self" class="nav-arrow">⬅️</a>
            <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
            <a href="./?nav=next" target="_self" class="nav-arrow">➡️</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 안내 문구 (스크린샷 17:45 버전)
    st.info(f"현재 {d.strftime('%Y-%m-%d')} 대관 내역을 조회 중입니다.")
    
    # 이 아래에 원본 카드 출력 로직을 이어서 작성하시면 됩니다.
