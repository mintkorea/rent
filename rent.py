import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 및 모바일 극강 최적화 CSS
st.set_page_config(page_title="성의교정 대관", layout="centered")

st.markdown("""
<style>
    .block-container { padding-top: 0.5rem !important; }
    header { visibility: hidden; }
    /* 결과 카드 디자인 */
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; margin-bottom: 10px; padding-bottom: 5px; }
    .event-card { border: 1px solid #eee; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #2E5077; background-color: #fcfcfc; }
    .no-data { font-size: 14px; color: #999; padding: 10px 0; text-align: center; border: 1px dashed #ddd; border-radius: 8px; margin-bottom: 15px; }
    /* 버튼 스타일 */
    div.stButton > button { height: 3em; font-size: 16px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# 2. 세션 상태 초기화 (조회 여부 확인)
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# 3. [조회 전] 필터 설정 화면
if not st.session_state.submitted:
    st.title("🏫 대관 현황 조회")
    
    target_date = st.date_input("날짜 선택", value=date(2026, 3, 12))
    
    st.write("**🏢 건물 선택 (2열)**")
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
    
    if st.button("🔍 조회하기", use_container_width=True, type="primary"):
        # 설정을 세션에 저장하고 상태 변경
        st.session_state.target_date = target_date
        st.session_state.selected_buildings = selected_buildings
        st.session_state.show_today = show_today
        st.session_state.show_period = show_period
        st.session_state.submitted = True
        st.rerun()

# 4. [조회 후] 결과 집중 화면
else:
    # 다시 검색 버튼 (상단 배치)
    if st.button("⬅️ 다시 검색", use_container_width=False):
        st.session_state.submitted = False
        st.rerun()

    # 데이터 가져오기
    @st.cache_data(ttl=300)
    def get_data(selected_date):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, params=params, headers=headers)
            return pd.DataFrame(res.json().get('res', []))
        except: return pd.DataFrame()

    df_raw = get_data(st.session_state.target_date)
    group_info = df_raw.iloc[0].get('groupNm', '-') if not df_raw.empty and 'groupNm' in df_raw.columns else "정보없음"
    
    st.subheader(f"📅 {st.session_state.target_date.strftime('%y.%m.%d')} ({group_info})")

    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= st.session_state.target_date) & (temp_df['endDt_dt'] >= st.session_state.target_date)]
    else:
        df = pd.DataFrame()

    # 건물별 결과 출력
    for bu in st.session_state.selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()
        
        # 유형 필터 적용
        if not bu_df.empty:
            bu_df = bu_df[
                ((bu_df['startDt'] == bu_df['endDt']) & st.session_state.show_today) |
                ((bu_df['startDt'] != bu_df['endDt']) & st.session_state.show_period)
            ]

        if bu_df.empty:
            st.markdown('<div class="no-data">해당 건물에 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            for _, row in bu_df.iterrows():
                st.markdown(f"""
                <div class="event-card">
                    <div style="font-weight:bold; font-size:15px; color:#1E3A5F;">📍 {row['placeNm']}</div>
                    <div style="color:#FF4B4B; font-weight:bold; font-size:14px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                    <div style="font-size:13px; margin-top:5px;">📄 {row['eventNm']}</div>
                    <div style="font-size:11px; color:#777; margin-top:5px;">👥 {row['mgDeptNm']}</div>
                </div>
                """, unsafe_allow_html=True)
