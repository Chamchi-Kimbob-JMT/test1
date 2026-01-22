# teacher.py
# 교사용 대시보드 - Supabase에 저장된 학생 답안 및 피드백 조회
# --------------------------------------------------

import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# ── Supabase 클라이언트 초기화 ──
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)

# ── 페이지 설정 ──
st.set_page_config(
    page_title="교사용 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📊 교사용 학생 답안 관리 대시보드")
st.markdown("---")

# ── 사이드바: 필터 옵션 ──
with st.sidebar:
    st.header("🔍 필터 옵션")
    
    # 학번 검색
    search_student_id = st.text_input("학번으로 검색", placeholder="예: 10130")
    
    # 정렬 옵션
    sort_option = st.selectbox(
        "정렬 기준",
        ["최신순", "학번 오름차순", "학번 내림차순"]
    )
    
    # 새로고침 버튼
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

# ── 데이터 로드 함수 ──
@st.cache_data(ttl=60)
def load_submissions():
    """Supabase에서 학생 제출 데이터 불러오기"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("student_submissions").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return []

# ── 데이터 로드 ──
data = load_submissions()

if not data:
    st.warning("⚠️ 제출된 답안이 없습니다.")
    st.stop()

# ── DataFrame 변환 ──
df = pd.DataFrame(data)

# created_at을 datetime으로 변환
if 'created_at' in df.columns:
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['제출일시'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')

# ── 필터 적용 ──
if search_student_id.strip():
    df = df[df['student_id'].astype(str).str.contains(search_student_id.strip())]

# 정렬 적용
if sort_option == "최신순":
    df = df.sort_values('created_at', ascending=False)
elif sort_option == "학번 오름차순":
    df = df.sort_values('student_id', ascending=True)
elif sort_option == "학번 내림차순":
    df = df.sort_values('student_id', ascending=False)

# ── 통계 요약 ──
st.subheader("📈 제출 현황 요약")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("총 제출 건수", len(df))
with col2:
    st.metric("제출 학생 수", df['student_id'].nunique())
with col3:
    if 'created_at' in df.columns:
        latest = df['created_at'].max().strftime('%Y-%m-%d %H:%M')
        st.metric("최근 제출", latest)
with col4:
    # 간단한 정답률 계산 (O: 로 시작하는 피드백 비율)
    total_answers = len(df) * 3  # 문항 3개
    correct_count = 0
    for col in ['feedback_1', 'feedback_2', 'feedback_3']:
        if col in df.columns:
            correct_count += df[col].astype(str).str.startswith('O:').sum()
    if total_answers > 0:
        accuracy = (correct_count / total_answers) * 100
        st.metric("전체 정답률", f"{accuracy:.1f}%")

st.markdown("---")

# ── 학생별 답안 목록 ──
st.subheader("📋 학생 답안 목록")

# 간단한 테이블 표시
display_df = df[['student_id', '제출일시']].copy() if '제출일시' in df.columns else df[['student_id']].copy()
display_df = display_df.rename(columns={'student_id': '학번'})

st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── 상세 답안 보기 ──
st.markdown("---")
st.subheader("🔍 상세 답안 조회")

# 학번 선택
student_ids = sorted(df['student_id'].unique())
selected_student = st.selectbox("조회할 학번 선택", student_ids)

if selected_student:
    # 해당 학생의 제출 내역 (최신순)
    student_data = df[df['student_id'] == selected_student].sort_values('created_at', ascending=False)
    
    if len(student_data) > 1:
        st.info(f"💡 해당 학생은 {len(student_data)}건의 제출 내역이 있습니다. 최신 제출 내역을 표시합니다.")
    
    # 최신 제출 데이터
    latest_submission = student_data.iloc[0]
    
    # 제출 정보
    st.markdown(f"**학번:** {latest_submission['student_id']}")
    if '제출일시' in latest_submission:
        st.markdown(f"**제출일시:** {latest_submission['제출일시']}")
    if 'model' in latest_submission:
        st.markdown(f"**사용 모델:** {latest_submission['model']}")
    
    st.markdown("---")
    
    # 문항별 답안 및 피드백 표시
    questions = {
        1: "기체 입자들의 운동과 온도의 관계를 서술하세요.",
        2: "보일 법칙에 대해 설명하세요.",
        3: "열에너지 이동 3가지 방식(전도·대류·복사)을 설명하세요."
    }
    
    for q_num in [1, 2, 3]:
        answer_col = f'answer_{q_num}'
        feedback_col = f'feedback_{q_num}'
        guideline_col = f'guideline_{q_num}'
        
        st.markdown(f"### 📝 문항 {q_num}")
        st.markdown(f"**문제:** {questions[q_num]}")
        
        # 채점 기준
        if guideline_col in latest_submission and pd.notna(latest_submission[guideline_col]):
            with st.expander("채점 기준 보기"):
                st.info(latest_submission[guideline_col])
        
        # 학생 답안
        if answer_col in latest_submission and pd.notna(latest_submission[answer_col]):
            st.markdown("**학생 답안:**")
            st.text_area(
                f"답안_{q_num}",
                latest_submission[answer_col],
                height=100,
                disabled=True,
                label_visibility="collapsed"
            )
        
        # AI 피드백
        if feedback_col in latest_submission and pd.notna(latest_submission[feedback_col]):
            feedback = latest_submission[feedback_col]
            if feedback.startswith('O:'):
                st.success(f"**AI 피드백:** {feedback}")
            else:
                st.warning(f"**AI 피드백:** {feedback}")
        
        st.markdown("---")

# ── 전체 데이터 다운로드 ──
st.subheader("💾 데이터 내보내기")

# CSV 다운로드 버튼
csv = df.to_csv(index=False).encode('utf-8-sig')  # 한글 깨짐 방지
st.download_button(
    label="📥 전체 데이터 CSV 다운로드",
    data=csv,
    file_name=f"student_submissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# ── 푸터 ──
st.markdown("---")
st.caption("💡 Tip: 사이드바의 '데이터 새로고침' 버튼으로 최신 제출 내역을 확인하세요.")
