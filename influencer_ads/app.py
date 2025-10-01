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
    layout="wide"
)

# 제목 및 설명
st.title("📧 인플루언서 협찬 이메일 분류 시스템")
st.markdown("""
이 시스템은 Gmail API와 Naver HyperCLOVA를 활용하여 협찬 요청 이메일을 자동으로 분류합니다.

### 분류 카테고리
- **1단계**: 고정 금액만 (영상 제작 및 게시)
- **2단계**: 고정 금액 + 조회수 기반 수익
- **3단계**: 고정 금액 + 조회수 수익 + 제품 판매 수수료
""")

st.divider()


def initialize_clients():
    """클라이언트 초기화"""
    try:
        # Naver HyperCLOVA API 키 확인
        # .env 파일에서 CLOVA_STUDIO_KEY를 읽어옵니다
        # Naver Cloud Platform > CLOVA Studio > 도메인 > API Key 관리에서 발급받으세요
        clova_api_key = os.getenv('CLOVA_STUDIO_KEY', 'nv-6aa7bad6cfa749f08dd3eb7bdc234578FAhq')
        
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
    """이메일 카드 UI"""
    # 카테고리별 색상
    category_colors = {
        'tier1': '🟢',
        'tier2': '🟡',
        'tier3': '🔴',
        'not_sponsorship': '⚪',
        'unclear': '🔵'
    }
    
    color = category_colors.get(classification, '⚪')
    
    with st.container():
        st.markdown(f"### {color} {email['subject']}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**발신자:** {email['sender']}")
            st.markdown(f"**날짜:** {email['date']}")
            
            with st.expander("📄 이메일 본문 보기"):
                body = email.get('body', email.get('snippet', ''))
                if len(body) > 1000:
                    st.text(body[:1000] + "...")
                else:
                    st.text(body)
        
        with col2:
            st.markdown(f"**분류:** {classification.upper()}")
            st.markdown(f"**설명:** {explanation}")
            
            if details:
                st.markdown("**상세 정보:**")
                for key, value in details.items():
                    st.markdown(f"- {key}: {value}")
        
        st.divider()


def main():
    """메인 함수"""
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        max_emails = st.slider(
            "가져올 이메일 수",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        search_query = st.text_input(
            "검색 쿼리 (선택사항)",
            placeholder="예: is:unread",
            help="Gmail 검색 문법을 사용할 수 있습니다"
        )
        
        fetch_button = st.button("📥 이메일 가져오기", type="primary", use_container_width=True)
        
        st.divider()
        
        st.markdown("""
        ### 📊 통계
        """)
        
        if 'classified_emails' in st.session_state:
            emails = st.session_state['classified_emails']
            st.metric("총 이메일", len(emails))
            
            # 카테고리별 개수
            tier1_count = sum(1 for e in emails if e['classification'] == 'tier1')
            tier2_count = sum(1 for e in emails if e['classification'] == 'tier2')
            tier3_count = sum(1 for e in emails if e['classification'] == 'tier3')
            
            st.metric("1단계", tier1_count)
            st.metric("2단계", tier2_count)
            st.metric("3단계", tier3_count)
    
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

