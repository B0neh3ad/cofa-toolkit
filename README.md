# Cofa 시험용 선택형 툴킷 v4

낯선 도메인의 요구 파악부터 구현·데이터 검증·설명까지 필요한 자료를 골라 씁니다.
**Skill 32개, MCP 6개, 프로젝트 템플릿 15개와 Spec Kit 원본 템플릿 5개**를 담았습니다.
연습 과제·데모 웹페이지·CSV 예제·워크트리 실습은 제거했습니다.
`tests/`는 툴킷 자체의 회귀 검증이며 연습 문제가 아닙니다.

바로 이동: [Skill 등록·호출](#원하는-skill-등록과-사용) · [MCP 등록·호출](#원하는-mcp-등록과-사용) ·
[템플릿 복사·작성](#원하는-템플릿-사용) · [개별 선택 카탈로그](docs/CATALOG.md)

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

## 원하는 구성을 등록하기 전

아래 `sh` 블록은 **터미널 명령**, `text` 블록은 **Codex 채팅에 넣을 프롬프트**입니다.
플랫폼 안에서 가져온 `cofa-toolkit` 폴더로 이동한 터미널에서 경로를 한 번 지정합니다.

```sh
COFA_TOOLKIT="$PWD"
COFA_PROJECT="/실제/과제/루트"
python3 "$COFA_TOOLKIT/scripts/setup.py" --list
```

`COFA_PROJECT`를 README가 있는 실제 과제 경로로 바꿉니다. 경로에 공백이 있어도 따옴표를 유지합니다.
이 변수는 같은 터미널에서만 유지됩니다. 새 터미널에서는 다시 지정하세요.
**채팅 프롬프트의 `[툴킷 경로]`, `[과제 경로]`에는 실제 경로를 적습니다. 셸 변수는 채팅에서 자동 치환되지 않습니다.**

## 원하는 Skill 등록과 사용

### 명령으로 등록

원하는 **폴더명**을 `--skill` 뒤에 넣습니다. 여러 개면 옵션을 반복합니다.
먼저 `--dry-run`으로 복사 계획만 보고, 끝의 `--dry-run`을 빼면 실제로 등록합니다.

```sh
python3 "$COFA_TOOLKIT/scripts/setup.py" --target "$COFA_PROJECT" \
  --skill domain-discovery --skill data-quality --dry-run

python3 "$COFA_TOOLKIT/scripts/setup.py" --target "$COFA_PROJECT" \
  --skill domain-discovery --skill data-quality
```

등록 위치는 `[과제 경로]/.agents/skills/선택한폴더/`입니다. 사용자 전역 Skill은 바꾸지 않습니다.
묶음 선택은 `--profile core --profile data`처럼 프로필을 반복합니다. 개별 `--skill`과 함께 써도 됩니다.

| 출력 | 의미와 다음 행동 |
|---|---|
| `copy` | 실제 실행이면 복사 완료, dry-run이면 복사 예정 |
| `unchanged` | 이미 같은 내용이 있어 재복사하지 않음 |
| `skipped-existing` | 기존 내용이 달라 보존함. 원본과 비교해 필요한 변경만 합침 |

### Codex에게 등록을 맡기는 프롬프트

```text
툴킷은 [툴킷 경로], 실제 과제는 [과제 경로]에 있어.
툴킷의 scripts/setup.py로 domain-discovery와 data-quality만 이 과제에 등록해줘.
기존 Skill과 지침은 보존하고, 등록된 경로와 실제 호출명을 알려줘.
아직 업무 파일 구현이나 MCP 설치는 시작하지 마.
```

### 등록 후 호출

**실제 과제 폴더에서 시작한 Codex**에서 `/skills` 또는 `$` 선택 목록으로 확인합니다.
목록에 보이면 다음처럼 명시적으로 사용합니다.

```text
$domain-discovery 를 사용해 README와 제공 자료의 용어·단위·업무 규칙을 정리해줘.
이미 확정된 요구는 활용하고, 구현 결과를 바꿀 미확인 정책만 짚어줘.
```

```text
$data-quality 를 사용해 제공 데이터의 스키마·누락·중복·조인 키·집계 기준을 확인해줘.
원본은 보존하고 표본 점검과 전체 검증을 구분해서 보고해줘.
```

등록 명령의 폴더명과 `$` 호출명은 다를 수 있습니다. 예를 들어
`--skill react-best-practices`의 호출은 `$vercel-react-best-practices`입니다.
`/skills`가 없거나 새 Skill이 보이지 않으면 제공 버전의 `/help`를 확인하고 새 세션에서 다시 봅니다.
자동 발견을 지원하지 않으면 다음처럼 **파일을 직접 읽게 하는 방식**으로 적용합니다.

```text
[과제 경로]/.agents/skills/data-quality/SKILL.md를 읽고 이번 데이터 검증에 적용해줘.
이 방식으로 읽은 것과 Skill 자동 등록·발견 여부는 구분해서 알려줘.
```

[공식 Skill 발견·호출 설명](https://learn.chatgpt.com/docs/build-skills)

## 원하는 MCP 등록과 사용

**패키지 설치 → 설정 조각 생성 → 플랫폼에 등록 → 연결·호출 확인**의 순서입니다.
`mcp_config.py` 실행만으로 플랫폼 MCP 등록까지 완료되는 것은 아닙니다.

### 선택한 서버 설치와 설정 생성

```sh
python3 "$COFA_TOOLKIT/scripts/mcp_config.py" --list
node --version

python3 "$COFA_TOOLKIT/scripts/mcp_config.py" --project "$COFA_PROJECT" \
  --servers memory --install --output "$COFA_PROJECT/.cofa/mcp-memory.json"
```

`--servers`에는 아래 MCP 선택표의 이름을 넣습니다. 여러 개는 `--servers memory filesystem`처럼
공백으로 나열합니다. `--install`은 선택 서버만 설치하며 Node 요구사항이 맞지 않으면 멈춥니다.
이미 설치되어 있으면 `--install`을 생략할 수 있습니다. 기존 출력 파일의 내용이 다르면 덮어쓰지 않으므로
다른 출력 파일명을 쓰거나 기존 조각과 명시적으로 합칩니다.

용도별 설정 예시는 다음과 같습니다. **필요한 한 가지 명령만 골라 실행**합니다.

```sh
# 공개 라이브러리 문서 조회
python3 "$COFA_TOOLKIT/scripts/mcp_config.py" --project "$COFA_PROJECT" \
  --servers context7 --install --output "$COFA_PROJECT/.cofa/mcp-context7.json"

# 기존 로컬 SQLite 조회: DB 경로를 실제 파일로 바꾸기
python3 "$COFA_TOOLKIT/scripts/mcp_config.py" --project "$COFA_PROJECT" \
  --servers dbhub --database "$COFA_PROJECT/data.db" --install \
  --output "$COFA_PROJECT/.cofa/mcp-db.json"

# 공개 OpenAI 문서: npm 설치와 Node가 필요 없는 HTTP 설정
python3 "$COFA_TOOLKIT/scripts/mcp_config.py" --project "$COFA_PROJECT" \
  --servers openai-docs --output "$COFA_PROJECT/.cofa/mcp-openai-docs.json"
```

### Cofa MCP 탭에 등록

1. 생성된 JSON을 플랫폼 에디터에서 열거나 터미널에서 확인합니다.
   예: `cat "$COFA_PROJECT/.cofa/mcp-memory.json"`.
2. 플랫폼의 **MCP 탭**에서 기존 설정을 확인합니다. 생성한 JSON의 `mcpServers` 안에 있는
   선택 서버 항목을 기존 설정에 합칩니다. 탭이 요구하는 JSON 구조가 다르면 해당 구조에 맞춥니다.
3. 저장한 뒤 제공 Codex에서 `/mcp`로 활성 서버와 도구를 확인합니다.
   터미널의 `codex mcp list`는 설정 확인용이며, 실제 호출 성공까지 증명하지는 않습니다.
4. 반영되지 않으면 새 Codex 세션에서 확인하고 플랫폼의 재연결 안내를 따릅니다.
   전체 감독·응시 환경을 임의로 재시작하지 않습니다. 형식이 불명확하면 Cofa Helper에서 확인합니다.

TOML을 사용하는 **설정 변경이 허용된 환경**에서는 다음처럼 조각을 생성해 기존 MCP 항목과 합칩니다.
플랫폼이 MCP 탭에서 설정을 관리한다면 그 경로를 우선합니다.

```sh
python3 "$COFA_TOOLKIT/scripts/mcp_config.py" --project "$COFA_PROJECT" \
  --servers memory --format toml --output "$COFA_PROJECT/.cofa/mcp-memory.toml"
```

### Codex에게 준비를 맡기는 프롬프트

```text
툴킷은 [툴킷 경로], 실제 과제는 [과제 경로]야.
툴킷의 scripts/mcp_config.py로 memory MCP만 준비해줘.
Node 요구사항을 확인하고 선택 패키지만 설치해 .cofa/mcp-memory.json을 생성해줘.
관리 설정이나 기존 MCP 설정은 자동으로 덮어쓰지 마.
내가 MCP 탭에 합칠 서버 항목과 등록 후 확인할 절차를 알려줘.
설정 생성·연결 성공·실제 호출 성공을 구분해서 보고해줘.
```

### 등록 후 실제 호출

```text
연결된 cofa_memory 도구로 '구현 전에 실제 README를 확인한다'는 점검 메모를
저장하고 다시 검색해줘. 실제 호출 결과로 연결을 확인하고 추측으로 성공 처리하지 마.
```

```text
연결된 cofa_context7 도구로 pandas read_csv의 dtype 옵션에 대한 공개 문서를 찾아줘.
공개 라이브러리 질문만 전달하고 과제 원문·코드·데이터·로그는 전송하지 마.
```

서버별 생성 이름은 `cofa_filesystem`, `cofa_memory`, `cofa_sequential_thinking`,
`cofa_dbhub`, `cofa_context7`, `cofa_openai_docs`입니다. 해당 서버를 선택·등록했을 때만 호출합니다.
MCP가 지원되지 않거나 연결이 실패하면 WORKLOG·터미널·기존 라이브러리로 진행합니다.
[공식 Codex MCP 설정·상태 확인 설명](https://learn.chatgpt.com/docs/extend/mcp)

## 원하는 템플릿 사용

### 선택한 파일만 복사

```sh
python3 "$COFA_TOOLKIT/scripts/setup.py" --target "$COFA_PROJECT" \
  --template AGENTS.md --template WORKLOG.md --template DOMAIN_BRIEF.md \
  --template DATA_CONTRACT.md
```

선택 파일이 **과제 루트**에 생깁니다. 기존 파일은 `skipped-existing`으로 보존합니다.
추가 파일이 필요하면 `--template TASKS.md --template REVIEW.md`처럼 고릅니다.
`--template`은 `templates/`의 15개 파일에 적용됩니다. `vendor/spec-kit/`의 원본 5개는 아래 참고 프롬프트로 사용합니다.

### 복사한 템플릿을 실제 내용으로 채우는 프롬프트

```text
[과제 경로]의 README·기존 지침·제공 데이터를 먼저 확인해줘.
툴킷은 [툴킷 경로]에 있어. 필요한 AGENTS.md, WORKLOG.md, DOMAIN_BRIEF.md,
DATA_CONTRACT.md 템플릿을 선택해서 적용하고 실제 과제의 사실과 근거로 채워줘.
기존 파일이 있으면 원래 요구를 보존하며 필요한 내용만 합쳐줘.
빈칸·가정·미확인은 구분하고 실제 실행하지 않은 결과를 검증 완료로 적지 마.
필수 제출 파일명이 따로 있으면 그 이름과 형식을 우선해줘.
```

AGENTS.md를 만들거나 합친 뒤 현재 세션에서 적용하려면 다음처럼 명시합니다.

```text
[과제 경로]/AGENTS.md를 다시 읽고 이후 작업에 적용해줘.
현재 목표·진행·결정·검증·다음 행동은 WORKLOG.md에 필요한 만큼 갱신해줘.
```

AGENTS 외의 템플릿은 파일명만으로 자동 실행되지 않습니다. 복사만 한 빈 양식을 완성된 산출물로 취급하지 않습니다.
`gitignore.example`도 `.gitignore`에 자동 병합되지 않으므로 기존 규칙과 필요한 패턴을 합칩니다.
`CHECKS.json`은 실제 코드 경로와 검증 명령을 채우기 전에는 사용할 검증이 없습니다.

Spec Kit의 긴 원본 양식이 필요할 때는 다음처럼 구조를 참고하게 합니다.

```text
[툴킷 경로]/vendor/spec-kit/spec-template.md와 tasks-template.md를 참고해줘.
현재 과제에 필요한 요구·수용 기준·의존성·병렬 작업 구조만 가져와
기존 WORKLOG.md 또는 과제에서 요구한 문서에 반영해줘.
예시 작업·치환자는 실제 내용으로 바꾸고 Spec Kit CLI 설치나 추가 프로세스는 시작하지 마.
```

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
