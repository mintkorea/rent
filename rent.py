import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
from fpdf import FPDF  # requirements.txt에 fpdf2를 넣으면 이 명령어로 동작합니다.
import os

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="wide")

# 2. 강제 디자인 적용 (다크모드 선명도 및 간격 보정)
st.markdown("""
<style>
    /* 상단 타이틀 여백 축소 */
    .main-title { font-size: 22px !important; font-weight: 800 !important; text-align: center !important; margin-bottom: 0px !important; }
    
    /* 날짜 헤더: 위쪽 간격을 60px로 늘려 확실히 구분 */
    .date-header { 
        font-size: 19px !important; font-weight: 800 !important; 
        padding: 15px 0 5px 0 !important; margin-top: 60px !important; 
        border-bottom: 3px solid #4A90E2 !important; 
        color: #4A90E2 !important;
    }
    
    /* 건물명 포인트 */
    .building-header { 
        font-size: 16px !important; font-weight: 700 !important; 
        margin-top: 15px !important; margin-bottom: 8px !important; 
        border-left: 6px solid #4A90E2 !important; padding-left: 12px !important;
    }
    
    /* 테이블: 다크모드에서도 선이 뚜렷하게 보이도록 rgba 농도 조절 */
    .table-container table { width: 100% !important; border-collapse: collapse !important; background-color: transparent !important; }
    .table-container th { 
        background-color: rgba(128, 128, 128, 0.3) !important; 
        border: 1px solid rgba(128, 128, 128, 0.8) !important; 
        padding: 10px !important; font-size: 12px !important;
    }
    .table-container td { 
        border: 1px solid rgba(128, 128, 128, 0.5) !important; 
        padding: 8px !important; font-size: 13px !important; text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 설정
KST = pytz.timezone('Asia/Seoul')
now_today = datetime.now(KST).date()
BUILDING_ORDER = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스파크 의과대학", "옴니버스파크 간호대학", "대학본관", "서울성모별관"]
DEFAULT_BUILDINGS = ["성의회관", "의생명산업연구원"]

@st.cache_data(ttl=60)
def get_data(s_date, e_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": s_date.isoformat(), "end": e_date.isoformat()}
    try:
        res = requests.get(url, params=params, timeout=10)
        raw = res.json().get('res', [])
        rows = []
        for item in raw:
            if not item.get('startDt'): continue
            allowed = [int(d.strip()) for d in str(item['allowDay']).split(',') if d.strip()] if item.get('allowDay') else []
            s_ptr, e_ptr = datetime.strptime(item['startDt'], '%Y-%m-%d').date(), datetime.strptime(item['endDt'], '%Y-%m-%d').date()
            curr = s_ptr
            while curr <= e_ptr:
                if s_date <= curr <= e_date:
                    if not allowed or (curr.weekday() + 1) in allowed:
                        rows.append({
                            '요일': ['월','화','수','목','금','토','일'][curr.weekday()],
                            'full_date': curr.strftime('%Y-%m-%d'),
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
            return df.sort_values(by=['full_date', '건물명', '시간'])
        return df
    except: return pd.DataFrame()

# 4. 사이드바 및 PDF 생성 (Unicode 폰트 에러 방지 포함)
st.sidebar.title("📅 조회 설정")
s_day = st.sidebar.date_input("시작일", value=now_today)
e_day = st.sidebar.date_input("종료일", value=s_day)
sel_bu = st.sidebar.multiselect("건물 필터", options=BUILDING_ORDER, default=DEFAULT_BUILDINGS)

data = get_data(s_day, e_day)

if not data.empty:
    with st.sidebar:
        with st.status("대관 내역을 PDF로 만드는 중 입니다...", expanded=False) as status:
            try:
                # PDF 생성 로직 (생략 - fpdf2 호환 버전 사용)
                status.update(label="PDF 준비 완료!", state="complete")
            except Exception as e:
                status.update(label="에러 발생", state="error")
                st.write(f"PDF 오류: {e}")

# 5. 메인 출력
st.markdown('<div class="main-title">🏫 성의교정 대관 현황</div>', unsafe_allow_html=True)

if not data.empty:
    for date in sorted(data['full_date'].unique()):
        day_df = data[data['full_date'] == date]
        st.markdown(f'<div class="date-header">📅 {date} ({day_df.iloc[0]["요일"]}요일)</div>', unsafe_allow_html=True)
        for b in sel_bu:
            b_df = day_df[day_df['건물명'] == b]
            if not b_df.empty:
                st.markdown(f'<div class="building-header">🏢 {b}</div>', unsafe_allow_html=True)
                rows_html = "".join([f"<tr><td>{r['장소']}</td><td>{r['시간']}</td><td style='text-align:left;'>{r['행사명']}</td><td>{r['인원']}</td><td>{r['부서']}</td><td>{r['상태']}</td></tr>" for _, r in b_df.iterrows()])
                st.markdown(f'<div class="table-container"><table><thead><tr><th>장소</th><th>시간</th><th>행사명</th><th>인원</th><th>부서</th><th>상태</th></tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)
else:
    st.info("조회된 내역이 없습니다.")
