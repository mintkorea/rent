import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.rerun()

# 2. CSS 스타일: 메인 페이지 줄간격만 정밀하게 압축
st.markdown("""
<style>
    /* 메인 페이지 레이아웃 압축 */
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stCheckbox"] { margin-bottom: -18px !important; }
    .stMarkdown p, .stMarkdown h3 { margin-bottom: 2px !important; margin-top: 4px !important; line-height: 1.2 !important; }
    
    /* 검색 버튼 (빨간색 원복) */
    div.stButton > button[kind="primary"] {
        background-color: #FF5252 !important; color: white !important;
        font-weight: bold !important; width: 100%; border: none;
    }

    /* 결과 카드 디자인 (18:57 원본 스타일) */
    .building-header { font-size: 17px; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; margin-top: 15px; padding-bottom: 2px; }
    .event-card { border: 1px solid #E8E8E8; border-left: 5px solid #1E3A5F; padding: 10px; border-radius: 8px; margin-bottom: 8px; background: white; }
    .time-text { font-weight: bold; color: #E63946; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 추출 (가장 중요한 부분: 기간 대관 포함 3건 모두 가져오기)
def get_rental_data(target_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    # 앞뒤로 넉넉하게 조회하여 오늘 날짜가 포함된 '기간 대관'을 놓치지 않음
    params = {
        "mode": "getReservedData",
        "start": (target_date - timedelta(days=60)).strftime('%Y-%m-%d'),
        "end": (target_date + timedelta(days=60)).strftime('%Y-%m-%d')
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        all_data = res.json().get('res', [])
        df = pd.DataFrame(all_data)
        if df.empty: return df
        
        # [핵심 필터] 사용자가 선택한 날짜가 대관 기간(startDt ~ endDt) 내에 있는지 체크
        target_str = target_date.strftime('%Y-%m-%d')
        df = df[(df['startDt'] <= target_str) & (df['endDt'] >= target_str)]
        return df
    except:
        return pd.DataFrame()

# 4. 메인 UI (18:13 스크린샷 원본 항목 완벽 유지)
st.title("🏫 성의교정 시설 대관 현황")

st.subheader("📅 날짜 선택")
target_date = st.date_input("d", value=st.session_state.target_date, label_visibility="collapsed")

st.subheader("🏢 건물 선택")
buildings = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in buildings if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"main_{b}")]

st.subheader("📋 대관 유형")
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", type="primary"):
    df = get_rental_data(target_date)
    
    # 날짜 네비게이션
    st.write("")
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1: 
        if st.button("⬅️", key="btn_p"): change_date(-1)
    with c2:
        w = ['월','화','수','목','금','토','일'][target_date.weekday()]
        st.markdown(f"<h3 style='text-align:center;'>{target_date.strftime('%Y.%m.%d')} ({w})</h3>", unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="btn_n"): change_date(1)

    # 5. 결과 출력 (성의회관 3건 모두 표시 및 내역 없음 표시)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu, na=False)] if not df.empty else pd.DataFrame()
        
        found_any = False
        if not bu_df.empty:
            for _, r in bu_df.iterrows():
                is_today = (r['startDt'] == r['endDt'])
                if (is_today and show_today) or (not is_today and show_period):
                    found_any = True
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
        
        if not found_any:
            st.write("대관 내역이 없습니다.")

st.markdown('<a href="#" style="position:fixed; bottom:20px; right:20px; background:#1E3A5F; color:white; width:45px; height:45px; border-radius:50%; text-align:center; line-height:45px; text-decoration:none; font-weight:bold; z-index:1000;">TOP</a>', unsafe_allow_html=True)
