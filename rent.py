import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화 (기존 소스 유지)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS: 중앙 정렬 및 텍스트 스타일 (기존 카드 디자인은 건드리지 않음)
st.markdown("""
<style>
    .nav-line {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin: 10px 0 20px 0;
    }
    .nav-item {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A5F;
        text-decoration: none;
        cursor: pointer;
    }
    .date-box {
        border: 1px solid #d1d9e6;
        padding: 8px 20px;
        border-radius: 8px;
        background: white;
        text-align: center;
    }
    .sat { color: blue; }
    .sun { color: red; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI (기존 소스 그대로 사용)
st.markdown('### 🏫 성의교정 시설 대관 현황')

# --- 이 부분이 날짜를 바꾸는 링크 버튼입니다 ---
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    if st.button("←", key="prev_day_btn"):
        st.session_state.target_date -= timedelta(days=1)
        st.rerun()
with c2:
    d = st.session_state.target_date
    w = ['월','화','수','목','금','토','일'][d.weekday()]
    st.markdown(f"""
        <div style="text-align:center; padding:8px; border:1px solid #ddd; border-radius:8px;">
            <b style="font-size:16px;">{d.strftime('%Y.%m.%d')}({w})</b>
        </div>
    """, unsafe_allow_html=True)
with c3:
    if st.button("→", key="next_day_btn"):
        st.session_state.target_date += timedelta(days=1)
        st.rerun()

# --- 기존의 건물 선택 및 검색 버튼 (절대 수정 금지 부분) ---
target_date_input = st.date_input("날짜 직접 선택", value=st.session_state.target_date)
st.session_state.target_date = target_date_input

# (이 자리에 기존의 checkbox들과 '🔍 검색하기' 버튼 코드를 그대로 두세요)

# 4. 결과 출력 (기존 로직 그대로)
if st.session_state.search_performed:
    # (기존의 get_data 함수와 데이터 출력 루프 코드를 그대로 사용하세요)
    st.write(f"조회 날짜: {st.session_state.target_date}")
