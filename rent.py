import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 및 디자인 (불필요한 배경 박스 제거 및 초밀착)
st.set_page_config(page_title="성의교정 대관 현황", layout="centered")

st.markdown("""
<style>
    /* 상단 여백 제거 */
    .block-container { padding-top: 1rem !important; }
    header { visibility: hidden; }
    
    /* 타이틀 및 요약 바 디자인 */
    .main-title { font-size: 20px !important; font-weight: bold; text-align: center; color: #1E3A5F; margin-bottom: 5px; }
    .summary-bar { background-color: #F0F4F8; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 15px; border: 1px solid #D1D9E6; }
    .summary-text { font-size: 16px; font-weight: bold; color: #1E3A5F; }

    /* 체크박스 줄 간격 초밀착 */
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; }
    div[data-testid="stCheckbox"] label p { font-size: 14px !important; }

    /* 결과 카드 디자인 */
    .building-header { font-size: 17px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 2px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 8px; margin-bottom: 8px; background-color: #fff; }
    .no-data { font-size: 13px; color: #888; padding: 10px 0; font-style: italic; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 필터 영역 (배경 없이 노출)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.write("**🏢 건물 선택**")
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
DEFAULT_BUILDINGS = ["성의회관", "의생명산업연구원"]

selected_buildings = []
cols = st.columns(2)
for i, bu in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(bu, value=(bu in DEFAULT_BUILDINGS), key=f"bu_{bu}"):
            selected_buildings.append(bu)

st.write("---")
c1, c2 = st.columns(2)
show_today = c1.checkbox("📌 당일 대관", value=True)
show_period = c2.checkbox("🗓️ 기간 대관", value=True)

search_clicked = st.button("🔍 결과 조회하기", use_container_width=True, type="primary")

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, params=params, headers=headers)
        return pd.DataFrame(res.json().get('res', []))
    except:
        return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    
    # 요약 정보 추출 (C조 등)
    group_info = df_raw.iloc[0].get('groupNm', '-') if not df_raw.empty and 'groupNm' in df_raw.columns else "-"
    weekday_dict = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
    weekday_str = weekday_dict[target_date.weekday()]

    # 요청하신 형태의 상단 바
    st.markdown(f"""
    <div class="summary-bar">
        <div class="summary-text">{target_date.strftime('%Y.%m.%d')} ({weekday_str}) | {group_info} 대관 현황</div>
    </div>
    """, unsafe_allow_html=True)

    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]
    else:
        df = pd.DataFrame()

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()
        
        # 유형 필터링 적용
        if not bu_df.empty:
            bu_df = bu_df[
                ((bu_df['startDt'] == bu_df['endDt']) & show_today) |
                ((bu_df['startDt'] != bu_df['endDt']) & show_period)
            ]

        if bu_df.empty:
            st.markdown('<div class="no-data">ℹ️ 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            for _, row in bu_df.iterrows():
                st.markdown(f"""
                <div class="event-card">
                    <div style="font-weight:bold; font-size:15px; color:#1E3A5F;">📍 {row['placeNm']}</div>
                    <div style="color:#FF4B4B; font-weight:bold; font-size:14px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                    <div style="font-size:13px; margin-top:5px; color:#333;">📄 {row['eventNm']}</div>
                    <div style="font-size:11px; color:#777; margin-top:3px;">👥 {row['mgDeptNm']}</div>
                </div>
                """, unsafe_allow_html=True)
