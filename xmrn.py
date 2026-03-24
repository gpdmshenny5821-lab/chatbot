import streamlit as st
import anthropic

# ── 페이지 기본 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="특수교육 전문가 챗봇",
    page_icon="🎓",
    layout="centered",
)

# ── 시스템 프롬프트 ───────────────────────────────────────────────
SYSTEM_PROMPT = """
당신은 20년 이상의 경험을 가진 특수교육 전문가입니다.
장애를 가진 특수학생을 담당하거나 통합학급에서 가르치는 일반 교사들에게
실질적이고 전문적인 지도 조언을 제공하는 것이 당신의 역할입니다.

【전문 분야】
- 발달장애(자폐스펙트럼장애, 지적장애)
- 학습장애(난독증, 난산증, 쓰기장애)
- 주의력결핍 과잉행동장애(ADHD)
- 지체장애 및 건강장애
- 시각장애 및 청각장애
- 정서·행동장애
- 언어장애
- 중복장애

【조언 원칙】
1. **개별화 접근**: 장애 유형과 학생의 개별 특성을 고려한 맞춤형 지도법을 제안합니다.
2. **근거 기반**: 특수교육 연구와 실증된 교육 방법론(ABA, PBIS, UDL 등)을 바탕으로 조언합니다.
3. **실용성 중시**: 일반 학급 환경에서 즉시 적용 가능한 구체적인 전략을 제시합니다.
4. **긍정적 접근**: 학생의 강점과 가능성에 초점을 맞춘 긍정적 행동 지원을 강조합니다.
5. **협력 강조**: 학부모, 특수교사, 관련 서비스 제공자와의 협력 방안을 안내합니다.
6. **법적·윤리적 기준**: 특수교육법 및 관련 법규를 준수한 조언을 제공합니다.

【응답 형식】
- 교사가 이해하기 쉽도록 명확하고 구체적으로 설명합니다.
- 필요 시 단계별 지도 방법을 번호 목록으로 제시합니다.
- 주의사항이나 추가 고려사항은 별도로 안내합니다.
- 전문 용어 사용 시 간단한 설명을 함께 제공합니다.
- 심각한 문제(자해, 타해 등)의 경우 전문가 협력과 즉각적인 지원을 권고합니다.

항상 따뜻하고 공감적인 태도로 교사의 어려움을 이해하며 실질적인 도움을 제공하세요.
"""

# ── 사이드바: API 키 및 앱 정보 ───────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/teacher.png", width=80)
    st.title("⚙️ 설정")

    api_key = st.text_input(
        "Anthropic API 키",
        type="password",
        placeholder="sk-ant-...",
        help="Anthropic 콘솔(console.anthropic.com)에서 발급받은 API 키를 입력하세요.",
    )

    st.divider()

    st.markdown("### 📌 이런 질문을 해보세요")
    example_questions = [
        "자폐 학생이 수업 중 갑자기 소리를 지르면 어떻게 해야 하나요?",
        "ADHD 학생의 집중력을 높이는 방법이 있나요?",
        "지적장애 학생에게 읽기를 가르치는 방법은?",
        "통합학급에서 장애 학생과 비장애 학생이 함께 활동하려면?",
        "학습장애 학생의 시험 지원 방법은 무엇인가요?",
    ]
    for q in example_questions:
        st.markdown(f"- {q}")

    st.divider()

    st.markdown("### ℹ️ 앱 정보")
    st.info(
        "이 챗봇은 특수교육 전문 AI로, "
        "장애 학생을 지도하는 일반 교사를 위한 "
        "실질적인 교육 조언을 제공합니다.\n\n"
        "⚠️ 긴급 상황에서는 반드시 학교 특수교사 "
        "또는 전문가와 즉시 협력하세요."
    )

    st.divider()

    st.markdown("### 🔧 모델 정보")
    st.caption("사용 모델: Claude Haiku 4.5 (2025-10-01)\n빠르고 효율적인 응답 제공")

    # 대화 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── 메인 화면 헤더 ────────────────────────────────────────────────
st.title("🎓 특수교육 전문가 챗봇")
st.caption("장애 학생 지도에 어려움을 겪는 선생님들을 위한 AI 특수교육 전문가 상담 서비스")

st.markdown(
    """
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 16px 20px; border-radius: 12px; color: white; margin-bottom: 20px;'>
        <b>👋 안녕하세요, 선생님!</b><br>
        저는 특수교육 전문 AI 상담사입니다. 담당 학생의 장애 유형, 학년, 구체적인 상황을
        알려주시면 더욱 맞춤화된 조언을 드릴 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 세션 상태 초기화 ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 이전 대화 출력 ────────────────────────────────────────────────
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👩‍🏫"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(message["content"])

# ── 사용자 입력 처리 ──────────────────────────────────────────────
if prompt := st.chat_input("학생 지도 관련 질문을 입력하세요... (예: ADHD 학생이 수업 중 돌아다녀요)"):

    # API 키 확인
    if not api_key:
        st.warning("⚠️ 사이드바에서 Anthropic API 키를 먼저 입력해주세요.")
        st.stop()

    # 사용자 메시지 저장 및 출력
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👩‍🏫"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant", avatar="🎓"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            client = anthropic.Anthropic(api_key=api_key)

            # 스트리밍 방식으로 API 호출
            with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            ) as stream:
                for text_chunk in stream.text_stream:
                    full_response += text_chunk
                    response_placeholder.markdown(full_response + "▌")

            # 최종 응답 출력 (커서 제거)
            response_placeholder.markdown(full_response)

        except anthropic.AuthenticationError:
            full_response = "❌ API 키가 올바르지 않습니다. 사이드바에서 유효한 API 키를 입력해주세요."
            response_placeholder.error(full_response)

        except anthropic.RateLimitError:
            full_response = "⏳ API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
            response_placeholder.warning(full_response)

        except anthropic.APIConnectionError:
            full_response = "🌐 네트워크 연결 오류가 발생했습니다. 인터넷 연결을 확인해주세요."
            response_placeholder.error(full_response)

        except Exception as e:
            full_response = f"⚠️ 예기치 않은 오류가 발생했습니다: {str(e)}"
            response_placeholder.error(full_response)

    # 어시스턴트 응답 저장
    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

# ── 하단 안내 ─────────────────────────────────────────────────────
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💬 대화 횟수", len([m for m in st.session_state.messages if m["role"] == "user"]))

with col2:
    if st.session_state.messages:
        st.metric("⚡ 모델", "Haiku 4.5")
    else:
        st.metric("⚡ 모델", "Haiku 4.5")

with col3:
    st.metric("📊 상태", "정상")

st.markdown(
    "<div style='text-align:center; color:gray; font-size:13px; margin-top:20px;'>"
    "🏫 본 서비스는 교육적 참고 목적으로 제공됩니다. "
    "긴급하거나 심각한 상황은 반드시 학교 특수교사 및 전문가와 협력하세요."
    "</div>",
    unsafe_allow_html=True,
)
