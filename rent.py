import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. 환경 설정 및 UI 테마 고정
st.set_page_config(page_title="성의교정 대관 관리 시스템", page_icon="🏫", layout="wide")
KST = pytz.timezone('Asia/Seoul')
now_today = datetime.now(KST).date()

# CSS: 가로 표(PC)와 세로 카드(모바일) 디자인 최적화
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .main .block-container { max-width: 1200px; margin: 0 auto; padding: 0.5rem 1rem !important; }
    .main-title { font-size: 24px; font-weight: 800; color: #1E3A5F; text-align: center; margin-bottom: 15px; }
    
    /* 가로 표 전용 스타일: 셀 너비 고정(%) 및 줄바꿈 방지 */
    .custom-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 13px; table-layout: fixed; background: white; }
    .custom-table th { background: #f1f4f9; border: 1px solid #dee2e6; padding: 12px 5px; text-align: center; color: #1E3A5F; }
    .custom-table td { border: 1px solid #dee2e6; padding: 10px 8px; text-align: center; vertical-align: middle; line-height: 1.5; }
    .event-cell { text-align: left !important; font-weight: 600; }
    .period-info { font-size: 11px; color: #2196F3; display: block; margin-top: 4px; font-weight: normal; }
    
    /* 날짜 및 건물 헤더 */
    .date-bar { background-color: #343a40; color: white; padding: 12px; border-radius: 6px; text-align: center; font-weight: bold; margin-top: 30px; margin-bottom: 15px; }
    .bu-header { font-size: 17px; font-weight: bold; color: #1E3A5F; margin: 15px 0 8px 0; border-left: 5px solid #1E3A5F; padding: 6px 12px; background: #f8f9fa; }
    
    /* 모바일 카드 스타일 */
    .mobile-card { background: white; border: 1px solid #eef0f2; border-left: 5px solid #2ecc71; border-radius: 6px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .m-row-1 { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
    .m-loc { font-size: 15px; font-weight: 800; color: #1E3A5F; }
    .m-time { font-size: 14px; font-weight: bold; color: #e74c3c; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 핵심 로직 함수 (인수인계 포인트) ---

def get_weekday_names(codes):
    """요일 코드(1,2,3)를 한글 요일로 변환"""
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    return ",".join([days.get(c.strip(), "") for c in str(codes).split(",") if c.strip() in days])

def get_shift(target_date):
    """2026-03-13 기준 3교대 로테이션 계산"""
    base_date = date(2026, 3, 13)
    diff = (target_date - base_date).days
    return f"{['A', 'B', 'C'][diff % 3]}조"

@st.cache_data(ttl=60)
def get_data(start_date, end_date):
    """학교 서버에서 대관 데이터 수집 및 전처리"""
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": start_date.isoformat(), "end": end_date.isoformat()}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        raw, rows = res.json().get('res', []), []
        for item in raw:
            if not item.get('startDt'): continue
            s_dt = datetime.strptime(item['startDt'], '%Y-%m-%d').date()
            e_dt = datetime.strptime(item['endDt'], '%Y-%m-%d').date()
            is_p = (item['startDt'] != item['endDt'])
            p_rng = f"{item['startDt']}~{item['endDt']}"
            d_nms = get_weekday_names(item.get('allowDay', ''))
            allowed = [d.strip() for d in str(item.get('allowDay', '')).split(",") if d.strip().isdigit()]
            
            curr = s_dt
            while curr <= e_dt:
                if start_date <= curr <= end_date:
                    if not allowed or str(curr.isoweekday()) in allowed:
                        rows.append({
                            'full_date': curr.strftime('%Y-%m-%d'), 'is_period': is_p, 
                            'period_range': p_rng, 'allowed_days': d_nms,
                            '건물명': str(item.get('buNm', '')).strip(), 
                            '장소': item.get('placeNm', '') or '-', 
                            '시간': f"{item.get('startTime', '')}~{item.get('endTime', '')}",
                            '행사명': item.get('eventNm', '') or '-', 
                            '부서': item.get('mgDeptNm', '') or '-', 
                            '인원': str(item.get('peopleCount', '0')), 
                            '상태': '확정' if item.get('status') == 'Y' else '대기'
                        })
                curr += timedelta(days=1)
        return pd.DataFrame(rows).drop_duplicates() if rows else pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 호출 오류: {e}")
        return pd.DataFrame()

# --- 3. 엑셀 출력 (기존 정식 서식 100% 복구) ---

def create_excel(df, selected_bu):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        ws = workbook.add_worksheet('현황')
        
        # 서식 정의 (변경 금지)
        title_f = workbook.add_format({'bold':True, 'size':16, 'align':'center', 'valign':'vcenter'})
        date_f = workbook.add_format({'bold':True, 'bg_color':'#343a40', 'font_color':'white', 'border':1, 'align':'center'})
        bu_f = workbook.add_format({'bold':True, 'bg_color':'#D9E1F2', 'font_color':'#1E3A5F', 'border':1, 'align':'left'})
        head_f = workbook.add_format({'bold':True, 'bg_color':'#F2F2F2', 'border':1, 'align':'center'})
        cell_f = workbook.add_format({'border':1, 'align':'center', 'valign':'vcenter', 'text_wrap':True})

        ws.set_column('A:A', 18); ws.set_column('B:B', 15); ws.set_column('C:C', 45); ws.set_column('D:D', 20)
        ws.merge_range('A1:F1', "성의교정 대관 현황 보고", title_f)
        
        row_num = 2
        for d_str in sorted(df['full_date'].unique()):
            ws.merge_range(row_num, 0, row_num, 5, f"📅 {d_str}", date_f); row_num += 1
            for bu in selected_bu:
                b_df = df[(df['full_date'] == d_str) & (df['건물명'].str.replace(" ","") == bu.replace(" ",""))]
                if b_df.empty: continue
                ws.merge_range(row_num, 0, row_num, 5, f"🏢 {bu}", bu_f); row_num += 1
                for i, h in enumerate(['장소', '시간', '행사명', '부서', '인원', '상태']): ws.write(row_num, i, h, head_f)
                row_num += 1
                for _, r in b_df.sort_values('시간').iterrows():
                    ev = f"{r['행사명']}\n({r['period_range']})" if r['is_period'] else r['행사명']
                    ws.write_row(row_num, 0, [r['장소'], r['시간'], ev, r['부서'], r['인원'], r['상태']], cell_f)
                    row_num += 1
                row_num += 1
    return output.getvalue()

# --- 4. 메인 화면 구성 ---

BUILDING_ORDER = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스파크 의과대학", "옴니버스파크 간호대학", "대학본관", "서울성모별관"]

st.markdown('<div class="main-title">🏫 성의교정 대관 관리 시스템</div>', unsafe_allow_html=True)

# 검색 바 (개선: Multiselect로 공간 절약)
with st.expander("🔍 조회 및 엑셀 출력", expanded=True):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        s_d = st.date_input("시작일", value=now_today)
        e_d = st.date_input("종료일", value=s_d)
    with col2:
        sel_bu = st.multiselect("건물 선택", options=BUILDING_ORDER, default=["성의회관", "의생명산업연구원"])
    with col3:
        mode = st.radio("보기", ["가로 표(PC)", "세로 카드(M)"], horizontal=True)
        df = get_data(s_d, e_d)
        if not df.empty:
            st.download_button("📊 엑셀 다운로드", create_excel(df, sel_bu), f"대관현황_{s_d}.xlsx", use_container_width=True)

# 데이터 표시
if not df.empty:
    curr = s_d
    while curr <= e_d:
        d_str = curr.strftime('%Y-%m-%d')
        day_df = df[df['full_date'] == d_str]
        if not day_df.empty:
            st.markdown(f'<div class="date-bar">📅 {d_str} ({"월화수목금토일"[curr.weekday()]}) | {get_shift(curr)}</div>', unsafe_allow_html=True)
            for bu in sel_bu:
                b_df = day_df[day_df['건물명'].str.replace(" ","") == bu.replace(" ","")]
                if b_df.empty: continue
                st.markdown(f'<div class="bu-header">🏢 {bu} ({len(b_df)}건)</div>', unsafe_allow_html=True)
                
                if "가로" in mode:
                    # 개선: HTML Table로 너비 고정 및 가시성 확보
                    table = '<table class="custom-table"><thead><tr><th style="width:15%">장소</th><th style="width:12%">시간</th><th style="width:38%">행사명</th><th style="width:15%">부서</th><th style="width:10%">인원</th><th style="width:10%">상태</th></tr></thead><tbody>'
                    for _, r in b_df.sort_values('시간').iterrows():
                        p_info = f'<span class="period-info">🗓️ {r["period_range"]} ({r["allowed_days"]})</span>' if r["is_period"] else ""
                        table += f"<tr><td>{r['장소']}</td><td style='color:#e74c3c; font-weight:bold;'>{r['시간']}</td><td class='event-cell'>{r['행사명']}{p_info}</td><td>{r['부서']}</td><td>{r['인원']}명</td><td>{r['상태']}</td></tr>"
                    st.markdown(table + "</tbody></table>", unsafe_allow_html=True)
                else:
                    for _, r in b_df.sort_values('시간').iterrows():
                        st.markdown(f'''<div class="mobile-card"><div class="m-row-1"><span class="m-loc">📍 {r['장소']}</span><span class="m-time">🕒 {r['시간']}</span></div><div style="font-size:14px;"><b>{r['행사명']}</b> / {r['부서']}</div>{f"<div style='color:#2196F3; font-size:11px; margin-top:5px;'>🗓️ {r['period_range']} ({r['allowed_days']})</div>" if r['is_period'] else ""}</div>''', unsafe_allow_html=True)
        curr += timedelta(days=1)
else:
    st.info("조회된 대관 내역이 없습니다.")
