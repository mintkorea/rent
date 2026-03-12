import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
from fpdf import FPDF
import os

# 1. 페이지 설정 및 강제 CSS (다크모드 대응 & 여백 확대)
st.set_page_config(page_title="성의교정 대관 조회", layout="wide")

st.markdown("""
<style>
    /* 전체 배경 및 글자색 */
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; margin-bottom: 10px; }
    
    /* 날짜 구분선: 위쪽 여백 80px로 확대 (수정 확인용) */
    .date-header { 
        font-size: 20px !important; font-weight: 800 !important; 
        margin-top: 80px !important; margin-bottom: 20px !important;
        padding-bottom: 10px !important;
        border-bottom: 4px solid #4A90E2 !important; 
        color: #4A90E2 !important;
    }
    
    /* 건물명 강조 */
    .building-header { 
        font-size: 17px !important; font-weight: 700 !important; 
        margin-top: 25px !important; margin-bottom: 10px !important; 
        border-left: 6px solid #4A90E2 !important; padding-left: 12px !important;
    }
    
    /* 테이블: 다크모드에서도 테두리가 뚜렷하게 보이도록 설정 */
    .table-container table { width: 100% !important; border-collapse: collapse !important; }
    .table-container th { 
        background-color: rgba(128, 128, 128, 0.4) !important; 
        border: 2px solid rgba(128, 128, 128, 0.9) !important; 
        padding: 12px !important; font-weight: bold;
    }
    .table-container td { 
        border: 1px solid rgba(128, 128, 128, 0.7) !important; 
        padding: 10px !important; text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. 기본 변수 및 데이터 로드 함수
KST = pytz.timezone('Asia/Seoul')
now_today = datetime.now(KST).date()
BUILDING_ORDER = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스파크 의과대학", "옴니버스파크 간호대학", "대학본관", "서울성모별관"]

@st.cache_data(ttl=10) # 10초 캐시로 즉시 반영 유도
def get_rental_data(s_date, e_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": s_date.isoformat(), "end": e_date.isoformat()}
    try:
        res = requests.get(url, params=params, timeout=10)
        raw = res.json().get('res', [])
        rows = []
        for item in raw:
            if not item.get('startDt'): continue
            # 요일 필터 로직
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

# 3. 사이드바 UI
st.sidebar.title("📅 대관 조회 설정")
s_day = st.sidebar.date_input("시작일", value=now_today)
e_day = st.sidebar.date_input("종료일", value=s_day)
sel_bu = st.sidebar.multiselect("건물 선택", options=BUILDING_ORDER, default=["성의회관", "의생명산업연구원"])

# 4. 메인 화면 출력
st.markdown('<div class="main-title">🏫 성의교정 대관 현황</div>', unsafe_allow_html=True)

data = get_rental_data(s_day, e_day)

if not data.empty:
    for date in sorted(data['full_date'].unique()):
        day_df = data[data['full_date'] == date]
        # 날짜 구분선
        st.markdown(f'<div class="date-header">📅 {date} ({day_df.iloc[0]["요일"]}요일)</div>', unsafe_allow_html=True)
        
        for b in sel_bu:
            b_df = day_df[day_df['건물명'] == b]
            if not b_df.empty:
                st.markdown(f'<div class="building-header">🏢 {b}</div>', unsafe_allow_html=True)
                # HTML 테이블 렌더링
                rows_html = "".join([f"<tr><td>{r['장소']}</td><td>{r['시간']}</td><td style='text-align:left;'>{r['행사명']}</td><td>{r['인원']}</td><td>{r['부서']}</td><td>{r['상태']}</td></tr>" for _, r in b_df.iterrows()])
                st.markdown(f'<div class="table-container"><table><thead><tr><th>장소</th><th>시간</th><th>행사명</th><th>인원</th><th>부서</th><th>상태</th></tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)
else:
    st.info("조회된 내역이 없습니다.")
