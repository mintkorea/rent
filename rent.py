import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 요일 매핑 및 근무조 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(target_date):
    """2026년 1월 1일(B조) 기준 3교대 순환 계산"""
    base_date = date(2026, 1, 1)
    diff_days = (target_date - base_date).days
    shift_idx = (diff_days + 1) % 3 # 01.01이 B조(1)이므로 +1
    return SHIFT_TYPES[shift_idx]

def get_header_html(target_date):
    """헤더 형식: [ 날짜(요일) | 근무조 ] + 요일 색상(토:청, 일:적)"""
    w_idx = target_date.weekday()
    w_str = WEEKDAY_KR[w_idx]
    shift_group = get_shift_group(target_date)
    date_str = target_date.strftime("%Y.%m.%d")
    
    color = "#1E3A5F" # 평일 기본색
    if w_idx == 5: color = "#0000FF" # 토요일 청색
    elif w_idx == 6: color = "#FF0000" # 일요일/공휴일 적색
    
    return f'<div class="date-display" style="color:{color};">📋 성의교정 대관 현황 [ {date_str}({w_str}) | {shift_group} ]</div>'

# CSS 스타일 (image_82e95c.jpg 스타일 복구)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 17px !important; font-weight: 800; color: #2E5077; margin-top: 12px !important; display: block; }
    .date-display { text-align: center; font-size: 17px; font-weight: 800; background-color: #F0F2F6; padding: 12px; border-radius: 10px; margin: 20px 0; border: 1px solid #D1D9E6; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #444; margin: 18px 0 10px 0; padding-left: 8px; border-left: 5px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 12px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .status-badge { float: right; padding: 2px 10px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .time-highlight { color: #FF4B4B; margin-left: 8px; font-weight: 800; }
    .event-name { font-size: 14px; margin-top: 8px; color: #333; font-weight: 600; }
    .info-row { font-size: 12px; color: #666; margin-top: 8px; display: flex; align-items: center; gap: 5px; }
</style>
""", unsafe_allow_html=True)

# 2. 검색 필터
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed", key="v59_d")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BU):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v59_b_{i}"):
            selected_bu.append(b)

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True, key="v59_btn")

# 3. 데이터 로드 (SyntaxError 수정 포인트)
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
    st.markdown(get_header_html(target_date), unsafe_allow_html=True)

    if not df.empty:
        df['startDt_dt'] = pd.to_datetime(df['startDt']).dt.date
        df['endDt_dt'] = pd.to_datetime(df['endDt']).dt.date
        mask = (df['startDt_dt'] <= target_date) & (df['endDt_dt'] >= target_date)
        filtered_df = df[mask].copy()

        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = filtered_df[filtered_df['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                st.markdown('<div style="color:#888; padding:10px;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
            else:
                bu_df = bu_df.sort_values(by=['placeNm', 'startTime'])
                
                # 당일 대관 (시작일=종료일)
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not t_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in t_ev.iterrows():
                        cls, txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card"><span class="status-badge {cls}">{txt}</span><div>📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div><div class="event-name">📄 {row['eventNm']}</div><div class="info-row">👥 {row['mgDeptNm']}</div></div>""", unsafe_allow_html=True)

                # 기간 대관 (요일 필터링 적용)
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                if not p_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    target_weekday = str(target_date.weekday() + 1)
                    for _, row in p_ev.iterrows():
                        allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                        if target_weekday in allow_days:
                            cls, txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                            wd_info = "(" + ", ".join([WEEKDAY_MAP[d] for d in allow_days if d in WEEKDAY_MAP]) + ")"
                            st.markdown(f"""<div class="event-card"><span class="status-badge {cls}">{txt}</span><div>📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div><div class="event-name">📄 {row['eventNm']}</div><div class="info-row"><span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']} ~ {row['endDt']} {wd_info}</span> <span style="margin-left:8px; padding-left:8px; border-left:1px solid #ddd;">👥 {row['mgDeptNm']}</span></div></div>""", unsafe_allow_html=True)

    st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center><br>", unsafe_allow_html=True)
