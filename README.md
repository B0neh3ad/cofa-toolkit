# Cofa 시험용 선택형 툴킷 v4

낯선 도메인의 요구 파악부터 구현·데이터 검증·설명까지 필요한 자료를 골라 씁니다.
**Skill 32개, MCP 6개, 프로젝트 템플릿 15개와 Spec Kit 원본 템플릿 5개**를 담았습니다.
연습 과제·데모 웹페이지·CSV 예제·워크트리 실습은 제거했습니다.
`tests/`는 툴킷 자체의 회귀 검증이며 연습 문제가 아닙니다.

## 시험 초반 설정

플랫폼 안의 허용된 터미널에서 이 공개 저장소를 가져옵니다. 실제 과제 루트를 확인하고,
기존 파일과 README를 보존합니다. 아래 명령은 **툴킷 루트에서** 실행합니다.

```sh
python3 scripts/setup.py --list
python3 scripts/setup.py --target /실제/과제/루트 --profile core --profile domain --template AGENTS.md --template WORKLOG.md
```

- `--target`은 이미 존재하는 실제 과제 폴더입니다. 예시 경로를 실제 값으로 바꾸세요.
- 선택한 Skill만 대상의 `.agents/skills/`에 복사합니다. 기존 파일은 덮어쓰지 않습니다.
- `skipped-existing`인 AGENTS/WORKLOG는 Codex에게 원래 규칙과 요구를 보존하며 필요한 내용만 합치게 합니다.
- Skill은 다음 턴에 발견되는지 `/skills`로 확인합니다. 해당 버전에서 보이지 않으면 새 세션이나 파일 경로 읽기를 사용합니다.
- AGENTS 수정은 현재 세션에서 명시적으로 읽게 하거나 새 세션에서 확인합니다.
- MCP·Python 패키지·전역 설정·제공 도구 버전은 이 명령으로 바꾸지 않습니다.

원하는 것만 개별 선택하거나 프로필을 추가할 수 있습니다.

```sh
python3 scripts/setup.py --target /실제/과제/루트 --skill data-quality --skill pdf --template DATA_CONTRACT.md
python3 scripts/setup.py --target /실제/과제/루트 --profile web --profile quality --dry-run
python3 scripts/setup.py --target /실제/과제/루트 --all-skills --dry-run
```

모든 자료는 저장소에 준비되어 있지만 전체 활성화는 선택입니다. 큰 참고 문서는 필요한 부분만 읽습니다.
3시간 과제에서 전체 감사를 실행하거나 기존 스택을 바꾸는 것은 별도로 판단하세요.

## Skill 선택표

아래 이름은 `--skill`에 쓰는 폴더명입니다. `$` 호출명은 SKILL.md의 `name`을 확인합니다.
Vercel 두 항목의 호출명은 각각 `vercel-react-best-practices`, `vercel-composition-patterns`입니다.
개별 Skill의 용도·출처·주의점은 [선택 카탈로그](docs/CATALOG.md)를 봅니다.

| 선택 프로필 | 포함 Skill | 주로 쓰는 상황 |
|---|---|---|
| `core` | domain-discovery, systematic-debugging, verification-before-completion, evidence-check, session-handoff, explain-artifact | 요구 파악·결함 조사·검증·인계·설명 |
| `domain` | domain-discovery, data-quality | 낯선 업무 용어·정책·데이터의 의미 확정 |
| `data` | data-quality, jupyter-notebook, pdf, property-based-testing | 파일·표·측정 데이터·분석·보고 |
| `web` | frontend-design, react-best-practices, composition-patterns | UI와 React/Next.js가 실제 과제일 때 |
| `quality` | test-driven-development, verification-before-completion, property-based-testing, differential-review, receiving-code-review | 동작 검증과 변경 검토 |
| `parallel` | parallel-delivery, dispatching-parallel-agents, using-git-worktrees, subagent-driven-development, requesting-code-review | 독립 작업 위임·격리·검토 |
| `security` | security-best-practices, security-threat-model, sharp-edges, differential-review | 인증·권한·입력·위험한 기본값 |
| `planning` | brainstorming, writing-plans, executing-plans, doc-coauthoring | 요구가 덜 정해진 과제·설계·문서 |
| `python` | modern-python | Python 도구 구성을 새로 정할 필요가 있을 때 |
| `deep-audit` | audit-context-building, dimensional-analysis | 큰 코드의 정밀 분석·수치/단위 감사; 전체 파이프라인 비용 주의 |
| `git-finish` | finishing-a-development-branch | 일반 개발의 Git 마무리 참고; 시험 중 push를 허용하지 않음 |

도메인은 반도체·물류·재무·인사·품질·운영 등으로 가정하지 않습니다. 용어·단위·상태 전이·
집계 기준을 제공 자료와 실무자 답변으로 확정하고, 실제 정책을 수용 사례로 바꿉니다.
`DOMAIN_BRIEF.md`와 `DATA_CONTRACT.md`는 그 근거를 남기는 선택 양식입니다.

## MCP 선택표

실행 패키지는 고정 버전과 lockfile로 준비했습니다. 필요한 것만 내려받고 연결합니다.
이미 제공된 Codex 터미널로 충분하면 MCP를 설치하지 않아도 됩니다.

