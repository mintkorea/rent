import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 날짜 변경 함수
def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일: 줄간격과 버튼 간격만 조정 (카드 디자인은 인라인으로 원복)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [요청 1] 첫 페이지 줄간격 축소 */
    [data-testid="stVerticalBlock"] > div { margin-bottom: -15px !important; }
    
    /* [요청 2] 검색 버튼과 박스 사이 간격 확보 */
    div.stButton > button[kind="primary"] { margin-bottom: 30px !important; }
    
    /* 타이틀 박스 및 화살표 정렬 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; border: 1px solid #D1D9E6; position: relative;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    
    /* 화살표 버튼 투명화 */
    div.stButton > button.arrow-btn {
        background: none !important; border: none !important; color: #1E3A5F !important;
        font-size: 24px !important; padding: 0 !important;
    }
    
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; display: block; margin-top: 10px !important; }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI (첫 화면)
st.markdown('<div style="font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v4_{b}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (화살표 배치 및 카드 디자인 원복)
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    # [수정 3] 타이틀 박스 내부 화살표 정렬
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1: st.button("◀", key="p_btn", on_click=move_date, args=(-1,))
    with c2: st.markdown(f'<div style="margin-top:5px; text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3: st.button("▶", key="n_btn", on_click=move_date, args=(1,))
    st.markdown('</div>', unsafe_allow_html=True)

    # [디자인 복구] 스크린샷 162154 기반 원본 카드 스타일
    for bu in selected_bu:
        st.markdown(f'<div style="font-size: 19px; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 2px solid #2E5077; padding-bottom: 5px;">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)] if not df_raw.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div style="padding:10px; color:#888;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            for _, row in bu_df.iterrows():
                is_p = str(row['startDt']) != str(row['endDt'])
                if (not is_p and show_today) or (is_p and show_period):
                    # 원본 카드 디자인 그대로 구현
                    st.markdown(f"""
                    <div style="border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-top: 10px; background-color: #ffffff; position: relative;">
                        <span style="position: absolute; right: 12px; top: 12px; font-size: 12px; color: #888; font-weight: bold;">{row['status']}</span>
                        <div style="font-size: 16px; font-weight: bold; color: #1E3A5F;">📍 {row['placeNm']}</div>
                        <div style="font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 4px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="font-size: 14px; color: #333; margin-top: 6px;">📄 {row['eventNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
