import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
import io
import os

# 1. 브라우저 탭 및 앱 설정 (아이콘 적용)
st.set_page_config(
    page_title="성의교정 대관현황 조회시스템", 
    page_icon="🏫",  # 브라우저 탭 아이콘 (이모지)
    layout="wide"
)

# 2. CSS: 모바일 가독성 및 디자인 강화
st.markdown("""
<style>
    /* 메인 타이틀 스타일 */
    .main-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1E3A5F;
        border-bottom: 3px solid #1E3A5F;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    /* 모바일에서 테이블 글자 크기 조정 */
    .stDataFrame {
        font-size: 0.9rem;
    }
    /* 상태 아이콘 색상 */
    .status-confirm { color: green; font-weight: bold; }
    .status-wait { color: orange; }
</style>
""", unsafe_allow_html=True)

# [데이터 수집 및 근무조/연차 로직은 이전과 동일]
def get_shift(target_date):
    base_date = date(2026, 3, 13)
    diff = (target_date - base_date).days
    shifts = ['A', 'B', 'C']
    return f"{shifts[diff % 3]}조"

def get_vacationers(target_date):
    file_path = "vacation.csv"
    if not os.path.exists(file_path): return ""
    try:
        try: v_df = pd.read_csv(file_path, encoding='utf-8')
        except: v_df = pd.read_csv(file_path, encoding='cp949')
        v_df['날짜'] = pd.to_datetime(v_df['날짜']).dt.date
        names = v_df[v_df['날짜'] == target_date]['이름'].tolist()
        return f" 🌴(연차: {', '.join(names)})" if names else ""
    except: return ""

@st.cache_data(ttl=60)
def get_data(start_date, end_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": start_date.isoformat(), "end": end_date.isoformat()}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        raw = res.json().get('res', [])
        rows = []
        for item in raw:
            if not item.get('startDt'): continue
            s_dt = datetime.strptime(item['startDt'], '%Y-%m-%d').date()
            e_dt = datetime.strptime(item['endDt'], '%Y-%m-%d').date()
            allow_day_raw = str(item.get('allowDay', '')).lower()
            allowed_days = [d.strip() for d in allow_day_raw.replace(' ', '').split(',') if d.strip().isdigit()] if allow_day_raw != 'none' else []
            
            curr = s_dt
            while curr <= e_dt:
                if start_date <= curr <= end_date:
                    if not allowed_days or str(curr.isoweekday()) in allowed_days:
                        # 상태에 아이콘 추가
                        status_val = '✅ 확정' if item.get('status') == 'Y' else '⏳ 대기'
                        rows.append({
                            'full_date': curr.strftime('%Y-%m-%d'),
                            '건물명': str(item.get('buNm', '')).strip(),
                            '장소': f"📍 {item.get('placeNm', '')}",
                            '시간': f"⏰ {item.get('startTime', '')}~{item.get('endTime', '')}",
                            '행사명': item.get('eventNm', '') or '-',
                            '부서': item.get('mgDeptNm', '') or '-',
                            '인원': f"👥 {item.get('peopleCount', '0')}",
                            '상태': status_val
                        })
                curr += timedelta(days=1)
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

# 4. 메인 UI (아이콘 적용)
with st.sidebar:
    st.markdown("## 🏢 성의교정 대관")
    st.write("조회 기간을 선택하세요.")
    s_date = st.date_input("📅 시작일", value=date.today())
    e_date = st.date_input("📅 종료일", value=s_date)
    sel_bu = st.multiselect("🏢 건물 필터", options=["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"], default=["성의회관", "의생명산업연구원"])

st.markdown('<div class="main-title">🏫 성의교정 대관현황 시스템</div>', unsafe_allow_html=True)

df = get_data(s_date, e_date)

if not df.empty:
    for d_str in sorted(df['full_date'].unique()):
        d_obj = datetime.strptime(d_str, '%Y-%m-%d').date()
        wd_name = ['','월','화','수','목','금','토','일'][d_obj.isoweekday()]
        vacation = get_vacationers(d_obj)
        
        # 날짜 헤더 아이콘화
        st.markdown(f"#### 🗓️ {d_str} ({wd_name}) | 👮 근무: {get_shift(d_obj)} <span style='color:#ff4b4b;'>{vacation}</span>", unsafe_allow_html=True)
        
        for b in sel_bu:
            b_df = df[(df['full_date'] == d_str) & (df['건물명'] == b)]
            if not b_df.empty:
                st.write(f"**🏢 {b}**")
                st.dataframe(b_df[['장소', '시간', '행사명', '부서', '인원', '상태']], use_container_width=True, hide_index=True)
else:
    st.info("💡 조회된 대관 내역이 없습니다.")
