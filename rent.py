import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 (원본 그대로)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (구조는 유지하되 '간격'만 촘촘하게 압축)
st.markdown("""
<style>
    /* 메인 컨테이너 여백 축소 */
    .block-container { padding-top: 1rem !important; }
    
    /* [핵심] 체크박스 간격 극소화 - 18:13 스크린샷의 넓은 간격 해결 */
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; }
    
    /* 텍스트 및 제목 간격 압축 */
    .stMarkdown p, .stMarkdown h3 { margin-bottom: 2px !important; margin-top: 5px !important; line-height: 1.2 !important; }

    /* 날짜 이동 바 수평 고정 (찢어짐 방지) */
    div[data-testid="column"] { display: flex; align-items: center; justify-content: center; }
    
    /* 카드 내부 디자인 (18:57 버전 유지) */
    .building-header { font-size: 17px; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 2px; margin-top: 15px; }
    .event-card { border: 1px solid #E8E8E8; border-left: 5px solid #1E3A5F; padding: 10px; border-radius: 8px; margin-bottom: 8px; background: white; }
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-text { font-weight: bold; color: #E63946; }
    .info-sub { font-size: 11px; color: #888; display: flex; justify-content: space-between; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 추출 (원본 로직 - 성의회관 3건 모두 추출)
def get_data(target_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {
        "mode": "getReservedData",
        "start": target_date.strftime('%Y-%m-%d'),
        "end": target_date.strftime('%Y-%m-%d')
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        return pd.DataFrame(res.json().get('res', []))
    except:
        return pd.DataFrame()

# 4. 메인 UI (18:13 스크린샷의 모든 건물 리스트 복구)
st.title("🏫 성의교정 시설 대관 현황")

st.subheader("📅 날짜 선택")
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.subheader("🏢 건물 선택")
# 18:13 원본 리스트 100% 복구
all_buildings = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in all_buildings:
    # 18:13 기준 기본 체크 상태 유지
    is_default = b in ["성의회관", "의생명산업연구원"]
    if st.checkbox(b, value=is_default, key=f"chk_{b}"):
        selected_bu.append(b)

st.subheader("📋 대관 유형")
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 결과 출력
if st.session_state.search_performed:
    df = get_data(st.session_state.target_date)
    
    # 날짜 네비게이션 (수평 배치 고정)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1: 
        if st.button("⬅️"): change_date(-1); st.rerun()
    with c2: 
        st.markdown(f"### {st.session_state.target_date.strftime('%Y.%m.%d')} ({['월','화','수','목','금','토','일'][st.session_state.target_date.weekday()]})")
    with c3: 
        if st.button("➡️"): change_date(1); st.rerun()

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        # 필터링 로직
        has_data = False
        if not df.empty:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if not bu_df.empty:
                for _, r in bu_df.iterrows():
                    is_today = r['startDt'] == r['endDt']
                    if (is_today and show_today) or (not is_today and show_period):
                        has_data = True
                        st.markdown(f"""
                        <div class="event-card">
                            <div style="display:flex; justify-content:space-between;">
                                <span class="place-name">📍 {r['placeNm']}</span>
                                <span style="font-size:10px; background:#F0F0F0; padding:2px 6px; border-radius:4px;">{r['statNm']}</span>
                            </div>
                            <div style="margin:3px 0;"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                            <div style="font-size:13px;">📄 {r['eventNm']}</div>
                            <div class="info-sub"><span>🗓️ {r['startDt']}</span><span>👥 {r['mgDeptNm']}</span></div>
                        </div>""", unsafe_allow_html=True)
        
        # '내역 없음' 표시 복구
        if not has_data:
            st.write("대관 내역이 없습니다.")

st.markdown('<a href="#" style="position:fixed; bottom:20px; right:20px; background:#1E3A5F; color:white; width:45px; height:45px; border-radius:50%; text-align:center; line-height:45px; text-decoration:none; font-weight:bold; z-index:1000; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">TOP</a>', unsafe_allow_html=True)
