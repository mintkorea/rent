import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 관리
if "target_date" not in st.session_state: st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state: st.session_state.search_performed = False

# 2. 스타일 시트 (검색 결과 박스 디자인 강화)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    .sub-label { font-size: 17px; font-weight: 800; color: #2E5077; margin-top: 10px; display: block; }

    /* 결과 박스 디자인 */
    .result-box-container {
        background-color: #F8FAFF;
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .result-title { font-size: 20px; font-weight: 800; color: #1E3A5F; margin-bottom: 10px; display: block; }
    
    /* 요일 색상 */
    .sat { color: #0000FF; } .sun { color: #FF0000; }

    /* 카드 및 내역 없음 스타일 */
    .building-header { font-size: 19px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin: 15px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background: white; line-height: 1.4; }
    .no-data-text { color: #999; font-size: 14px; padding: 15px; text-align: center; background: #fcfcfc; border: 1px dashed #ddd; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 영역
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택 (세션 연동)
st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

# 건물 및 유형 선택
st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}")]

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

st.write("")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직
@st.cache_data(ttl=300)
def get_data(target_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": target_date.strftime('%Y-%m-%d'), "end": target_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 (원하는 디자인 핵심)
if st.session_state.search_performed:
    st.divider()
    
    # [디자인] 검색 결과 타이틀 박스
    st.markdown('<div class="result-box-container"><span class="result-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # 박스 내부 버튼 배치 (컬럼 활용)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("◀", key="prev_btn", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        d = st.session_state.target_date
        w_idx = d.weekday()
        w_str = ['월','화','수','목','금','토','일'][w_idx]
        w_cls = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
        # 요일 색상 적용된 오늘 날짜 버튼 (누르면 오늘로 이동)
        if st.button(f"{d.strftime('%Y.%m.%d')}.({w_str})", key="today_btn", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
    with c3:
        if st.button("▶", key="next_btn", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 가져오기
    df_raw = get_data(st.session_state.target_date)
    target_weekday = str(st.session_state.target_date.weekday() + 1)

    # 건물별 출력 루프
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                # 당일/기간 대관 출력 (간격 1.4 적용된 카드)
                for ev_type, df, label in [("📌 당일 대관", t_ev, ""), ("🗓️ 기간 대관", v_p_ev, "period")]:
                    if not df.empty:
                        has_bu_content = True
                        st.markdown(f'<div class="section-title">{ev_type}</div>', unsafe_allow_html=True)
                        for _, row in df.sort_values(by='startTime').iterrows():
                            s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                            s_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                            st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
