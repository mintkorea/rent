import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 (원본 복구)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 (줄간격 최소화 + 자바스크립트 없는 자동 스크롤)
st.markdown("""
<style>
    html { scroll-behavior: smooth; } /* 부드러운 스크롤 */import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 (태평양 줄간격 박멸 + 결과창 강제 이동)
st.markdown("""
<style>
    html { scroll-behavior: smooth; }
    #top-anchor { position: absolute; top: 0; }
    .block-container { padding: 0.2rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 줄간격 및 여백 최소화 */
    [data-testid="stVerticalBlock"] > div { padding: 0px !important; margin: 0px !important; gap: 0rem !important; }
    .stCheckbox { margin-bottom: -10px !important; }
    
    .main-title { font-size: 20px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    .sub-label { font-size: 15px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; margin-bottom: -5px !important; display: block; }
    
    /* 결과 상단 날짜 박스 (초슬림) */
    .date-display { 
        text-align: center; font-size: 17px; font-weight: 800; 
        background-color: #F0F2F6; padding: 5px; border-radius: 6px; 
        margin: 5px 0; color: #1E3A5F; line-height: 1.2; 
    }
    
    .sat-text { color: #0000FF !important; } 
    .sun-text { color: #FF0000 !important; }

    .building-header { font-size: 17px !important; font-weight: bold; color: #2E5077; margin-top: 8px; border-bottom: 2px solid #2E5077; padding-bottom: 2px; margin-bottom: 5px; }
    
    /* 카드 디자인 (줄간격 초밀착 고도화) */
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 4px 8px; border-radius: 4px; margin-bottom: 4px !important; 
        background-color: #ffffff; line-height: 1.0 !important; 
    }
    .place-name { font-size: 14px; font-weight: bold; color: #1E3A5F; margin-bottom: 2px; }
    .time-row { font-size: 13px; font-weight: bold; color: #FF4B4B; margin-bottom: 2px; }
    .event-name { font-size: 12px; color: #333; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .bottom-info { font-size: 10px; color: #777; display: flex; justify-content: space-between; margin-top: 2px; }
    
    .status-badge { padding: 0px 4px; font-size: 9px; border-radius: 4px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    
    /* TOP 버튼 */
    .top-link-container { position: fixed; bottom: 15px; right: 15px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 35px; height: 35px; line-height: 35px; text-align: center; border-radius: 50%; font-size: 10px; font-weight: bold; text-decoration: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v6_{b}"):
            selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
# 폼을 사용하여 버튼 클릭 시 결과 위치로 앵커 이동 유도
with st.form("search_form"):
    search_clicked = st.form_submit_button("🔍 조회하기 (클릭 시 하단 결과로 이동)", use_container_width=True)

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    # 앵커 지점
    st.markdown('<div id="result"></div>', unsafe_allow_html=True)
    
    df_raw = get_data(target_date)
    w_idx = target_date.weekday()
    w_str = ["월","화","수","목","금","토","일"][w_idx]
    w_class = "sat-text" if w_idx == 5 else ("sun-text" if w_idx == 6 else "")
    
    st.markdown(f"""
        <div class="date-display">
            성의교정 대관현황<br>
            {target_date.strftime("%Y.%m.%d")}<span class="{w_class}">({w_str})</span>
        </div>
    """, unsafe_allow_html=True)

    if not df_raw.empty:
        target_weekday = str(w_idx + 1)
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            
            for _, row in bu_df.iterrows():
                is_today = (row['startDt'] == row['endDt'])
                is_period = (row['startDt'] != row['endDt'])
                
                show = False
                if is_today and show_today: show = True
                elif is_period and show_period:
                    if target_weekday in [d.strip() for d in str(row.get('allowDay','')).split(",")]:
                        show = True
                
                if show:
                    s_cls, s_txt = (("status-y", "예약확정") if row.get('status') == 'Y' else ("status-n", "신청대기"))
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div class="place-name">📍 {row['placeNm']}</div>
                        <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div class="event-name">📄 {row['eventNm']}</div>
                        <div class="bottom-info">
                            <span>🗓️ {row['startDt']}</span>
                            <span>👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
    else:
        st.info("조회 내역이 없습니다.")

    # 조회 버튼 클릭 후 결과창으로 강제 포커스 이동 (HTML 앵커 활용)
    st.markdown('<script>window.location.hash="result";</script>', unsafe_allow_html=True)
    #top-anchor { position: absolute; top: 0; }
    .block-container { padding: 0.5rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 타이틀 및 간격 좁히기 */
    .main-title { font-size: 22px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }
    
    /* 결과 상단 날짜 박스 */
    .date-display { 
        text-align: center; font-size: 18px; font-weight: 800; 
        background-color: #F0F2F6; padding: 6px; border-radius: 10px; 
        margin: 10px 0; color: #1E3A5F; line-height: 1.3; 
    }
    
    /* 요일 색상 */
    .sat-text { color: #0000FF !important; } 
    .sun-text { color: #FF0000 !important; }

    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 10px; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin-bottom: 8px; }
    
    /* 카드 디자인 (줄간격 초밀착) */
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 5px 10px; border-radius: 5px; margin-bottom: 5px !important; background-color: #ffffff; line-height: 1.1 !important; }
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 14px; font-weight: bold; color: #FF4B4B; margin-top: 1px; }
    .event-name { font-size: 13px; margin-top: 2px; color: #333; }
    .bottom-info { font-size: 11px; color: #666; margin-top: 3px; display: flex; justify-content: space-between; }
    
    .status-badge { display: inline-block; padding: 1px 6px; font-size: 10px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    
    /* TOP 버튼 */
    .top-link-container { position: fixed; bottom: 20px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 40px; height: 40px; line-height: 40px; text-align: center; border-radius: 50%; font-size: 11px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); }
    
    /* 결과 이동 버튼 */
    .scroll-btn { display: block; width: 100%; background-color: #2E5077; color: white !important; text-align: center; padding: 10px; border-radius: 5px; text-decoration: none !important; font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
# 2열 배치로 세로 길이 축소
cols = st.columns(2)
for i, b in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v5_{b}"):
            selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=True)

search_clicked = st.button("🔍 데이터 조회하기", use_container_width=True)

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    # 결과 이동 버튼 (클릭 시 하단으로 스크롤)
    st.markdown('<a href="#result-section" class="scroll-btn">👇 결과 확인하기 (클릭)</a>', unsafe_allow_html=True)
    
    df_raw = get_data(target_date)
    
    # 요일 및 색상
    weekday_names = ["월","화","수","목","금","토","일"]
    w_idx = target_date.weekday()
    w_str = weekday_names[w_idx]
    w_class = "sat-text" if w_idx == 5 else ("sun-text" if w_idx == 6 else "")
    
    # 결과 섹션 시작 앵커
    st.markdown('<div id="result-section" style="padding-top:20px;"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="date-display">
            성의교정 대관현황<br>
            {target_date.strftime("%Y.%m.%d")}<span class="{w_class}">({w_str})</span>
        </div>
    """, unsafe_allow_html=True)

    if not df_raw.empty:
        target_weekday = str(w_idx + 1)
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            
            for _, row in bu_df.iterrows():
                is_today = (row['startDt'] == row['endDt'])
                is_period = (row['startDt'] != row['endDt'])
                
                show = False
                if is_today and show_today: show = True
                elif is_period and show_period:
                    if target_weekday in [d.strip() for d in str(row.get('allowDay','')).split(",")]:
                        show = True
                
                if show:
                    s_cls, s_txt = (("status-y", "예약확정") if row.get('status') == 'Y' else ("status-n", "신청대기"))
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div class="place-name">📍 {row['placeNm']}</div>
                        <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div class="event-name">📄 {row['eventNm']}</div>
                        <div class="bottom-info">
                            <span>🗓️ {row['startDt']}</span>
                            <span>👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # TOP 버튼
        st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")

