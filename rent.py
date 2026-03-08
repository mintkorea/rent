import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 - 요청하신 네이비 배경+흰색 글씨 고정
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 상단 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; 
        padding: 15px; border-radius: 12px; margin-bottom: 20px; 
        border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 20px; font-weight: 800; color: #1E3A5F; display: block; }
    
    /* 요일 색상 */
    .sat { color: #0000FF !important; font-weight: bold; } 
    .sun { color: #FF0000 !important; font-weight: bold; }

    /* 근무조 배지 - 네이비 바탕(#000080) / 흰색 글자(#FFFFFF) */
    .g-badge {
        display: inline-block !important;
        background-color: #000080 !important;
        color: #FFFFFF !important;
        padding: 2px 12px !important;
        border-radius: 6px !important;
        font-weight: 900 !important;
        margin-left: 5px !important;
    }

    /* 대관 카드 스타일 */
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 10px; border-radius: 5px; margin-bottom: 10px; 
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

# 건물 선택 (원본 체크박스 리스트)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"])):
        selected_bu.append(b)

show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except:
        return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    
    # 요일/날짜 처리
    w_idx = target_date.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    # 조 이름 가져오기
    group_nm = "-"
    if not df_raw.empty and 'groupNm' in df_raw.columns:
        valid_groups = df_raw['groupNm'].dropna().unique()
        if len(valid_groups) > 0:
            group_nm = str(valid_groups[0]).strip()
            if "조" not in group_nm: group_nm += "조"

    # 상단 타이틀 (네이비 배지)
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <div style="font-size: 17px; font-weight: 700; margin-top:5px;">
            {target_date.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span> | 
            근무 : <span class="g-badge">{group_nm}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 본래 데이터 출력 구조
    if not df_raw.empty:
        target_weekday = str(w_idx + 1)
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f"### 🏢 {bu}")
            
            # 필터링 로직 (당일/기간)
            for _, row in bu_df.iterrows():
                is_today = row['startDt'] == row['endDt']
                is_period = row['startDt'] != row['endDt']
                
                # 기간 대관일 경우 요일 체크
                include = False
                if is_today and show_today:
                    include = True
                elif is_period and show_period:
                    if target_weekday in [d.strip() for d in str(row.get('allowDay','')).split(",")]:
                        include = True
                
                if include:
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                        <div style="color:#FF4B4B; font-weight:bold;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="font-size:14px; margin-top:4px;">📄 {row['eventNm']}</div>
                        <div style="font-size:12px; color:#666; margin-top:5px;">👥 {row['mgDeptNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")
