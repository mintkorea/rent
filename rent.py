import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# 1. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()

# 3. CSS (강제 가로 배치 및 플로팅 버튼 최적화)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 원본 디자인 유지 */
    div[data-testid="stVerticalBlock"] > div { padding: 0px !important; margin: 0px !important; }
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; margin-top: 10px; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 5px; }

    /* [핵심] 모바일 강제 가로 정렬 컨테이너 */
    .custom-nav {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 10px !important;
        margin: 15px 0 !important;
        width: 100% !important;
    }
    
    /* 버튼 스타일 (image_f0da7f 디자인 복구) */
    .stButton > button {
        width: 100% !important;
        border: 1px solid #D1D9E6 !important;
        background-color: white !important;
        border-radius: 8px !important;
        height: 42px !important;
        font-weight: 600 !important;
    }

    /* 카드 디자인 유지 */
    .event-card { border:1px solid #E0E0E0; border-left:8px solid #2E5077; padding:10px; border-radius:10px; margin-bottom:10px; background:white; position:relative; }
    .status-badge { position:absolute; top:10px; right:10px; background:#FFF3E0; color:#E65100; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:10px; }

    /* [해결] 플로팅 탑버튼 - 겹침 방지 및 우선순위 최상위 */
    #floating-top-btn {
        position: fixed !important;
        bottom: 30px !important;
        right: 20px !important;
        width: 50px !important;
        height: 50px !important;
        background-color: #2E5077 !important;
        color: white !important;
        border-radius: 50% !important;
        text-align: center !important;
        line-height: 50px !important;
        font-size: 24px !important;
        z-index: 999999 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
        cursor: pointer !important;
        border: none !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력부 (스크롤용 앵커)
st.markdown('<div id="top-point"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 데이터 API
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력
st.markdown('<div id="result-view"></div>', unsafe_allow_html=True)
if st.session_state.get("search_performed"):
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    c_cls = "red-date" if w_idx == 6 or is_holiday(d) else ("blue-date" if w_idx == 5 else "black-date")

    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box {c_cls}">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    
    # [수정] st.columns를 사용하되, CSS 클래스로 강제 가로 배치
    st.markdown('<div class="custom-nav">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3) # 동일 비율 3분할
    with col1:
        if st.button("◀", key="nav_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with col2:
        if st.button("오늘", key="nav_today"):
            st.session_state.target_date = today_kst()
            st.rerun()
    with col3:
        if st.button("▶", key="nav_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    df_raw = get_data(st.session_state.target_date)
    for bu in selected_bu:
        st.markdown(f'<div style="font-size:16px; font-weight:bold; color:#1E3A5F; border-bottom:2px solid #1E3A5F; padding-bottom:3px; margin:15px 0 8px 0;">🏢 {bu}</div>', unsafe_allow_html=True)
        has_any = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ","").str.contains(bu.replace(" ",""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: str(w_idx+1) in [i.strip() for i in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                
                combined = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                if not combined.empty:
                    has_any = True
                    for _, row in combined.iterrows():
                        st.markdown(f"""
                        <div class="event-card">
                            <div class="status-badge">예약확정</div>
                            <div style="font-size:16px; font-weight:800; color:#1E3A5F; margin-bottom:3px;">📍 {row['placeNm']}</div>
                            <div style="font-size:14px; font-weight:700; color:#D32F2F; margin-bottom:3px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:13px; color:#333; margin-bottom:8px;">📄 {row['eventNm']}</div>
                            <div class="event-footer"><span>📅 {row['startDt']}</span><span>👤 {row.get('mgDeptNm', '정보없음')}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_any:
            st.markdown('<div style="color:#999; font-size:12px; padding:15px; text-align:center; background:#FAFAFA; border:1px dashed #DDD; border-radius:10px;">내역 없음</div>', unsafe_allow_html=True)

# 7. [최종] 플로팅 탑버튼 (JS를 통한 확실한 구현)
st.components.v1.html("""
    <script>
        const btn = window.parent.document.createElement("button");
        btn.innerHTML = "▲";
        btn.id = "floating-top-btn";
        btn.onclick = () => { window.parent.document.getElementById("top-point").scrollIntoView({behavior: "smooth"}); };
        
        const style = window.parent.document.createElement("style");
        style.innerHTML = `
            #floating-top-btn {
                position: fixed !important; bottom: 30px !important; right: 20px !important;
                width: 50px !important; height: 50px !important;
                background-color: #2E5077 !important; color: white !important;
                border-radius: 50% !important; border: none !important;
                font-size: 24px !important; z-index: 999999 !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important; cursor: pointer !important;
            }
        `;
        
        // 중복 생성 방지
        if (!window.parent.document.getElementById("floating-top-btn")) {
            window.parent.document.head.appendChild(style);
            window.parent.document.body.appendChild(btn);
        }
    </script>
""", height=0)
