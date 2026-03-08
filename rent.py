import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 기본 설정
st.set_page_config(page_title="성의교정 대관", layout="centered")

# CSS: 모바일 가독성 최적화 (에러 방지를 위해 최소화)
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    header { visibility: hidden; }import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 기본 설정
st.set_page_config(page_title="성의교정 대관", layout="centered")

# CSS: 모바일 가독성 최적화 (에러 방지를 위해 최소화)
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    header { visibility: hidden; }
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; }
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; margin-top: 15px; }
    .event-card { border: 1px solid #eee; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #2E5077; background-color: #fcfcfc; }
</style>
""", unsafe_allow_html=True)

st.title("🏫 성의교정 대관 현황")

# 2. 필터 섹션
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
# 버튼을 클릭하면 세션 상태를 변경하여 화면을 하단으로 유도합니다.
if st.button("🔍 조회하기", use_container_width=True, type="primary"):
    st.session_state.search_done = True
else:
    if 'search_done' not in st.session_state:
        st.session_state.search_done = False

# 4. 데이터 로딩 함수
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

# 5. 결과 출력 (버튼 클릭 시에만 나타남)
if st.session_state.search_done:
    # [자동 스크롤 포인트] 결과가 시작되는 지점에 닻(Anchor)을 내립니다.
    st.markdown("<div id='result'></div>", unsafe_allow_html=True)
    
    df_raw = get_data(target_date)
    
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]
        
        # 운영 조 정보 추출
        group_info = df_raw.iloc[0].get('groupNm', 'C조') if 'groupNm' in df_raw.columns else "C조"
        st.success(f"📅 {target_date.strftime('%Y.%m.%d')} | {group_info} 대관 내역")

        for bu in selected_buildings:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()

            if bu_df.empty:
                st.caption("ℹ️ 해당 건물에 대관 내역이 없습니다.")
            else:
                for _, row in bu_df.iterrows():
                    is_today = row['startDt'] == row['endDt']
                    # 필터 조건 확인
                    if (is_today and show_today) or (not is_today and show_period):
                        # 안전한 텍스트 출력을 위해 f-string과 HTML 조합 최적화
                        card_html = f"""
                        <div class="event-card">
                            <div style="font-weight:bold; font-size:15px; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="color:#FF4B4B; font-weight:bold; font-size:14px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:13px; margin-top:5px; color:#333;">📄 {row['eventNm']}</div>
                            <div style="font-size:11px; color:#777; margin-top:5px;">👥 {row['mgDeptNm']}</div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 해당 날짜에 조회된 데이터가 없습니다.")

    # 조회 후 버튼 아래로 다시 돌아가는 것을 방지하기 위해 하단에 여백 추가
    st.write("")
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; }
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; margin-top: 15px; }
    .event-card { border: 1px solid #eee; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #2E5077; background-color: #fcfcfc; }
</style>
""", unsafe_allow_html=True)

st.title("🏫 성의교정 대관 현황")

# 2. 필터 섹션
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
# 버튼을 클릭하면 세션 상태를 변경하여 화면을 하단으로 유도합니다.
if st.button("🔍 조회하기", use_container_width=True, type="primary"):
    st.session_state.search_done = True
else:
    if 'search_done' not in st.session_state:
        st.session_state.search_done = False

# 4. 데이터 로딩 함수
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

# 5. 결과 출력 (버튼 클릭 시에만 나타남)
if st.session_state.search_done:
    # [자동 스크롤 포인트] 결과가 시작되는 지점에 닻(Anchor)을 내립니다.
    st.markdown("<div id='result'></div>", unsafe_allow_html=True)
    
    df_raw = get_data(target_date)
    
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]
        
        # 운영 조 정보 추출
        group_info = df_raw.iloc[0].get('groupNm', 'C조') if 'groupNm' in df_raw.columns else "C조"
        st.success(f"📅 {target_date.strftime('%Y.%m.%d')} | {group_info} 대관 내역")

        for bu in selected_buildings:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()

            if bu_df.empty:
                st.caption("ℹ️ 해당 건물에 대관 내역이 없습니다.")
            else:
                for _, row in bu_df.iterrows():
                    is_today = row['startDt'] == row['endDt']
                    # 필터 조건 확인
                    if (is_today and show_today) or (not is_today and show_period):
                        # 안전한 텍스트 출력을 위해 f-string과 HTML 조합 최적화
                        card_html = f"""
                        <div class="event-card">
                            <div style="font-weight:bold; font-size:15px; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="color:#FF4B4B; font-weight:bold; font-size:14px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:13px; margin-top:5px; color:#333;">📄 {row['eventNm']}</div>
                            <div style="font-size:11px; color:#777; margin-top:5px;">👥 {row['mgDeptNm']}</div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 해당 날짜에 조회된 데이터가 없습니다.")

    # 조회 후 버튼 아래로 다시 돌아가는 것을 방지하기 위해 하단에 여백 추가
    st.write("")

