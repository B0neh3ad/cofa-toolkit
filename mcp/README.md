# 선택형 MCP 설정

`catalog.json`에 6개 선택지를 준비했습니다. 서버별 `servers/이름/package.json`과
lockfile로 버전을 고정합니다. 필요한 서버만 설치하며 전역 Codex 설정은 자동 수정하지 않습니다.

| 이름 | 용도·범위 | 고정 버전 | Node |
|---|---|---|---|
| filesystem | 지정한 프로젝트의 파일 도구; 쓰기 기능 포함, CLI와 중복될 수 있음 | 2.1.0 | 24+ |
| memory | 로컬 지식 그래프; 프로젝트 `.cofa/memory.jsonl` | 2.0.1 | 24+ |
| sequential-thinking | 단계별 문제 정리; 짧은 일에는 호출 비용이 더 클 수 있음 | 2.0.0 | 24+ |
| context7 | 공개 라이브러리 문서; 질의가 외부 서비스로 감 | 4.4.4 | 20.18.1+ |
| dbhub | 기존 로컬 SQLite 조회; execute_sql 읽기 전용과 최대 1,000행 설정 | 1.5.0 | 22.5+ |
| openai-docs | 공식 OpenAI 공개 문서; 외부 HTTP 연결, 별도 런타임 없음 | 제공 서비스 | 불필요 |

처음 세 서버는 현재 고정 버전에서 Node 24가 필요합니다. 제공 런타임이 낮으면
시험 도구를 업데이트하지 않고 WORKLOG·터미널·기존 데이터 도구로 진행합니다.
로컬 서버의 '외부 통신 없음'은 설치 후 이 구성의 업무 처리 기준입니다.
패키지 설치는 공개 npm에서 다운로드하며 클라이언트/모델 자체의 통신은 별개입니다.

## 1. 선택하고 설치·설정 조각 만들기

툴킷 루트에서 실행합니다. 경로를 실제 과제 루트로 바꿉니다.

```sh
python3 scripts/mcp_config.py --project /실제/과제/루트 --servers memory filesystem --install --output /실제/과제/루트/mcp-selected.json
```

- 선택한 패키지만 `npm ci --ignore-scripts`로 설치합니다. lockfile의 전이 의존성도 고정됩니다.
- `.cofa/`에는 로컬 상태·설정·npm 캐시가 생길 수 있습니다. 실제 과제 Git 제외와 제출 요구를 확인합니다.
- JSON은 흔히 쓰는 `mcpServers` 구조입니다. 플랫폼 MCP 탭에서 요구하는 실제 JSON 형식을
  먼저 확인하고 생성한 서버 항목을 기존 설정에 합칩니다. 기존 항목 전체를 지우지 않습니다.
- 파일명 접두사는 `cofa_`입니다. 같은 이름의 기존 서버와 충돌하는지 확인합니다.
- Codex TOML 조각은 `--format toml`로 생성합니다. 관리 설정 경로에 자동 기록하지 않습니다.
- 같은 출력 파일이 다르면 덮어쓰지 않고 멈춥니다. 명시적으로 검토·합쳐 사용합니다.

연결 뒤 제공 Codex의 `/mcp` 또는 실제 도움말에 나온 상태 확인 기능으로 도구를 확인합니다.
서버 시작 성공·도구 목록 조회·실제 도구 호출 성공은 각각 구분합니다.
사용하지 않을 서버는 켜지 않습니다. MCP 설정이 실패해도 본 구현을 계속할 대안을 둡니다.

## 2. 로컬 DB

```sh
python3 scripts/mcp_config.py --project /실제/과제/루트 --servers dbhub --database /실제/과제/루트/data.db --install --output /실제/과제/루트/mcp-db.json
```

이미 존재하는 로컬 SQLite 파일만 받습니다. `.cofa/dbhub.toml`에 sources와
`execute_sql.readonly = true`, `max_rows = 1000`을 생성합니다. 이것은 tool 설정이며
source에 readonly를 적는 것과 다릅니다. 먼저 작은 조회로 스키마·행 수를 확인합니다.
행 제한으로 잘린 결과를 전체 분석으로 보고하지 않습니다. 원본 DB 보존과 전체 검증은 별개입니다.
원격 DB·관리자 자격증명·임의 DSN을 넣는 구성은 이 스크립트에 포함하지 않았습니다.

## 3. 외부 공개 문서

```sh
python3 scripts/mcp_config.py --project /실제/과제/루트 --servers context7 --install --output /실제/과제/루트/mcp-docs.json
python3 scripts/mcp_config.py --project /실제/과제/루트 --servers openai-docs --format toml
```

개인 API 키 없이 공개 문서를 사용하는 설정입니다. 서비스 제한·인증 요구가 생기면
개인 키를 추가하지 않고 대체합니다. 시험의 외부 문서 조회 허용 범위도 먼저 확인합니다.
공개 라이브러리명·버전·공개 API 질문만 질의하고, 문제·코드·데이터·로그·개인정보는 전송하지 않습니다.
Context7은 업무 도메인의 정답이나 신뢰성을 보증하지 않습니다. 전문 규칙은 제공 자료와 1차 근거를 확인합니다.

## 자료와 제약

- [MCP reference servers](https://github.com/modelcontextprotocol/servers)
- [Context7](https://github.com/upstash/context7)
- [DBHub](https://github.com/bytebase/dbhub), [읽기 전용 설정](https://dbhub.ai/config/toml)
- [공식 OpenAI Docs MCP](https://developers.openai.com/learn/docs-mcp)
- [Codex MCP 설정](https://learn.chatgpt.com/docs/extend/mcp)

filesystem의 폴더 범위는 비밀값 마스킹을 뜻하지 않습니다. `.gitignore`도 읽기 차단이 아닙니다.
memory에는 확정된 업무 결정과 근거만 필요한 만큼 저장하고 파일·구현과 대조합니다.
sequential-thinking에는 간결한 작업 요약을 사용하며 호출 수 자체를 성과로 기록하지 않습니다.
브라우저 자동 조작·외부 AI·GitHub 쓰기·메시지 전송용 MCP는 시험용 구성에 포함하지 않았습니다.
