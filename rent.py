import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state: st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state: st.session_state.search_performed = False

# 3. CSS 스타일 (틀어진 카드 및 메인 디자인 전면 수정)
st.markdown("""
<style>
    .block-container { padding: 1.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 10px; margin-bottom: 5px; display: block; }

    /* 타이틀 박스 (이미지 f1c9e3 기준) */
    .result-box-container {
        margin-top: 30px;
        background-color: #F0F4F8;
        border: 1px solid #D1D9E6;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .result-title { font-size: 18px; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 4px; }
    .result-date { font-size: 16px; font-weight: 700; }
    
    .blue-date { color: #0047FF !important; }
    .red-date { color: #FF0000 !important; }

    /* 슬림 컨트롤러 버튼 스타일 */
    div[data-testid="stColumn"] button {
        height: 32px !important;
        min-height: 32px !important;
        line-height: 32px !important;
        padding: 0 5px !important;
        font-size: 13px !important;
        border-radius: 6px !important;
    }

    /* 카드 디자인 복구 (이미지 24153e 기준) */
    .building-header { 
        font-size: 18px; font-weight: bold; color: #1E3A5F; 
        border-bottom: 2px solid #1E3A5F; padding-bottom: 5px; margin: 20px 0 12px 0; 
    }
    .section-title { font-size: 15px; font-weight: bold; color: #666; margin: 10px 0 5px 5px; }
    
    .event-card { 
        position: relative; border: 1px solid #E0E0E0; border-radius: 8px; 
        padding: 12px 15px; margin-bottom: 12px; background: white; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); line-height: 1.5 !important;
    }
    .status-badge {
        position: absolute; top: 12px; right: 12px;
        background-color: #FFF3E0; color: #E65100;
        font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 10px;
    }
    .place-name { font-size: 16px; font-weight: 800; color: #1E3A5F; margin-bottom: 4px; display: block; }
    .time-row { font-size: 15px; font-weight: 700; color: #D32F2F; margin-bottom: 4px; display: block; }
    .event-name { font-size: 14px; color: #333; font-weight: 500; }
    
    .no-data-text { color: #999; font-size: 13px; padding: 20px; text-align: center; background: #FAFAFA; border: 1px dashed #DDD; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

c_bu, c_ty = st.columns(2)
with c_bu:
    st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
    ALL_B = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
    selected_bu = [b for b in ALL_B if st.checkbox(b, value=(b=="성의회관"), key=f"b_{b}")]
with c_ty:
    st.markdown('<span class="sub-label">🗓️ 유형 선택</span>', unsafe_allow_html=True)
    show_today = st.checkbox("당일 대관", value=True)
    show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 데이터 로드 (기존 로직 유지)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력 영역
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 요일 색상 결정
    c_cls = ""
    if w_idx == 5: c_cls = "blue-date"
    elif w_idx == 6 or is_holiday(d): c_cls = "red-date"

    # 타이틀 박스 (고정형)
    st.markdown(f"""
    <div class="result-box-container">
        <span class="result-title">성의교정 대관 현황</span>
        <span class="result-date {c_cls}">{d.strftime('%Y.%m.%d')}.({w_str})</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 슬림 버튼 컨트롤러 (타이틀 박스 외부 하단)
    nc1, nc2, nc3 = st.columns([1, 1.5, 1])
    with nc1:
        if st.button("◀ 이전", key="p_day", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with nc2:
        if st.button("오늘", key="t_day", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
    with nc3:
        if st.button("다음 ▶", key="n_day", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    df_raw = get_data(d)
    t_weekday = str(w_idx + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_any = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ","").str.contains(bu.replace(" ",""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: t_weekday in [i.strip() for i in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                combined = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                if not combined.empty:
                    has_any = True
                    for _, row in combined.iterrows():
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge">예약확정</span>
                            <span class="place-name">📍 {row['placeNm']}</span>
                            <span class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</span>
                            <div class="event-name">📄 {row['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)

        if not has_any:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
