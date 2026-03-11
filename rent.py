import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 시간 및 세션 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# https://www.wordreference.com/koen/%EB%8C%80%EC%9D%91 Before/Today/Next 클릭 시 동작
q = st.query_params
if "d" in q:
    try:
        url_d = datetime.strptime(q["d"], "%Y-%m-%d").date()
        if st.session_state.target_date != url_d:
            st.session_state.target_date = url_d
            st.session_state.search_performed = True
            st.rerun()
    except: pass

# 2. CSS 스타일 (링크 바 위치: 날짜 박스 바로 아래)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 날짜 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
        margin-top: 10px;
    }
    /* 링크 바 (날짜 박스 아래 밀착) */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 25px !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 14px !important;
    }
    .nav-item:last-child { border-right: none !important; }

    .res-main-title { font-size: 18px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    
    /* 카드 디자인 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 15px 0 8px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 12px; background: white; line-height: 1.5; }
    .status-badge { display: inline-block; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 3. 입력 UI (날짜, 건물, 대관유형)
t_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
if t_date != st.session_state.target_date:
    st.session_state.target_date = t_date
    st.rerun()

st.markdown('**🏢 건물 선택**')
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
c1, c2 = st.columns(2)
show_today = c1.checkbox("당일 대관", value=True)
show_period = c2.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [위치] 날짜 박스
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    """, unsafe_allow_html=True)

    # [위치] 날짜 박스 바로 아래 링크 바
    p_s, t_s, n_s = (d-timedelta(1)).isoformat(), today_kst().isoformat(), (d+timedelta(1)).isoformat()
    st.markdown(f"""
    <div class="nav-link-bar">
        <a href="./?d={p_s}" target="_self" class="nav-item">Before</a>
        <a href="./?d={t_s}" target="_self" class="nav-item">Today</a>
        <a href="./?d={n_s}" target="_self" class="nav-item">Next</a>
    </div>
    """, unsafe_allow_html=True)

    # [데이터 로직 최적화]
    @st.cache_data(ttl=300)
    def get_data(d_obj):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": d_obj.isoformat(), "end": d_obj.isoformat()}
        try:
            r = requests.get(url, params=params, timeout=10)
            return pd.DataFrame(r.json().get('res', []))
        except: return pd.DataFrame()

    df = get_data(d)
    target_weekday = str(d.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        
        if not df.empty:
            # 필터링 조건 완화: 건물명이 포함만 되어도 추출
            bu_df = df[df['buNm'].str.contains(bu.split()[0], na=False)].copy()
            
            # 당일/기간 분류
            t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
            p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
            v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in str(x))] if not p_ev.empty else pd.DataFrame()

            for ev_df, title in [(t_ev, "📌 당일 대관"), (v_p_ev, "🗓️ 기간 대관")]:
                if not ev_df.empty:
                    has_content = True
                    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
                    for _, row in ev_df.sort_values(by='startTime').iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge {s_cls}">{s_txt}</span>
                            <div style="font-weight:bold; color:#1E3A5F; font-size:16px;">📍 {row['placeNm']}</div>
                            <div style="color:#FF4B4B; font-weight:bold; font-size:15px; margin:4px 0;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:14px; color:#333;">📄 {row['eventNm']}</div>
                            <div style="font-size:12px; color:#666; margin-top:8px; border-top:1px solid #eee; padding-top:4px;">👥 {row.get('mgDeptNm', '정보 없음')}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        if not has_content:
            st.markdown('<div style="color:#999; text-align:center; padding:15px;">조회 내역 없음</div>', unsafe_allow_html=True)

st.markdown('<a href="#" style="position:fixed;bottom:25px;right:20px;width:45px;height:45px;background:#1E3A5F;color:white;border-radius:50%;text-align:center;line-height:45px;text-decoration:none;z-index:999;box-shadow:2px 4px 8px rgba(0,0,0,0.3);font-size:12px;font-weight:bold;">TOP</a>', unsafe_allow_html=True)
