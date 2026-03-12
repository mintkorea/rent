import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import pytz

# 1. 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")
KST = pytz.timezone('Asia/Seoul')
now_today = datetime.now(KST).date()
BUILDING_ORDER = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]

# 2. 모바일용 CSS (카드 디자인)
st.markdown("""
<style>
    .stApp { background-color: #F5F7FA; }
    .main-title { font-size: 22px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* 건물 헤더 스타일 */
    .building-header { font-size: 18px !important; font-weight: 700; color: #2E5077; margin-top: 30px; border-bottom: 2px solid #2E5077; padding-bottom: 8px; margin-bottom: 15px; }
    
    /* 모바일 카드 스타일 */
    .event-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #2E5077;
    }
    .event-time { font-size: 16px; font-weight: 800; color: #FF4B4B; margin-bottom: 5px; }
    .event-place { font-size: 15px; font-weight: 700; color: #333; }
    .event-name { font-size: 14px; color: #555; margin: 8px 0; line-height: 1.4; }
    .event-dept { font-size: 12px; color: #888; text-align: right; }
    
    /* 점선 내역 없음 박스 */
    .no-data-box { color: #999; text-align: center; padding: 25px; border: 1px dashed #CCC; font-size: 14px; background-color: #FFF; border-radius: 10px; margin: 10px 0; }
    
    /* 하단 상시 개방 카드 */
    .open-room-card { border: 1px dashed #2E5077; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #EFF5FF; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수 (기존 로직 유지)
@st.cache_data(ttl=60)
def get_data(s_date, e_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": s_date.isoformat(), "end": e_date.isoformat()}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        raw = res.json().get('res', [])
        rows = []
        for item in raw:
            if not item.get('startDt'): continue
            s_dt = datetime.strptime(item['startDt'], '%Y-%m-%d').date()
            e_dt = datetime.strptime(item['endDt'], '%Y-%m-%d').date()
            allowed_days = str(item.get('allowDay', '')).split(',')
            allowed_days = [d.strip() for d in allowed_days if d.strip()]
            curr = s_dt
            while curr <= e_dt:
                if s_date <= curr <= e_date:
                    if not (s_dt != e_dt and allowed_days and str(curr.isoweekday()) not in allowed_days):
                        rows.append({
                            '날짜': curr.strftime('%m-%d'),
                            '건물명': str(item.get('buNm', '')).strip(),
                            '장소': item.get('placeNm', ''), 
                            '시간': f"{item.get('startTime', '')} ~ {item.get('endTime', '')}",
                            '행사명': item.get('eventNm', ''), 
                            '부서': item.get('mgDeptNm', ''),
                            '상태': '확정' if item.get('status') == 'Y' else '대기'
                        })
                curr += timedelta(days=1)
        df = pd.DataFrame(rows)
        if not df.empty:
            df['건물명'] = pd.Categorical(df['건물명'], categories=BUILDING_ORDER, ordered=True)
            return df.sort_values(by=['날짜', '건물명', '시간'])
        return df
    except: return pd.DataFrame()

# 4. 사이드바 (입력창)
st.sidebar.markdown("### 🔍 조회 조건")
start_selected = st.sidebar.date_input("조회일", value=now_today)
selected_bu = st.sidebar.multiselect("건물 필터", options=BUILDING_ORDER, default=BUILDING_ORDER[:2])

# 5. 메인 결과 출력
st.markdown(f'<div class="main-title">🏫 대관 현황 ({start_selected})</div>', unsafe_allow_html=True)

all_df = get_data(start_selected, start_selected)

for bu in selected_bu:
    st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
    bu_df = all_df[all_df['건물명'] == bu] if not all_df.empty else pd.DataFrame()
    
    if not bu_df.empty:
        for _, row in bu_df.iterrows():
            status_tag = f" <span style='color:#1967D2; font-size:11px;'>[{row['상태']}]</span>"
            st.markdown(f"""
            <div class="event-card">
                <div class="event-time">⏰ {row['시간']}</div>
                <div class="event-place">📍 {row['장소']} {status_tag}</div>
                <div class="event-name">📄 {row['eventNm']}</div>
                <div class="event-dept">👥 {row['부서']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="no-data-box">내역 없음</div>', unsafe_allow_html=True)

# 6. 강의실 개방 요청 일람 (모바일 하단 카드)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"### 🔓 강의실 개방 요청 일람")

v_weekday = start_selected.isoweekday() 
is_weekend = v_weekday in [6, 7]
is_period_4th = (date(start_selected.year, 3, 2) <= start_selected <= date(start_selected.year, 4, 30))
is_period_801 = (date(start_selected.year, 2, 7) <= start_selected <= date(start_selected.year, 4, 24))

open_data = []
if not is_weekend:
    open_data.append({"bu": "별관", "rooms": ["1201~1206호 (오전 개방)"], "note": "1206호(금) 10시 교육" if v_weekday == 5 else ""})
else:
    open_data.append({"bu": "별관", "rooms": ["1201~1206호 (대관 확인 후)"], "note": "주말 지침"})

seong_rooms = []
if not is_weekend: seong_rooms.append("421~522호: 오전 개방")
if is_period_4th: seong_rooms.append("402~407호: 08:00 ~ 20:00")
if is_period_801: seong_rooms.append("801호: 09:00 ~ 21:00")
if v_weekday == 2: seong_rooms.append("502-1호: 19:00 ~ 22:00")
elif v_weekday == 3: seong_rooms.append("506호: 15:00경 / 502-1호: 19:00")

if seong_rooms:
    open_data.append({"bu": "성의회관", "rooms": seong_rooms, "note": "퇴실 독촉 금지"})

for item in open_data:
    st.markdown(f"""
    <div class="open-room-card">
        <div style="font-weight:bold; color:#2E5077; margin-bottom:5px;">🏢 {item['bu']}</div>
        <div style="font-size:13px; color:#333;">{' / '.join(item['rooms'])}</div>
        {f'<div style="font-size:11px; color:#666; margin-top:5px;">💡 {item["note"]}</div>' if item['note'] else ''}
    </div>
    """, unsafe_allow_html=True)
