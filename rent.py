import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# ---------------------------------
# 1. 한국 시간 설정 및 초기화
# ---------------------------------
KST = ZoneInfo("Asia/Seoul")

def today_kst():
    return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()

if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# ---------------------------------
# 2. CSS 스타일 (화살표 제거 버전 + 간격 최적화)
# ---------------------------------
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 메인 간격 유지 */
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }

    .main-title {
        font-size: 24px !important; font-weight: 800;
        text-align: center; color: #1E3A5F; margin-bottom: 10px !important; 
    }

    .date-display-box { 
        text-align: center; background-color: #F8FAFF; 
        padding: 15px; border-radius: 12px; margin-bottom: 15px; 
        border: 1px solid #D1D9E6; line-height: 1.5;
    }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } 
    .sun { color: #FF0000 !important; }

    .sub-label {
        font-size: 17px !important; font-weight: 800; color: #2E5077;
        margin-top: 8px !important; display: block;
    }

    .building-header { 
        font-size: 19px !important; font-weight: bold; color: #2E5077; 
        margin-top: 15px; border-bottom: 2px solid #2E5077; 
        padding-bottom: 5px; margin-bottom: 12px; 
    }

    .section-title { 
        font-size: 16px; font-weight: bold; color: #555; 
        margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; 
    }
    
    /* [수정] 카드 줄간격 1.4 적용 */
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 12px 14px; border-radius: 5px; 
        margin-bottom: 12px !important; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); 
        background-color: #ffffff;
        line-height: 1.4 !important; 
    }
    
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 4px; }
    .event-name { font-size: 14px; margin-top: 6px; color: #333; font-weight: 500; }
    
    .bottom-info { 
        font-size: 12px; color: #666; margin-top: 8px; 
        display: flex; justify-content: space-between; border-top: 1px solid #f3f3f3; padding-top: 6px;
    }
    .period-label { color: #d63384; font-weight: bold; }
    .allow-days { color: #2E5077; font-weight: bold; margin-left: 4px; }

    /* [발췌] 내역 없음 스타일 */
    .no-data-text { color: #999; font-size: 14px; padding: 15px; text-align: center; background-color: #fcfcfc; border: 1px dashed #ddd; border-radius: 8px; margin-bottom: 10px; }

    .bottom-spacer { height: 80px; }
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 4px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# ---------------------------------
# 3. 상단 날짜 이동 및 선택 UI
# ---------------------------------
col1, col2, col3, col4 = st.columns([1, 1.5, 1, 1])

with col1:
    if st.button("⬅ 이전", use_container_width=True):
        st.session_state.target_date -= timedelta(days=1)
        st.session_state.search_performed = True

with col2:
    selected_date = st.date_input("조회 날짜", value=st.session_state.target_date, label_visibility="collapsed")
    st.session_state.target_date = selected_date

with col3:
    if st.button("다음 ➡", use_container_width=True):
        st.session_state.target_date += timedelta(days=1)
        st.session_state.search_performed = True

with col4:
    if st.button("오늘", use_container_width=True):
        st.session_state.target_date = today_kst()
        st.session_state.search_performed = True

# ---------------------------------
# 4. 건물 및 유형 선택
# ---------------------------------
st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
# 체크박스를 한 줄에 촘촘히 배치하기 위해 컬럼 활용 가능 (여기서는 원본 유지)
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

st.write("")
st.markdown('<div id="btn-anchor"></div>', unsafe_allow_html=True)
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# ---------------------------------
# 5. 데이터 로직 및 출력
# ---------------------------------
@st.cache_data(ttl=300)
def get_data(target_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": target_date.strftime('%Y-%m-%d'), "end": target_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

def get_weekday_names(allow_day_str):
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    if not allow_day_str: return ""
    day_list = [days.get(d.strip()) for d in str(allow_day_str).split(",") if days.get(d.strip())]
    return f"({','.join(day_list)})"

if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}. <span class="{w_class}">({w_str})</span> 대관 현황</span>
    </div>
    """, unsafe_allow_html=True)

    # 검색 시 결과 위치로 스크롤
    components.html(f"<script>var element = window.parent.document.getElementById('btn-anchor'); if (element) {{ element.scrollIntoView({{behavior: 'smooth', block: 'start'}}); }}</script>", height=0)

    target_weekday = str(d.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False # [발췌 로직 핵심]
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                if not t_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in t_ev.sort_values(by='startTime').iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div><div class="bottom-info"><span class="period-label">🗓️ {row['startDt']}</span><span>👥 {row['mgDeptNm']}</span></div></div>""", unsafe_allow_html=True)

                if not v_p_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in v_p_ev.sort_values(by='startTime').iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        day_info = get_weekday_names(row['allowDay'])
                        st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div><div class="bottom-info"><span class="period-label">🗓️ {row['startDt']} ~ {row['endDt']} <span class="allow-days">{day_info}</span></span><span>👥 {row['mgDeptNm']}</span></div></div>""", unsafe_allow_html=True)

        # [발췌 로직 핵심] 결과가 없으면 출력
        if not has_bu_content:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
