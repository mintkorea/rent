import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관", layout="centered")

# CSS: 모바일 가독성 및 카드 디자인
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    header { visibility: hidden; }
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; }
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; margin-top: 15px; padding-bottom: 3px; }
    .event-card { border: 1px solid #eee; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #2E5077; background-color: #fcfcfc; }
    .no-data { font-size: 13px; color: #888; padding: 10px 0; font-style: italic; }
</style>
""", unsafe_allow_html=True)

st.title("🏫 성의교정 대관 현황")

# 2. 필터 영역
target_date = st.date_input("날짜 선택", value=date(2026, 3, 12))

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
st.write("**🗓️ 유형 선택**")
c1, c2 = st.columns(2)
show_today = c1.checkbox("📌 당일 대관", value=True)
show_period = c2.checkbox("🗓️ 기간 대관", value=True)

# 3. 조회 버튼
search_clicked = st.button("🔍 조회하기", use_container_width=True, type="primary")

# 4. 데이터 엔진
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

# 5. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    
    # 상단 요약 바 정보 추출
    group_info = df_raw.iloc[0].get('groupNm', '정보없음') if not df_raw.empty and 'groupNm' in df_raw.columns else "-"
    st.success(f"📅 {target_date.strftime('%Y.%m.%d')} | {group_info} 대관 내역")

    if not selected_buildings:
        st.warning("조회할 건물을 선택해 주세요.")
    else:
        # 데이터가 있는 경우에만 날짜 필터링 진행
        if not df_raw.empty:
            temp_df = df_raw.copy()
            temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
            temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
            df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]
        else:
            df = pd.DataFrame()

        # 건물별 순회 출력
        for bu in selected_buildings:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            
            # 현재 건물 데이터 필터링
            bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()
            
            # 유형 필터링 (당일/기간) 적용
            if not bu_df.empty:
                bu_df = bu_df[
                    ((bu_df['startDt'] == bu_df['endDt']) & show_today) |
                    ((bu_df['startDt'] != bu_df['endDt']) & show_period)
                ]

            # 최종 출력 또는 "내역 없음" 표시
            if bu_df.empty:
                st.markdown('<div class="no-data">ℹ️ 선택하신 유형의 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
            else:
                for _, row in bu_df.iterrows():
                    card_html = f"""
                    <div class="event-card">
                        <div style="font-weight:bold; font-size:15px; color:#1E3A5F;">📍 {row['placeNm']}</div>
                        <div style="color:#FF4B4B; font-weight:bold; font-size:14px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="font-size:13px; margin-top:5px; color:#333;">📄 {row['eventNm']}</div>
                        <div style="font-size:11px; color:#777; margin-top:5px;">👥 {row['mgDeptNm']}</div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
