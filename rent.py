import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 및 디자인 (image_82e95c.jpg 스타일 완벽 유지)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 요일 매핑 테이블 (1:월 ~ 7:일)
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_weekday_string(allow_day_str):
    """'1,2,3' -> '(월, 화, 수)' 변환"""
    if not allow_day_str or pd.isna(allow_day_str): return ""
    days = [WEEKDAY_MAP.get(d.strip()) for d in str(allow_day_str).split(",") if d.strip() in WEEKDAY_MAP]
    return f"({', '.join(days)})" if days else ""

def is_event_on_day(target_date, allow_day_str):
    """선택한 날짜의 요일이 allowDay에 포함되는지 확인"""
    if not allow_day_str or pd.isna(allow_day_str): return True # 정보 없으면 기본 노출
    # target_date.weekday()는 0(월)~6(일)이므로 +1 하여 맞춤
    target_weekday = str(target_date.weekday() + 1)
    allow_days = [d.strip() for d in str(allow_day_str).split(",")]
    return target_weekday in allow_days

st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 17px !important; font-weight: 800; color: #2E5077; margin-top: 12px !important; margin-bottom: 5px !important; display: block; }
    .date-display { text-align: center; font-size: 19px; font-weight: 800; background-color: #F0F2F6; padding: 12px; border-radius: 10px; margin: 20px 0; color: #1E3A5F; border: 1px solid #D1D9E6; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #444; margin: 18px 0 10px 0; padding-left: 8px; border-left: 5px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 12px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .status-badge { float: right; padding: 2px 10px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .place-time { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; margin-left: 8px; font-weight: 800; }
    .event-name { font-size: 14px; margin-top: 8px; color: #333; font-weight: 600; }
    .info-row { font-size: 12px; color: #666; margin-top: 8px; display: flex; align-items: center; gap: 8px; }
    .weekday-text { color: #2E5077; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI (Duplicate ID 방지 고유 Key)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜선택", value=date(2026, 3, 12), label_visibility="collapsed", key="v57_date")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v57_bu_{i}"):
            selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관 보기", value=True, key="v57_show_t")
with c2: show_period = st.checkbox("기간 대관 보기", value=True, key="v57_show_p")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True, key="v57_search_btn")

# 3. 데이터 로드 로직
@st.cache_data(ttl=300)
def fetch_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df = fetch_data(target_date)
    st.markdown(f'<div class="date-display">📋 성의교정 대관 현황({target_date.strftime("%Y.%m.%d")})</div>', unsafe_allow_html=True)

    if not df.empty:
        df['startDt_dt'] = pd.to_datetime(df['startDt']).dt.date
        df['endDt_dt'] = pd.to_datetime(df['endDt']).dt.date
        
        # 기본 날짜 범위 필터링
        mask = (df['startDt_dt'] <= target_date) & (df['endDt_dt'] >= target_date)
        filtered_df = df[mask].copy()

        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = filtered_df[filtered_df['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                st.markdown('<div style="color:#888; padding:10px;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
            else:
                bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
                bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])

                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]

                # 당일 대관
                if show_today and not t_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in t_ev.iterrows():
                        cls, txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card"><span class="status-badge {cls}">{txt}</span><div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div><div class="event-name">📄 {row['eventNm']}</div><div class="info-row">👥 {row['mgDeptNm']}</div></div>""", unsafe_allow_html=True)

                # 기간 대관 (요일 필터링 적용)
                if show_period and not p_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    has_period_content = False
                    for _, row in p_ev.iterrows():
                        # 요일 조건 확인: 선택한 날짜의 요일이 allowDay에 포함될 때만 출력
                        if is_event_on_day(target_date, row.get('allowDay', '')):
                            has_period_content = True
                            cls, txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                            wd_info = get_weekday_string(row.get('allowDay', ''))
                            st.markdown(f"""<div class="event-card"><span class="status-badge {cls}">{txt}</span><div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div><div class="event-name">📄 {row['eventNm']}</div><div class="info-row"><span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']} ~ {row['endDt']}</span> <span class="weekday-text">{wd_info}</span> <span style="margin-left:8px; padding-left:8px; border-left:1px solid #ddd;">👥 {row['mgDeptNm']}</span></div></div>""", unsafe_allow_html=True)
                    
                    if not has_period_content:
                        st.markdown('<div style="color:#888; padding:5px 10px; font-size:14px;">ℹ️ 오늘 해당 요일의 기간 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center><br>", unsafe_allow_html=True)
