import streamlit as st
import os
from dotenv import load_dotenv
from gmail_client import GmailClient
from classifier import SponsorshipClassifier
import pandas as pd

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="협찬 이메일 분류 시스템",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일
st.markdown("""
<style>
    /* Google Fonts - Noto Sans KR 임포트 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    /* 전체 폰트 적용 */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    /* 메인 타이틀 스타일 */
    h1 {
        color: #4A90E2 !important;
        font-weight: 700 !important;
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 서브 헤더 스타일 */
    h2, h3 {
        color: #5B7C99 !important;
        font-weight: 600 !important;
    }
    
    /* 카드 스타일 */
    .stContainer {
        background-color: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(74, 144, 226, 0.1);
        margin-bottom: 1rem;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E6F3FF 0%, #F0F8FF 100%);
    }
    
    /* 프로그레스 바 스타일 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 메트릭 스타일 */
    [data-testid="stMetricValue"] {
        color: #4A90E2;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Divider 스타일 */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #4A90E2, transparent);
    }
    
    /* 성공 메시지 스타일 */
    .stSuccess {
        background-color: #D4EDDA;
        border-left: 4px solid #28A745;
        border-radius: 8px;
    }
    
    /* 경고 메시지 스타일 */
    .stWarning {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        border-radius: 8px;
    }
    
    /* 에러 메시지 스타일 */
    .stError {
        background-color: #F8D7DA;
        border-left: 4px solid #DC3545;
        border-radius: 8px;
    }
    
    /* 정보 박스 스타일 */
    .stInfo {
        background-color: #D1ECF1;
        border-left: 4px solid #17A2B8;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 제목 및 설명
st.title("📧 인플루언서 협찬 이메일 분류 시스템")

# 소개 섹션
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
            padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;'>
    <p style='color: #5B7C99; font-size: 1.1rem; margin: 0; text-align: center;'>
        🤖 <strong>Gmail API</strong>와 <strong>Naver HyperCLOVA AI</strong>를 활용한 
        스마트 협찬 이메일 자동 분류 시스템
    </p>
</div>
""", unsafe_allow_html=True)

# 카테고리 소개
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; 
                box-shadow: 0 2px 10px rgba(74, 144, 226, 0.1); text-align: center;'>
        <h3 style='color: #52C41A; margin-top: 0;'>🟢 1단계</h3>
        <p style='color: #666;'>고정 금액만</p>
        <p style='font-size: 0.9rem; color: #999;'>영상 제작 시 고정 비용 지급</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; 
                box-shadow: 0 2px 10px rgba(74, 144, 226, 0.1); text-align: center;'>
        <h3 style='color: #FAAD14; margin-top: 0;'>🟡 2단계</h3>
        <p style='color: #666;'>고정 + 조회수</p>
        <p style='font-size: 0.9rem; color: #999;'>기본료 + 조회수 기반 추가 수익</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; 
                box-shadow: 0 2px 10px rgba(74, 144, 226, 0.1); text-align: center;'>
        <h3 style='color: #F5222D; margin-top: 0;'>🔴 3단계</h3>
        <p style='color: #666;'>고정 + 조회수 + 판매</p>
        <p style='font-size: 0.9rem; color: #999;'>복합 수익 구조</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


