# Third-party notices

This repository is an aggregation. The root MIT license applies to original toolkit
instructions, scripts and templates, not a relicensing of the imported works below.
Exact commits, source paths, modifications and file hashes are in `vendor/manifest.json`.
Imported licenses are preserved in each skill and/or `vendor/licenses/`.

| Source | Imported material | License |
|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | 12 workflow skills and their supporting files | MIT |
| [anthropics/skills](https://github.com/anthropics/skills) | frontend-design, doc-coauthoring | Apache-2.0 |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | React best practices and composition patterns | MIT declared in upstream SKILL.md |
| [openai/skills](https://github.com/openai/skills) | pdf, jupyter-notebook, security-best-practices, security-threat-model | Apache-2.0 |
| [trailofbits/skills](https://github.com/trailofbits/skills) | differential-review, modern-python, property-based-testing, sharp-edges, audit-context-building, dimensional-analysis | CC-BY-SA-4.0 |
| [github/spec-kit](https://github.com/github/spec-kit) | 5 original templates under vendor/spec-kit | MIT |

Attribution for Trail of Bits material: Trail of Bits, `trailofbits/skills`, linked above.
Those files and their local path adaptations remain available under CC-BY-SA-4.0;
the original license text is included. This collection does not change their license.
Plugin-level agent prompts were bundled under the respective skill's `agents/` and
relative paths were repaired. The notebook skill's installation-path guidance was
adapted for project-scoped Codex use. Upstream debugging authoring/pressure-test
documents were omitted. Unsupported `effort` frontmatter was preserved under metadata;
compiled React guide links were repaired. Other substantive adaptations are listed in the manifest.

Vercel's imported SKILL.md files declare MIT. The upstream snapshot supplies no
separate license text; a copy of the MIT permission/warranty terms is included without
inventing a copyright holder notice. Original attribution and license fields remain.
Anthropic's frontend-design Apache license text is also retained with doc-coauthoring,
consistent with the repository's open-source example-skill licensing statement.
Anthropic's source-available docx/pdf/pptx/xlsx implementations were not imported.

The OpenAI skill repository marks itself deprecated. These selected, pinned files are
included for their self-contained workflows, not as a claim that their packaging is
the current plugin installation method. See official Codex documentation for discovery.

MCP server code is obtained as pinned npm dependencies when selected. Each server has
its own package manifest and lockfile; `node_modules` is not committed. Their licenses
remain with the installed packages. Reference-source license texts are also preserved:

- modelcontextprotocol/servers: upstream transition notice and applicable Apache-2.0/MIT
  terms; documentation CC-BY-4.0. See `vendor/licenses/modelcontextprotocol-servers.LICENSE`.
- upstash/context7: MIT. See `vendor/licenses/upstash-context7.LICENSE`.
- bytebase/dbhub: MIT. See `vendor/licenses/bytebase-dbhub.LICENSE`.
- OpenAI Docs MCP: remote documentation service configuration only; no service code redistributed.

The original lightweight templates under `templates/` are separate from the unmodified
Spec Kit templates in `vendor/spec-kit/`. A template does not automatically install the
Spec Kit CLI, authorize deployment, or replace the assessment's required deliverables.
