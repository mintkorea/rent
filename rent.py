import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [기능] 클릭 수만큼 날짜 누적 변경
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (스크린샷 기반 정밀 복구)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 타이틀 박스 디자인 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6;
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* 파란색 화살표 버튼 (스크린샷 스타일) */
    div.stButton > button {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 22px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 55px !important; height: 40px !important;
    }

    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* [원본 카드 디자인 핵심] */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 10px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 12px 0 8px 0; }
    
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background-color: #ffffff; position: relative; }
    .status-badge { position: absolute; right: 10px; top: 10px; font-size: 11px; font-weight: bold; padding: 1px 8px; border-radius: 12px; background: #FFF4E5; color: #B25E09; border: 1px solid #FFE0B2; }
    .place-name { font-size: 17px; font-weight: bold; color: #1E3A5F; margin-bottom: 3px; display: flex; align-items: center; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-bottom: 3px; }
    .event-name { font-size: 14px; color: #333; margin-bottom: 8px; }
    
    /* 카드 하단 정보 열 (날짜와 담당부서 좌우 배치) */
    .card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; border-top: 1px solid #f0f0f0; padding-top: 5px; font-size: 13px; color: #666; }
    .footer-date { color: #E91E63; font-weight: 500; }
    .footer-dept { font-weight: 500; }

    /* TOP 버튼 */
    .top-btn { position: fixed; bottom: 120px; right: 15px; background: #1E3A5F; color: white !important; width: 42px; height: 42px; border-radius: 50%; text-align: center; line-height: 42px; font-weight: bold; text-decoration: none; font-size: 11px; z-index: 999; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 3. 입력부 (원본 보존)
st.markdown('<div style="font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"b_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
c_t, c_p = st.columns(2)
with c_t: show_today = st.checkbox("당일 대관", value=True)
with c_p: show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 조회 (캐시 적용)
@st.cache_data(ttl=300)
def fetch_data(target):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": target.strftime('%Y-%m-%d'), "end": target.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    df = fetch_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_str = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
    w_cls = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    # [핵심] 날짜 변경 박스 + 파란 버튼
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1: 
        if st.button("⬅️", key="p"): change_date(-1); st.rerun()
    with c2: 
        st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_cls}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3: 
        if st.button("➡️", key="n"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 카드 디자인 출력
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        b_df = df[df['buNm'].str.contains(bu.replace(" ", ""), na=False)] if not df.empty else pd.DataFrame()
        
        if b_df.empty:
            st.markdown('<div style="color:gray; padding:10px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
            continue

        # 유형별 카드 출력 (📍, ⏰, 📄, 🗓️, 👥 구성)
        def draw_cards(target_df, title_icon, title_text):
            if not target_df.empty:
                st.markdown(f'<div class="section-title">{title_icon} {title_text}</div>', unsafe_allow_html=True)
                for _, r in target_df.iterrows():
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge">{r['status']}</span>
                        <div class="place-name">📍 {r['placeNm']}</div>
                        <div class="time-row">⏰ {r['startTime']} ~ {r['endTime']}</div>
                        <div class="event-name">📄 {r['eventNm']}</div>
                        <div class="card-footer">
                            <span class="footer-date">🗓️ {r['startDt']}</span>
                            <span class="footer-dept">👥 {r['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        if show_today: draw_cards(b_df[b_df['startDt'] == b_df['endDt']], "📌", "당일 대관")
        if show_period: draw_cards(b_df[b_df['startDt'] != b_df['endDt']], "🗓️", "기간 대관")

    st.markdown('<a href="#top-anchor" class="top-btn">TOP</a>', unsafe_allow_html=True)