| 이름 | 용도 | 실행 요구 | 런타임의 외부 통신 |
|---|---|---|---|
| `filesystem` | 지정 프로젝트 파일 탐색·읽기·편집 | Node 24+ | 없음; 파일 쓰기 기능 포함 |
| `memory` | 작업별 로컬 지식 그래프·상태 보존 | Node 24+ | 없음; `.cofa/memory.jsonl` 저장 |
| `sequential-thinking` | 단계별 문제 정리 | Node 24+ | 없음; 간단한 작업에는 불필요 |
| `dbhub` | 로컬 SQLite 스키마·SQL 조회 | Node 22.5+ | 이 구성은 로컬 DB만; 읽기 전용 |
| `context7` | 공개 소프트웨어 라이브러리 문서 | Node 20.18.1+ | 있음; 질의가 외부로 전송됨 |
| `openai-docs` | 공식 OpenAI 공개 문서 조회 | HTTP MCP 지원 | 있음; 질의가 외부로 전송됨 |

```sh
python3 scripts/mcp_config.py --list
python3 scripts/mcp_config.py --project /실제/과제/루트 --servers memory --install --output /실제/과제/루트/mcp-selected.json
```

선택 서버만 `npm ci`로 설치하고 MCP JSON 조각을 만듭니다. 설치 중에는 공개 패키지 다운로드가 필요합니다.
생성한 서버 항목을 플랫폼 MCP 탭의 실제 형식에 맞게 기존 설정과 합칩니다.
Codex TOML 조각이 필요하면 `--format toml`을 사용합니다. 스크립트는 관리 설정을 자동 수정하지 않습니다.
자세한 서버별 명령과 제약은 [mcp/README.md](mcp/README.md)를 봅니다.

외부 문서 MCP에는 공개 라이브러리명·공개 문서 질문만 전달합니다. 문제·코드·데이터·키를 보내지 않습니다.
개인 API 키가 필요한 구성을 넣지 않았습니다. 외부 문서 MCP의 허용 여부와 제공 버전의 호환성은
사전 점검에서 확인합니다. Node가 낮으면 관리 도구를 업그레이드하지 않고 다른 선택이나 CLI로 진행합니다.

## 템플릿과 실행 도구

- `templates/`: AGENTS, WORKLOG, DOMAIN_BRIEF, DATA_CONTRACT, TASKS, CONTRACT,
  PARALLEL_PLAN, WORKER_BRIEF, DECISIONS, REVIEW, DELIVERY, AI_COLLABORATION,
  ENVIRONMENT, CHECKS.json, gitignore.example를 선택합니다. 실제 파일 목록은 `--list`가 기준입니다.
- `vendor/spec-kit/`: GitHub Spec Kit의 명세·계획·작업판·체크리스트·헌장 원본 5개입니다.
  긴 프로세스와 CLI 치환자를 포함하므로 필요한 구조만 참고하고 현재 과제에 맞게 채웁니다.
- `scripts/run_checks.py`: 선언한 검증 명령·종료 코드·출력·파일 상태를 기록합니다.
- `scripts/scan_secrets.py`: 일부 자격증명 패턴의 위치를 보고합니다. 누락 가능성이 있습니다.
- [START_EXAM.txt](START_EXAM.txt): 첫 요청문, [PROMPTS.txt](PROMPTS.txt): 짧은 후속 요청문.
- [PRECHECK_15MIN.txt](PRECHECK_15MIN.txt): 환경 확인, [docs/WORKFLOW.md](docs/WORKFLOW.md): 실행·검증 절차.

양식을 전부 만들 필요는 없습니다. `CHECKS.json`은 빈 설정이므로 실제 소스·검증 명령을 채워야 합니다.
필수 제출 파일명과 위치는 실제 과제 안내를 따릅니다. 별도 worktree의 결과는 최종 제출 루트로 통합합니다.

## 외부 자료와 시험 적용

- 원본 Skill의 `Claude`, `Task`, `superpowers:` 표기는 제공된 Codex 도구와 설치된 Skill로 대응합니다.
  해당 기능이 없으면 같은 역할을 직접 수행하고 다른 AI를 연결하지 않습니다.
- 선택형 Skill은 자체 절차·도구를 제안할 수 있습니다. 기존 스택·사용자 지시·시험 규칙을 우선합니다.
  배포·push·자동 UI 조작·관리 설정 변경을 외부 Skill만으로 승인받았다고 해석하지 않습니다.
- Browser 확인은 응시자가 플랫폼 안에서 직접 합니다. 브라우저 자동 조작 MCP는 포함하지 않았습니다.
- `deep-audit`는 기본 프로필이 아닙니다. 특히 dimensional-analysis는 전체 산술 파일과 여러 분석 역할을
  처리하고 주석을 추가할 수 있어, 필요한 파일·시간·권한을 먼저 판단합니다.
- 문서·분석용 Skill의 Python 패키지와 시스템 도구는 자동 설치하지 않습니다.
  설치된 도구와 과제 스택을 먼저 확인합니다. Context7은 전문 업무 지식의 검증을 대신하지 않습니다.
- `.gitignore`는 AI나 MCP의 읽기를 차단하지 않습니다. memory·로그·실제 과제 자료는 공개 저장소에 보내지 않습니다.

## 출처·라이선스·검증

외부 Skill 26개는 공개 저장소에서 실제 파일과 지원 자료를 가져왔습니다. 정확한 커밋·원본 경로·
수정 내역·SHA-256은 [vendor/manifest.json](vendor/manifest.json)에 있습니다.
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 출처와 라이선스를 구분했습니다.
원본 저작 파일은 루트 MIT LICENSE, 외부 자료는 각 MIT·Apache-2.0·CC-BY-SA-4.0 조건을 따릅니다.

로컬 검증 범위는 [VALIDATION.txt](VALIDATION.txt)를 봅니다. 제공 플랫폼에서 실제 사용 가능하다는 보장은
아니므로 사전 체험에서 선택한 구성만 확인합니다. 전역 설치나 기존 Codex 설정 변경은 하지 않았습니다.
