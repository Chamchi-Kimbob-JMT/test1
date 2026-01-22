# teacher_test.py (임시 테스트용)
import streamlit as st

st.title("🔍 Supabase 연결 테스트")

try:
    # Secrets 확인
    st.write("### 1. Secrets 파일 확인")
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    st.success("✅ Secrets 파일 로드 성공")
    st.write(f"URL: {url[:30]}...")
    st.write(f"KEY: {key[:20]}...")
    
except KeyError as e:
    st.error(f"❌ Secrets 오류: {e}")
    st.stop()

try:
    # Supabase 연결
    st.write("### 2. Supabase 연결 시도")
    from supabase import create_client
    
    supabase = create_client(url, key)
    st.success("✅ Supabase 클라이언트 생성 성공")
    
except Exception as e:
    st.error(f"❌ Supabase 연결 실패: {e}")
    st.stop()

try:
    # 데이터 조회
    st.write("### 3. 데이터 조회 시도")
    response = supabase.table("student_submissions").select("*").limit(5).execute()
    
    st.success(f"✅ 데이터 조회 성공! (총 {len(response.data)}건)")
    st.write(response.data)
    
except Exception as e:
    st.error(f"❌ 데이터 조회 실패: {e}")
    st.write("**가능한 원인:**")
    st.write("- 테이블 이름이 'student_submissions'가 아님")
    st.write("- RLS(Row Level Security) 정책 때문에 접근 불가")
    st.write("- 테이블에 데이터가 아직 없음")
