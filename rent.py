import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import pytz

# 1. 페이지 및 기본 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="wide")
KST = pytz.timezone('Asia/Seoul')
now_today = datetime.now(KST).date()
BUILDING_ORDER = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]

# 2. CSS 설정 (점선 박스 및 카드 디자인)
st.markdown("""
<style>
    .stApp { background-color: white; }
    .main-title { font-size: 20px !important; font-weight: 800; text-align: center; margin-bottom: 15px; }
    .building-header { font-size: 16px !important; font-weight: 700; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .table-container { width: 100%; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 600px; }
    th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 6px; font-size: 11px; font-weight: bold; }
    td { border: 1px solid #eee; padding: 8px 6px; font-size: 12px; text-align: center; }
    /* 내역 없음 점선 박스 */
    .no-data-box { color: #999; text-align: center; padding: 15px; border: 1px dashed #ddd; font-size: 13px; margin: 10px 0; border-radius: 5px; }
    /* 강의실 개방 카드 */
    .open-room-card { border: 1px dashed #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 10px; background-color: #fcfcfc; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수
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
                    curr_weekday = str(curr.isoweekday())
                    is_allowed = True
                    if s_dt != e_dt and allowed_days:
                        if curr_weekday not in allowed_days: is_allowed = False
                    if is_allowed:
                        rows.append({
                            '날짜': curr.strftime('%m-%d'),
                            '건물명': str(item.get('buNm', '')).strip(),
                            '장소': item.get('placeNm', ''), 
                            '시간': f"{item.get('startTime', '')}~{item.get('endTime', '')}",
                            '행사명': item.get('eventNm', ''), 
                            '인원': item.get('peopleCount', ''),
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

# 4. 사이드바 설정
st.sidebar.title("📅 조회 설정")
start_selected = st.sidebar.date_input("조회 시작일", value=now_today)
end_selected = st.sidebar.date_input("조회 종료일", value=now_today)
selected_bu = st.sidebar.multiselect("건물 필터", options=BUILDING_ORDER, default=BUILDING_ORDER)

# 5. 대관 현황 출력
display_title = f"성의교정 대관 현황 ({start_selected})" if start_selected == end_selected else f"성의교정 대관 현황 ({start_selected} ~ {end_selected})"
st.markdown(f'<div class="main-title">🏫 {display_title}</div>', unsafe_allow_html=True)

all_df = get_data(start_selected, end_selected)

if not all_df.empty:
    for bu in selected_bu:
        bu_df = all_df[all_df['건물명'] == bu]
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        if not bu_df.empty:
            rows_html = "".join([f"<tr><td>{r['날짜']}</td><td>{r['장소']}</td><td>{r['시간']}</td><td style='text-align:left;'>{r['행사명']}</td><td>{r['인원']}</td><td>{r['부서']}</td><td>{r['상태']}</td></tr>" for _, r in bu_df.iterrows()])
            st.markdown(f'<div class="table-container"><table><thead><tr><th>날짜</th><th>장소</th><th>시간</th><th>행사명</th><th>인원</th><th>부서</th><th>상태</th></tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data-box">내역 없음</div>', unsafe_allow_html=True)
else:
    st.info("조회된 기간에 전체 대관 내역이 없습니다.")

# 6. 강의실 개방 요청 일람 (맨 하단 고정)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"### 🔓 강의실 개방 요청 일람 ({start_selected})")

v_weekday = start_selected.isoweekday() 
is_weekend = v_weekday in [6, 7]
is_period_4th = (date(start_selected.year, 3, 2) <= start_selected <= date(start_selected.year, 4, 30))
is_period_801 = (date(start_selected.year, 2, 7) <= start_selected <= date(start_selected.year, 4, 24))

open_data = []

# 별관 데이터
if not is_weekend:
    open_data.append({"bu": "별관", "rooms": ["1201~1206호 (오전 개방 / 오후 폐쇄)"], "note": "1206호 금요일 10시 교육 예정" if v_weekday == 5 else ""})
else:
    open_data.append({"bu": "별관", "rooms": ["1201~1206호 (대관 현황 확인 후 개방)"], "note": "주말 지침 적용"})

# 성의회관 데이터
seong_rooms = []
if not is_weekend: seong_rooms.append("421~522호: 오전 개방 (오후 원칙적 폐쇄)")
if is_period_4th: seong_rooms.append("402~407호: 08:00 ~ 20:00 (첫 순찰 개방)")
if is_period_801: seong_rooms.append("801호: 09:00 ~ 21:00 (직원 개방)")
if v_weekday == 2: seong_rooms.append("502-1호: 19:00 ~ 22:00")
elif v_weekday == 3: 
    seong_rooms.append("506호(솔로몬): 15:00경 개방")
    seong_rooms.append("502-1호: 19:00 ~ 22:00")

if seong_rooms:
    open_data.append({"bu": "성의회관", "rooms": seong_rooms, "note": "학생 요청 시 무리한 퇴실 조치 금지"})

# 화면 출력
if open_data:
    cols = st.columns(len(open_data))
    for i, item in enumerate(open_data):
        with cols[i]:
            st.markdown(f"""
            <div class="open-room-card">
                <div style="font-weight:bold; color:#2E5077; margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:5px;">🏢 {item['bu']}</div>
                <div style="font-size:13px; line-height:1.7; color:#333;">
                    {''.join([f"• {r}<br>" for r in item['rooms']])}
                </div>
                {f'<div style="font-size:11px; color:#666; margin-top:10px; padding-top:5px; font-style:italic;">💡 {item["note"]}</div>' if item['note'] else ''}
            </div>
            """, unsafe_allow_html=True)
