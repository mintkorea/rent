import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 (부타이틀 복구 + TOP 버튼 + 요일 색상)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 (줄간격 초밀착 + 스크롤 애니메이션)
st.markdown("""
<style>
    /* 전체 스크롤 부드럽게 */
    html { scroll-behavior: smooth; }
    #top-anchor { position: absolute; top: 0; }
    
    .block-container { padding: 0.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 간격 축소 컨트롤 */
    .main-title { font-size: 22px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 0px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 8px !important; margin-bottom: -10px !important; display: block; }
    
    /* 결과 상단 날짜 박스 (촘촘하게) */
    .date-display { 
        text-align: center; font-size: 18px; font-weight: 800; 
        background-color: #F0F2F6; padding: 8px; border-radius: 8px; 
        margin: 10px 0; color: #1E3A5F; line-height: 1.3; 
    }
    
    /* 요일 색상 */
    .sat-text { color: #0000FF !important; } 
    .sun-text { color: #FF0000 !important; }

    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 2px; margin-bottom: 8px; }
    
    /* 카드 디자인 (줄간격 최소화) */
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 6px 10px; border-radius: 4px; margin-bottom: 6px !important; background-color: #ffffff; }
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; line-height: 1.2; }
    .time-row { font-size: 14px; font-weight: bold; color: #FF4B4B; margin-top: 0px; }
    .event-info { font-size: 13px; margin-top: 2px; color: #333; line-height: 1.2; }
    .bottom-info { font-size: 11px; color: #777; margin-top: 4px; display: flex; justify-content: space-between; }
    
    .status-badge { display: inline-block; padding: 0px 6px; font-size: 10px; border-radius: 8px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    
    /* TOP 버튼 */
    .top-link-container { position: fixed; bottom: 20px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 40px; height: 40px; line-height: 40px; text-align: center; border-radius: 50%; font-size: 11px; font-weight: bold; text-decoration: none !important; box-shadow: 1px 2px 5px rgba(0,0,0,0.2); }
    
    /* 검색 버튼 내부 이동용 링크 스타일 */
    .scroll-link { display: block; text-align: center; background-color: #FF4B4B; color: white !important; padding: 10px; border-radius: 5px; text-decoration: none !important; font-weight: bold; margin-top: 10px; }
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
# 건물 체크박스 간격도 좁게 유지
cols = st.columns(2)
for i, b in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
            selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=True)

# 검색 버튼 및 결과 이동 앵커
st.write(" ")
search_clicked = st.button("🔍 데이터 불러오기", use_container_width=True)

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
    # 검색 성공 시 결과 위치로 바로 이동하도록 유도하는 버튼형 링크
    st.markdown('<a href="#result-top" class="scroll-link">👇 결과 바로보기 (클릭)</a>', unsafe_allow_html=True)
    st.markdown('<div id="result-top" style="margin-top:20px;"></div>', unsafe_allow_html=True)
    
    df_raw = get_data(target_date)
    
    weekday_names = ["월","화","수","목","금","토","일"]
    w_idx = target_date.weekday()
    w_str = weekday_names[w_idx]
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
                        <div class="event-info">📄 {row['eventNm']}</div>
                        <div class="bottom-info">
                            <span>🗓️ {row['startDt']} {('~ ' + row['endDt']) if is_period else ''}</span>
                            <span>👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 메인 및 부타이틀 스타일 */
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 20px !important; display: block; margin-bottom: 10px !important; }
    
    /* 결과 상단 날짜 박스 */
    .date-display { 
        text-align: center; font-size: 19px; font-weight: 800; 
        background-color: #F0F2F6; padding: 12px; border-radius: 10px; 
        margin-bottom: 20px; color: #1E3A5F; line-height: 1.5; 
    }
    
    /* 요일 색상 */
    .sat-text { color: #0000FF !important; } 
    .sun-text { color: #FF0000 !important; }

    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 15px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px 15px; border-radius: 5px; margin-bottom: 12px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; }
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 2px; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 8px; display: flex; justify-content: space-between; }
    
    .status-badge { display: inline-block; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    
    /* 플로팅 TOP 버튼 */
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 4px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

# 페이지 상단 이동을 위한 앵커
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI (부타이틀 완벽 복구)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    show_today = st.checkbox("당일 대관", value=True)
with c2:
    show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

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
    df_raw = get_data(target_date)
    
    # 요일 처리 및 색상 결정
    weekday_names = ["월","화","수","목","금","토","일"]
    w_idx = target_date.weekday()
    w_str = weekday_names[w_idx]
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
                    s_cls = "status-y" if row.get('status') == 'Y' else "status-n"
                    s_txt = "예약확정" if row.get('status') == 'Y' else "신청대기"
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div class="place-name">📍 {row['placeNm']}</div>
                        <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="font-size:14px; margin-top:5px; color:#333;">📄 {row['eventNm']}</div>
                        <div class="bottom-info">
                            <span>🗓️ {row['startDt']} {('~ ' + row['endDt']) if is_period else ''}</span>
                            <span>👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # TOP 버튼 활성화
        st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")

