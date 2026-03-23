import streamlit as st
import anthropic

# 페이지 기본 설정
st.set_page_config(
    page_title="특수교육 전문가 챗봇",
    page_icon="🎓",
    layout="centered"
)

# 커스텀 CSS 스타일
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        color: white;
    }
    .main-header h1 {
        font-size: 1.8rem;
        margin: 0;
        padding: 0;
    }
    .main-header p {
        font-size: 0.95rem;
        margin: 8px 0 0 0;
        opacity: 0.9;
    }
    .info-box {
        background-color: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        color: #333;
    }
    .stChatMessage {
        border-radius: 10px;
    }
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #4a4a8a;
        margin-bottom: 10px;
    }
    .tip-box {
        background-color: #fff8e1;
        border: 1px solid #ffe082;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #555;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 시스템 프롬프트 정의
SYSTEM_PROMPT = """당신은 20년 이상의 경력을 가진 특수교육 전문가입니다.
특수학생 지도에 어려움을 겪고 있는 일반 교사들에게 실질적이고 전문적인 도움을 제공하는 것이 당신의 역할입니다.

## 전문 영역
- 자폐 스펙트럼 장애(ASD) 학생 지도법
- 주의력결핍 과잉행동장애(ADHD) 학생 지도법
- 학습장애(LD) 학생 지도법
- 지적장애 학생 지도법
- 정서·행동장애 학생 지도법
- 감각처리장애 학생 지도법
- 통합교육 환경에서의 지도 전략
- 개별화교육프로그램(IEP) 작성 지원
- 보조공학기기 활용 방법
- 부모·보호자와의 협력 방안

## 응답 원칙
1. **공감 우선**: 교사의 어려움과 고충에 먼저 공감하고 정서적 지지를 제공하세요.
2. **실용적 조언**: 즉시 교실에서 적용할 수 있는 구체적이고 실용적인 전략을 제시하세요.
3. **개별화 접근**: 모든 특수학생은 고유한 특성을 가지므로, 학생의 특성에 맞는 맞춤형 방법을 안내하세요.
4. **단계적 설명**: 복잡한 내용은 단계별로 나누어 이해하기 쉽게 설명하세요.
5. **긍정적 접근**: 학생의 강점을 활용하는 긍정적 행동 지원(PBS) 관점을 유지하세요.
6. **법적·제도적 안내**: 필요시 특수교육법, 지원 체계, 전문기관 연계 방법도 안내하세요.
7. **한국 교육 맥락**: 한국의 교육 제도와 환경에 맞는 현실적인 조언을 제공하세요.

## 응답 형식
- 명확한 소제목과 번호 목록을 활용하여 읽기 쉽게 구성하세요.
- 핵심 전략은 **굵은 글씨**로 강조하세요.
- 필요한 경우 실제 사례나 예시를 들어 이해를 도우세요.
- 응답은 너무 길지 않게 핵심 내용 위주로 작성하되, 필요한 경우 추가 질문을 유도하세요.
- 항상 따뜻하고 지지적인 어조를 유지하세요.

교사가 자신감을 갖고 특수학생을 효과적으로 지도할 수 있도록 실질적인 도움을 주세요."""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key_confirmed" not in st.session_state:
    st.session_state.api_key_confirmed = False

# 메인 헤더
st.markdown("""
    <div class="main-header">
        <h1>🎓 특수교육 전문가 AI 상담봇</h1>
        <p>특수학생 지도에 어려움이 있는 선생님들을 위한 전문 상담 서비스</p>
    </div>
""", unsafe_allow_html=True)

# 사이드바 구성
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ 설정</div>', unsafe_allow_html=True)

    # API 키 입력
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Anthropic에서 발급받은 API 키를 입력하세요."
    )

    if api_key:
        if api_key.startswith("sk-ant-"):
            st.success("✅ API 키가 입력되었습니다.")
            st.session_state.api_key_confirmed = True
        else:
            st.error("❌ 올바른 API 키 형식이 아닙니다.")
            st.session_state.api_key_confirmed = False
    else:
        st.session_state.api_key_confirmed = False

    st.divider()

    # 상담 주제 빠른 선택
    st.markdown('<div class="sidebar-title">📋 상담 주제 예시</div>', unsafe_allow_html=True)

    example_questions = {
        "🧩 자폐 스펙트럼": "자폐 스펙트럼 장애 학생이 수업 중 갑자기 소리를 지르는 경우 어떻게 대처해야 하나요?",
        "⚡ ADHD 집중력": "ADHD 학생의 수업 집중력을 높이는 방법이 있을까요?",
        "📚 학습장애": "학습장애 학생을 위한 읽기 지도 방법을 알려주세요.",
        "😤 행동 문제": "수업 방해 행동이 잦은 학생을 어떻게 지도해야 할까요?",
        "👨‍👩‍👧 부모 협력": "특수학생 학부모와 효과적으로 소통하는 방법을 알고 싶어요.",
        "📝 IEP 작성": "개별화교육프로그램(IEP) 목표 작성 방법을 알려주세요.",
        "🤝 통합교육": "통합학급에서 특수학생과 일반학생이 함께 어울리는 활동을 제안해 주세요.",
        "🧠 감각처리": "감각 자극에 매우 민감한 학생을 위한 환경 구성 방법은?"
    }

    for label, question in example_questions.items():
        if st.button(label, use_container_width=True, key=f"btn_{label}"):
            if st.session_state.api_key_confirmed:
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
            else:
                st.warning("먼저 API 키를 입력해 주세요.")

    st.divider()

    # 대화 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

    # 도움말
    st.markdown("""
        <div class="tip-box">
        💡 <strong>활용 팁</strong><br>
        학생의 장애 유형, 학년, 구체적인 상황을 함께 알려주시면 더욱 맞춤화된 조언을 받으실 수 있어요.
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("Powered by Claude claude-sonnet-4-6")
    st.caption("© 2025 특수교육 AI 상담봇")

# 메인 화면 안내 메시지 (대화 없을 때)
if not st.session_state.messages:
    st.markdown("""
        <div class="info-box">
        👋 안녕하세요! 저는 특수교육 전문가 AI입니다.<br>
        특수학생 지도에 관한 어떤 고민이든 편하게 질문해 주세요.
        왼쪽 사이드바에서 빠른 상담 주제를 선택하거나, 아래 채팅창에 직접 질문하실 수 있습니다.
        </div>
    """, unsafe_allow_html=True)

    # 안내 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🧩 **장애 유형별**\n\n자폐, ADHD, 학습장애 등 다양한 장애 유형에 맞는 지도법")
    with col2:
        st.info("🏫 **교실 적용**\n\n즉시 활용 가능한 실용적인 수업 전략과 환경 구성 팁")
    with col3:
        st.info("🤝 **협력 방안**\n\n학부모, 특수교사, 전문기관과의 효과적인 협력 방법")

# 대화 내역 표시
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👩‍🏫"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(message["content"])

# 챗 입력 및 응답 처리
if prompt := st.chat_input("특수학생 지도에 대해 궁금한 점을 질문해 주세요..."):
    if not st.session_state.api_key_confirmed:
        st.warning("⚠️ 먼저 사이드바에서 Anthropic API 키를 입력해 주세요.")
        st.stop()

    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👩‍🏫"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("전문가 답변을 생성하는 중입니다..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)

                # 메시지 목록 구성
                messages_for_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                # 스트리밍 응답
                response_text = ""
                response_placeholder = st.empty()

                with client.messages.stream(
                    model="claude-sonnet-4-5",
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    messages=messages_for_api
                ) as stream:
                    for text_chunk in stream.text_stream:
                        response_text += text_chunk
                        response_placeholder.markdown(response_text + "▌")

                # 최종 응답 표시 (커서 제거)
                response_placeholder.markdown(response_text)

                # 응답 세션에 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })

            except anthropic.AuthenticationError:
                st.error("❌ API 키 인증에 실패했습니다. API 키를 다시 확인해 주세요.")
            except anthropic.RateLimitError:
                st.error("⚠️ API 요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
            except anthropic.APIConnectionError:
                st.error("🌐 네트워크 연결 오류가 발생했습니다. 인터넷 연결을 확인해 주세요.")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")