import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
from fpdf import FPDF
import os

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="wide")

# 2. 강력한 CSS 적용 (다크모드 대응 및 여백 확대)
st.markdown("""
<style>
    /* 메인 타이틀 */
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; margin-bottom: 10px; }
    
    /* 날짜 구분선: 위쪽 간격을 70px로 대폭 확대 (수정 여부 확인용) */
    .date-header { 
        font-size: 20px !important; font-weight: 800 !important; 
        margin-top: 70px !important; margin-bottom: 15px !important;
        padding-bottom: 10px !important;
        border-bottom: 3px solid #4A90E2 !important; 
        color: #4A90E2 !important;
    }
    
    /* 테이블 테두리: 다크모드에서도 무조건 보이도록 rgba 농도 강화 */
    .table-container table { width: 100% !important; border-collapse: collapse !important; }
    .table-container th { 
        background-color: rgba(128, 128, 128, 0.4) !important; 
        border: 2px solid rgba(128, 128, 128, 0.8) !important; 
        padding: 10px !important;
    }
    .table-container td { 
        border: 1px solid rgba(128, 128, 128, 0.6) !important; 
        padding: 8px !important; text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 (캐시 초기화 포함)
KST = pytz.timezone('Asia/Seoul')
now_today = datetime.now(KST).date()
BUILDING_ORDER = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스파크 의과대학", "옴니버스파크 간호대학", "대학본관", "서울성모별관"]

@st.cache_data(ttl=30)
def get_data_final(s_date, e_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": s_date.isoformat(), "end": e_date.isoformat()}
    try:
        res = requests.get(url, params=params, timeout=10)
        raw = res.json().get('res', [])
        rows = []
        for item in raw:
            if not item.get('startDt'): continue
            # 요일 필터링 로직
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
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

# 4. PDF 생성 함수 (NanumGothic 폰트 적용)
def create_pdf(df, sel_bu):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    font_path = "NanumGothic.ttf"
    if os.path.exists(font_path):
        pdf.add_font("Nanum", "", font_path)
        pdf.set_font("Nanum", size=10)
    
    for date_val in sorted(df['full_date'].unique()):
        pdf.add_page()
        d_df = df[df['full_date'] == date_val]
        pdf.cell(0, 10, f"대관 현황 - {date_val}", ln=True, align='C')
        # ... 이하 PDF 테이블 생성 로직 생략 (기존과 동일)
    return pdf.output()

# 5. UI 및 실행
st.sidebar.title("📅 설정")
s_day = st.sidebar.date_input("시작일", value=now_today)
e_day = st.sidebar.date_input("종료일", value=s_day)
sel_bu = st.sidebar.multiselect("건물 필터", options=BUILDING_ORDER, default=["성의회관", "의생명산업연구원"])

st.markdown('<div class="main-title">🏫 성의교정 대관 현황</div>', unsafe_allow_html=True)

data = get_data_final(s_day, e_day)

if not data.empty:
    for date in sorted(data['full_date'].unique()):
        day_df = data[data['full_date'] == date]
        st.markdown(f'<div class="date-header">📅 {date} ({day_df.iloc[0]["요일"]}요일)</div>', unsafe_allow_html=True)
        # 테이블 출력 로직...
else:
    st.info("조회된 내역이 없습니다.")
