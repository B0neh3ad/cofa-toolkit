# 개별 도구 선택 카탈로그

폴더명으로 `scripts/setup.py --skill 이름`을 선택합니다. source는 실제 가져온 저장소입니다.
내부 Skill은 파일·터미널 기반이며 선택한 과제의 기존 도구와 함께 사용할 수 있습니다.

| Skill | 쓸 상황 | 출처·비용/제약 |
|---|---|---|
| domain-discovery | 생소한 용어·규칙을 근거와 수용 사례로 확정 | toolkit; 도메인 선입견 없이 시작 |
| data-quality | CSV·JSON·DB·측정 데이터의 의미·품질·집계 검증 | toolkit; 원본 보존과 전체/표본 구분 |
| systematic-debugging | 반복 실패의 원인 조사와 최소 수정 | Superpowers; 전체 참고 자료를 매번 읽을 필요 없음 |
| verification-before-completion | 완료 주장 전 실제 실행 확인 | Superpowers; 불필요한 전체 재검증보다 변경 관련 검증 |
| test-driven-development | 로직의 기대 동작을 먼저 검증 | Superpowers; 의미 있는 검증에 적용 |
| dispatching-parallel-agents | 독립 조사·결함을 병렬로 분배 | Superpowers; 제공된 subagent가 필요 |
| requesting-code-review | 안정된 코드 상태의 검토 요청 | Superpowers; 코드 상태·검토 범위를 지정 |
| receiving-code-review | 검토 의견의 근거를 판단하고 반영 | Superpowers; 모든 제안을 무조건 수용하지 않음 |
| using-git-worktrees | 여러 쓰기 작업의 파일 공간 분리 | Superpowers; Git·커밋 기준·허용 경로 확인 |
| writing-plans | 여러 단계의 구현 계획 | Superpowers; 짧은 과제에 과도한 계획 문서 금지 |
| executing-plans | 정해진 계획을 검증 단위로 실행 | Superpowers; 현재 과제의 승인 범위를 따름 |
| subagent-driven-development | 구현·명세·리뷰 역할을 나누는 절차 | Superpowers; 역할 수와 검토 비용이 클 수 있음 |
| brainstorming | 목표와 설계 대안이 덜 정해진 작업 | Superpowers; README가 명확하면 짧게, 시험에서는 텍스트 설계 |
| finishing-a-development-branch | 일반 개발의 Git 마무리 선택지 | Superpowers; 시험 중 외부 push·발행·임의 삭제는 제외 |
| frontend-design | 목적에 맞는 UI·시각적 구성 | Anthropic; 실제 업무 사용성과 기존 디자인 우선 |
| doc-coauthoring | 명세·의사결정·사용 문서 작성 | Anthropic; Claude/다른 서비스 단계는 제공 Codex와 파일로 대체 |
| react-best-practices | React/Next.js 비동기·성능·렌더링 검토 | Vercel; 해당 스택일 때만 규칙 참고 |
| composition-patterns | 복잡한 React 컴포넌트 인터페이스 정리 | Vercel; 작은 UI에 불필요한 추상화 금지 |
| pdf | PDF 읽기·생성·레이아웃 검토 | OpenAI; pypdf/reportlab/Poppler 등 필요한 의존성 확인 |
| jupyter-notebook | 데이터 탐색·실험·재현 가능한 노트북 | OpenAI; 템플릿·생성 스크립트 포함, 실행 환경은 별도 확인 |
| security-best-practices | 언어·프레임워크별 보안 기본값 | OpenAI; 지원되는 언어의 참고 문서 선택 |
| security-threat-model | 자산·경계·위협·완화책 정리 | OpenAI; 실제 외부 경계와 위험에 맞춰 사용 |
| differential-review | 변경 전후의 위험·영향 검토 | Trail of Bits; 대규모 감사보다 현재 diff부터 |
| modern-python | Python 프로젝트 도구 구성 | Trail of Bits; Python 3.11+ 중심, 기존 스택을 자동 교체하지 않음 |
| property-based-testing | 파서·변환·집계 등의 불변조건 검증 | Trail of Bits; Hypothesis 등은 필요할 때 설치 |
| sharp-edges | 실수하기 쉬운 API·위험한 기본값 검토 | Trail of Bits; 보안·설정 경계가 있을 때 |
| audit-context-building | 낯선 큰 코드의 함수·흐름 파악 | Trail of Bits; 정밀 분석 비용이 큼 |
| dimensional-analysis | 단위·정밀도·배율의 수치 코드 감사 | Trail of Bits; 원본은 DeFi 사례와 전체 분석 파이프라인 중심 |
| evidence-check | 요구와 실제 실행 근거를 연결 | toolkit; 검증 종류와 미실행을 구분 |
| explain-artifact | 실제 구조·선택 이유·한계를 설명 | toolkit; AI 허용 단계에서만 사용 |
| session-handoff | 다음 세션의 재개 지점 저장 | toolkit; 파일과 작업 기록을 대조 |
| parallel-delivery | 마감 시간·소유 파일·통합 순서를 관리 | toolkit; subagent와 worktree를 구분 |

## 전문 도메인에서 선택하기

특정 산업용 규칙을 정답으로 가져오지 않습니다. 첫 입력의 용어·단위·상태·시간 기준과
성공 조건을 확인한 뒤 필요한 도구를 붙입니다. 문서 중심이면 pdf/doc-coauthoring,
데이터 중심이면 data-quality/notebook/property-based-testing, 수치 계산이면 단위와
정밀도 검토, 기존 코드 수정이면 systematic-debugging/differential-review부터 선택합니다.
DBHub는 실제 데이터 조회, Context7은 소프트웨어 문서 조회용입니다. 둘 다 업무 규칙의 근거를 대신하지 않습니다.

## 템플릿 선택하기

| 필요 | 템플릿 |
|---|---|
| 공통 지침·현재 목표·인계 | AGENTS.md, WORKLOG.md |
| 낯선 용어·정책·데이터 | DOMAIN_BRIEF.md, DATA_CONTRACT.md |
| 작업·의존성·병렬 계약 | TASKS.md, CONTRACT.md, PARALLEL_PLAN.md, WORKER_BRIEF.md |
| 판단과 AI 기여·검토 | DECISIONS.md, AI_COLLABORATION.md, REVIEW.md |
| 실행·환경·최종 설명 | ENVIRONMENT.md, CHECKS.json, DELIVERY.md |
| Git 제외 패턴 참고 | gitignore.example |
| 장문 명세·계획의 원본 참고 | vendor/spec-kit의 5개 템플릿 |

템플릿은 선택해서 채우는 문서입니다. 예시 경로·치환자·빈 검증을 실제 구현이나 실행 결과처럼 제출하지 않습니다.
