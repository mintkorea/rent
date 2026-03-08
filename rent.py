import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 (자바스크립트 없이 스타일만 정의)
st.markdown("""
<style>
    /* 상단 여백 및 너비 조절 */
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 결과 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; 
        padding: 15px; border-radius: 12px; margin-bottom: 20px; 
        border: 1px solid #D1D9E6; line-height: 1.6;
    }
    .res-main-title { font-size: 20px; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 3px; }
    .res-sub-title { font-size: 17px; font-weight: 700; color: #333; }
    
    /* 요일 색상 */
    .sat-text { color: #0000FF !important; font-weight: bold; } 
    .sun-text { color: #FF0000 !important; font-weight: bold; }

    /* 근무조 배지 - 네이비 배경(#000080) + 흰색 글씨(#FFFFFF) 강제 고정 */
    .g-badge {
        display: inline-block !important;
        padding: 3px 12px !important;
        border-radius: 6px !important;
        font-weight: 900 !important;
        margin-left: 5px !important;
        background-color: #000080 !important;
        color: #FFFFFF !important;
        border: 1px solid #000060;
    }

    /* 카드 디자인 */
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 10px 12px; border-radius: 5px; margin-bottom: 12px !important; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div style="text-align:center; font-size:24px; font-weight:800; color:#1E3A5F; margin-bottom:15px;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

target_date = st.date_input("날짜 선택", value=date(2026, 3, 12), label_visibility="collapsed")

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"])):
        selected_bu.append(b)

show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

# 검색 버튼
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직 (데이터가 없을 때를 대비한 안전한 설계)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json().get('res', [])
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    
    # 요일 처리
    weekday_list = ['월', '화', '수', '목', '금', '토', '일']
    w_idx = target_date.weekday()
    w_str = weekday_list[w_idx]
    
    # 요일별 CSS 클래스 선택
    w_span_class = ""
    if w_idx == 5: w_span_class = "sat-text"
    elif w_idx == 6: w_span_class = "sun-text"
    
    # 조 이름 추출 로직 (있는 그대로 가져오기)
    group_display = "-"
    if not df_raw.empty and 'groupNm' in df_raw.columns:
        valid_val = df_raw['groupNm'].dropna().unique()
        if len(valid_val) > 0:
            group_display = str(valid_val[0]).strip()
            if "조" not in group_display: group_display += "조"

    # 타이틀 섹션 (네이비 배지 적용)
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">
            {target_date.strftime("%Y.%m.%d")}.<span class="{w_span_class}">({w_str})</span> | 
            근무 : <span class="g-badge">{group_display}</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

    if not df_raw.empty:
        target_weekday = str(w_idx + 1)
        for bu in selected_bu:
            if 'buNm' not in df_raw.columns: continue
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div style="font-size:18px; font-weight:bold; color:#2E5077; border-bottom:2px solid #2E5077; margin-top:15px; padding-bottom:5px;">🏢 {bu}</div>', unsafe_allow_html=True)
            
            # 당일 대관
            if show_today:
                today_ev = bu_df[bu_df['startDt'] == bu_df.get('endDt', bu_df['startDt'])]
                if not today_ev.empty:
                    for _, row in today_ev.iterrows():
                        st.markdown(f"""<div class="event-card">
                            <div style="font-size:16px; font-weight:bold; color:#1E3A5F;">📍 {row.get('placeNm','-')}</div>
                            <div style="font-size:15px; font-weight:bold; color:#FF4B4B; margin-top:2px;">⏰ {row.get('startTime','')} ~ {row.get('endTime','')}</div>
                            <div style="font-size:14px; margin-top:4px;">📄 {row.get('eventNm','')}</div>
                            <div style="font-size:12px; color:#666; margin-top:5px; display:flex; justify-content:space-between;"><span>🗓️ {row.get('startDt','')}</span><span>👥 {row.get('mgDeptNm','')}</span></div>
                        </div>""", unsafe_allow_html=True)
            
            # 기간 대관
            if show_period and 'allowDay' in bu_df.columns:
                period_ev = bu_df[bu_df['startDt'] != bu_df.get('endDt', '')]
                valid_period_ev = period_ev[period_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])]
                if not valid_period_ev.empty:
                    for _, row in valid_period_ev.iterrows():
                        st.markdown(f"""<div class="event-card">
                            <div style="font-size:16px; font-weight:bold; color:#1E3A5F;">📍 {row.get('placeNm','-')}</div>
                            <div style="font-size:15px; font-weight:bold; color:#FF4B4B; margin-top:2px;">⏰ {row.get('startTime','')} ~ {row.get('endTime','')}</div>
                            <div style="font-size:14px; margin-top:4px;">📄 {row.get('eventNm','')}</div>
                            <div style="font-size:12px; color:#666; margin-top:5px; display:flex; justify-content:space-between;"><span>🗓️ {row.get('startDt','')} ~ {row.get('endDt','')}</span><span>👥 {row.get('mgDeptNm','')}</span></div>
                        </div>""", unsafe_allow_html=True)
    else:
        st.info("해당 날짜에 조회된 대관 내역이 없습니다.")
