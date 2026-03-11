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
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# 3. CSS 스타일 (화살표 디자인 및 버튼 슬림화만 추가, 카드 디자인은 원본 유지)
st.markdown("""
<style>
    .block-container { padding: 1.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 결과 박스 스타일 (화살표 포함) */
    .result-main-box {
        background-color: #F0F4FA;
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .result-main-title { font-size: 20px; font-weight: 800; color: #1E3A5F; margin-bottom: 10px; display: block; }
    .result-main-date { font-size: 18px; font-weight: 700; display: flex; justify-content: center; align-items: center; gap: 15px; }

    /* 요일 색상 */
    .blue-date { color: #0047FF !important; }
    .red-date { color: #FF0000 !important; }
    .black-date { color: #333333 !important; }

    /* 하단 슬림 버튼 (중앙 정렬) */
    div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] button {
        height: 28px !important;
        min-height: 28px !important;
        padding: 0px !important;
        font-size: 12px !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력 UI (원본 설정 및 배치 100% 유지)
st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
# 원본처럼 7개 건물 리스트 및 성의회관/의생명 2개 기본 선택 유지
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
# 원본처럼 유형 선택 하단 배치 유지
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 데이터 로직 (원본 무수정)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    c_cls = "black-date"
    if w_idx == 5: c_cls = "blue-date"
    elif w_idx == 6 or is_holiday(d): c_cls = "red-date"

    # 화살표가 포함된 결과 박스 디자인 (image_f1ac37 스타일)
    st.markdown(f"""
    <div class="result-main-box">
        <span class="result-main-title">성의교정 대관 현황</span>
        <div class="result-main-date">
            <span style="color:#1E3A5F;">⬅</span>
            <span class="{c_cls}">{d.strftime('%Y.%m.%d')}.({w_str})</span>
            <span style="color:#1E3A5F;">➡</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 슬림 버튼 3개 중앙 정렬
    bc1, bc2, bc3, bc4, bc5 = st.columns([1.5, 0.5, 1, 0.5, 1.5])
    with bc2:
        if st.button("◀", key="p"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with bc3:
        if st.button("오늘", key="t"):
            st.session_state.target_date = today_kst()
            st.rerun()
    with bc4:
        if st.button("▶", key="n"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    df_raw = get_data(st.session_state.target_date)
    for bu in selected_bu:
        # 원본 카드 디자인 CSS 100% 무수정 적용
        st.markdown(f'<div style="font-size:18px; font-weight:bold; color:#1E3A5F; border-bottom:2px solid #1E3A5F; padding-bottom:5px; margin:25px 0 10px 0;">🏢 {bu}</div>', unsafe_allow_html=True)
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
                        <div style="border:1px solid #E0E0E0; border-left:5px solid #2E5077; padding:12px; border-radius:6px; margin-bottom:10px; background:white;">
                            <div style="font-size:16px; font-weight:800; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="font-size:15px; font-weight:700; color:#D32F2F; margin-top:3px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:14px; color:#444; margin-top:5px;">📄 {row['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_any:
            # 원본 내역 없음 디자인 100% 무수정 적용
            st.markdown('<div style="color:#999; font-size:13px; padding:15px; text-align:center; background:#FAFAFA; border:1px dashed #DDD; border-radius:10px;">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