def initialize_clients():
    """클라이언트 초기화"""
    try:
        # Naver HyperCLOVA API 키 확인
        # .env 파일에서 CLOVA_STUDIO_KEY를 읽어옵니다
        # Naver Cloud Platform > CLOVA Studio > Playground에서 발급받으세요
        clova_api_key = os.getenv('CLOVA_STUDIO_KEY', 'nv-bf2506d5f74f4d0c921a472cb24d8c44tQby')
        
        if not clova_api_key:
            st.error("❌ Naver HyperCLOVA API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
            st.info("""
**필요한 환경 변수:**
- CLOVA_STUDIO_KEY (Naver CLOVA Studio API 키)

**API 키 발급 방법:**
1. https://www.ncloud.com/ 접속
2. CLOVA Studio 서비스 신청
3. 도메인 > API Key 관리에서 키 발급
            """)
            return None, None
        
        # Gmail 클라이언트 초기화
        gmail_client = GmailClient()
        
        # 분류기 초기화 (API 키만 전달, request_id는 내부에서 자동 생성)
        classifier = SponsorshipClassifier(clova_api_key)
        
        return gmail_client, classifier
    
    except FileNotFoundError as e:
        st.error(f"❌ {str(e)}")
        st.info("""
**Gmail API 설정 방법:**
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성
3. Gmail API 활성화
4. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)
5. credentials.json 파일 다운로드 후 프로젝트 루트에 저장
        """)
        return None, None
    
    except Exception as e:
        st.error(f"❌ 초기화 오류: {str(e)}")
        return None, None


def display_email_card(email, classification, explanation, details):
    """이메일 카드 UI (개선된 디자인)"""
    # 카테고리별 색상 및 라벨
    category_info = {
        'tier1': {'icon': '🟢', 'color': '#52C41A', 'label': '1단계', 'bg': '#F6FFED'},
        'tier2': {'icon': '🟡', 'color': '#FAAD14', 'label': '2단계', 'bg': '#FFFBE6'},
        'tier3': {'icon': '🔴', 'color': '#F5222D', 'label': '3단계', 'bg': '#FFF1F0'},
        'not_sponsorship': {'icon': '⚪', 'color': '#8C8C8C', 'label': '협찬 아님', 'bg': '#FAFAFA'},
        'unclear': {'icon': '🔵', 'color': '#1890FF', 'label': '불분명', 'bg': '#E6F7FF'}
    }
    
    info = category_info.get(classification, category_info['unclear'])
    
    # 카드 컨테이너
    st.markdown(f"""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; 
                box-shadow: 0 4px 15px rgba(74, 144, 226, 0.1); 
                margin-bottom: 1.5rem; border-left: 5px solid {info["color"]};'>
        <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
            <span style='font-size: 1.5rem; margin-right: 0.5rem;'>{info["icon"]}</span>
            <h3 style='margin: 0; color: #2C3E50; flex-grow: 1;'>{email['subject']}</h3>
            <span style='background: {info["bg"]}; color: {info["color"]}; 
                         padding: 0.3rem 1rem; border-radius: 20px; 
                         font-weight: 600; font-size: 0.9rem;'>{info["label"]}</span>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**👤 발신자:** {email['sender']}")
        st.markdown(f"**📅 날짜:** {email['date']}")
        
        with st.expander("📄 이메일 본문 보기"):
            body = email.get('body', email.get('snippet', ''))
            if len(body) > 1000:
                st.text(body[:1000] + "...")
            else:
                st.text(body)
    
    with col2:
        st.markdown(f"""
        <div style='background: {info["bg"]}; padding: 1rem; border-radius: 10px;'>
            <p style='margin: 0; color: {info["color"]}; font-weight: 600;'>📋 분류 결과</p>
            <p style='margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;'>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if details:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📊 상세 정보:**")
            for key, value in details.items():
                st.markdown(f"• **{key}:** {value}")
    
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    """메인 함수"""
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='color: #4A90E2; margin: 0;'>⚙️ 설정</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        max_emails = st.slider(
            "📊 가져올 이메일 수",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        search_query = st.text_input(
            "🔍 검색 쿼리 (선택사항)",
            placeholder="예: is:unread",
            help="Gmail 검색 문법을 사용할 수 있습니다"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fetch_button = st.button("📥 이메일 가져오기", type="primary", use_container_width=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: white; padding: 1rem; border-radius: 10px; 
                    box-shadow: 0 2px 8px rgba(74, 144, 226, 0.15);'>
            <h3 style='color: #4A90E2; margin-top: 0; text-align: center;'>📊 통계</h3>
        """, unsafe_allow_html=True)
        
        if 'classified_emails' in st.session_state:
            emails = st.session_state['classified_emails']
            
            # 카테고리별 개수
            tier1_count = sum(1 for e in emails if e['classification'] == 'tier1')
            tier2_count = sum(1 for e in emails if e['classification'] == 'tier2')
            tier3_count = sum(1 for e in emails if e['classification'] == 'tier3')
            
            st.metric("📧 총 이메일", len(emails))
            st.metric("🟢 1단계", tier1_count)
            st.metric("🟡 2단계", tier2_count)
            st.metric("🔴 3단계", tier3_count)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 메인 영역
    if fetch_button:
        with st.spinner("🔄 이메일을 가져오는 중..."):
            gmail_client, classifier = initialize_clients()
            
            if gmail_client is None or classifier is None:
                return
            
            # 협찬 관련 이메일 가져오기
            if search_query:
                emails = gmail_client.get_emails(query=search_query, max_results=max_emails)
            else:
                emails = gmail_client.search_sponsorship_emails(max_results=max_emails)
            
            if not emails:
                st.warning("⚠️ 검색된 이메일이 없습니다.")
                return
            
            st.success(f"✅ {len(emails)}개의 이메일을 가져왔습니다.")
        
        # 이메일 분류
        classified_emails = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        import time
        
        for i, email in enumerate(emails):
            status_text.text(f"분류 중... ({i+1}/{len(emails)})")
            
            # 분류 수행
            classification, explanation, details = classifier.classify_email(email)
            
            classified_emails.append({
                'email': email,
                'classification': classification,
                'explanation': explanation,
                'details': details
            })
            
            progress_bar.progress((i + 1) / len(emails))
            
            # API 제한 방지: 각 요청 사이에 1초 대기
            if i < len(emails) - 1:  # 마지막 요청 후에는 대기 안함
                time.sleep(1)
        
        status_text.empty()
        progress_bar.empty()
        
        # 세션 상태에 저장
        st.session_state['classified_emails'] = classified_emails
        
        st.success("✅ 모든 이메일 분류가 완료되었습니다!")
    
    # 분류된 이메일 표시
    if 'classified_emails' in st.session_state:
        classified_emails = st.session_state['classified_emails']
        
        # 필터 탭
        tab1, tab2, tab3, tab4 = st.tabs(["🟢 1단계", "🟡 2단계", "🔴 3단계", "📋 전체"])
        
        with tab1:
            st.header("1단계: 고정 금액만")
            tier1_emails = [e for e in classified_emails if e['classification'] == 'tier1']
            if tier1_emails:
                for item in tier1_emails:
                    display_email_card(
                        item['email'],
                        item['classification'],
                        item['explanation'],
                        item['details']
                    )
            else:
                st.info("해당하는 이메일이 없습니다.")
        
        with tab2:
            st.header("2단계: 고정 금액 + 조회수 수익")
            tier2_emails = [e for e in classified_emails if e['classification'] == 'tier2']
            if tier2_emails:
                for item in tier2_emails:
                    display_email_card(
                        item['email'],
                        item['classification'],
                        item['explanation'],
                        item['details']
                    )
            else:
                st.info("해당하는 이메일이 없습니다.")
        
        with tab3:
            st.header("3단계: 고정 금액 + 조회수 + 판매 수수료")
            tier3_emails = [e for e in classified_emails if e['classification'] == 'tier3']
            if tier3_emails:
                for item in tier3_emails:
                    display_email_card(
                        item['email'],
                        item['classification'],
                        item['explanation'],
                        item['details']
                    )
            else:
                st.info("해당하는 이메일이 없습니다.")
        
        with tab4:
            st.header("전체 이메일")
            for item in classified_emails:
                display_email_card(
                    item['email'],
                    item['classification'],
                    item['explanation'],
                    item['details']
                )
        
        # CSV 다운로드 기능
        if st.button("📥 결과를 CSV로 다운로드"):
            # DataFrame 생성
            data = []
            for item in classified_emails:
                email = item['email']
                data.append({
                    '제목': email['subject'],
                    '발신자': email['sender'],
                    '날짜': email['date'],
                    '분류': item['classification'],
                    '설명': item['explanation'],
                    '상세정보': str(item['details'])
                })
            
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="CSV 파일 다운로드",
                data=csv,
                file_name="sponsorship_classification.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()

