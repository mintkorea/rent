
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 1. CSS: 메인 줄간격 극소화 (사용자님 요청사항)
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stCheckbox"] { margin-bottom: -18px !important; }
    .stMarkdown p, .stMarkdown h3 { margin-bottom: 2px !important; margin-top: 5px !important; line-height: 1.2 !important; }
    div[data-testid="column"] { display: flex; align-items: center; justify-content: center; }
    .building-header { font-size: 17px; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; margin-top: 15px; }
    .event-card { border: 1px solid #E8E8E8; border-left: 5px solid #1E3A5F; padding: 10px; border-radius: 8px; margin-bottom: 8px; background: white; }
    .time-text { font-weight: bold; color: #E63946; }
</style>
""", unsafe_allow_html=True)

# 2. 데이터 추출 로직 (기간 대관 겹침 확인 로직 추가)
def get_verified_data(target_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    # 현재 달의 데이터를 넉넉하게 가져와서 필터링 (기간 대관 누락 방지)
    params = {
        "mode": "getReservedData",
        "start": (target_date - timedelta(days=30)).strftime('%Y-%m-%d'),
        "end": (target_date + timedelta(days=30)).strftime('%Y-%m-%d')
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        all_data = res.json().get('res', [])
        df = pd.DataFrame(all_data)
        if df.empty: return df
        
        # 선택한 날짜(target_date)가 시작일과 종료일 사이에 있는지 정확히 체크
        target_str = target_date.strftime('%Y-%m-%d')
        df = df[(df['startDt'] <= target_str) & (df['endDt'] >= target_str)]
        return df
    except:
        return pd.DataFrame()

# 3. 메인 화면 항목 (18:13 원본 완벽 복구)
st.title("🏫 성의교정 시설 대관 현황")
target_date = st.date_input("날짜", value=date.today(), label_visibility="collapsed")

st.subheader("🏢 건물 선택")
all_bu = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in all_bu if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=b)]

st.subheader("📋 대관 유형")
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    df = get_verified_data(target_date)
    
    # 날짜 바 수평 고정
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2: st.markdown(f"### {target_date.strftime('%Y.%m.%d')} ({['월','화','수','목','금','토','일'][target_date.weekday()]})")

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()
        
        display_count = 0
        if not bu_df.empty:
            for _, r in bu_df.iterrows():
                is_today = (r['startDt'] == r['endDt'])
                if (is_today and show_today) or (not is_today and show_period):
                    display_count += 1
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-size:15px; font-weight:bold; color:#1E3A5F;">📍 {r['placeNm']}</span>
                            <span style="font-size:10px; background:#F0F0F0; padding:2px 6px; border-radius:4px;">{r['statNm']}</span>
                        </div>
                        <div style="margin:3px 0;"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                        <div style="font-size:13px;">📄 {r['eventNm']}</div>
                        <div style="font-size:11px; color:#888; display:flex; justify-content:space-between; margin-top:5px;">
                            <span>🗓️ {r['startDt']} ~ {r['endDt']}</span><span>👥 {r['mgDeptNm']}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
        
        if display_count == 0:
            st.write("대관 내역이 없습니다.")
