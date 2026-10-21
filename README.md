# AI Control Crosswalk

**One set of AI controls, mapped to the risk taxonomies, security lists, principles, standards and regulation that organisations have to answer to - with sector views and an interactive dashboard.**

Most organisations adopting AI face the same problem: the MIT AI Risk Repository describes *what can go wrong*, OWASP describes *how GenAI and agents get attacked*, the OECD sets *principles*, ISO/IEC 42001 defines a *management system*, and the EU AI Act sets *legal obligations* - but nothing ties them together. This project defines **28 unified, auditable AI controls** and maps each one across all six frameworks, so a single control can evidence many requirements at once.

> **Live dashboard:** `https://bhatearohi.github.io/ai-control-crosswalk/` (after enabling GitHub Pages - see below)

---

## What's mapped

| Framework | Version used | Items | Role in the crosswalk |
|---|---|---|---|
| [MIT AI Risk Repository](https://airisk.mit.edu/) - Domain Taxonomy | 7 domains, 24 subdomains | 24 | *What* can go wrong |
| [MIT AI Risk Mitigation Taxonomy](https://airisk.mit.edu/blog/mapping-ai-risk-mitigations) | 4 top-level categories | 4 | How each control is classified |
| [OWASP Top 10 for LLM Applications](https://genai.owasp.org/) | 2026 | 10 | GenAI security threats |
| [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/) | 2026 | 10 | Autonomous-agent threats |
| [OECD AI Principles](https://oecd.ai/en/ai-principles) | 2019, updated 2024 | 5 | Values and principles |
| [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html) Annex A | 2023 | 38 | Certifiable management-system controls |
| [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) - Reg. (EU) 2024/1689 | selected articles | 19 | Legal obligations |

**Sectors:** Manufacturing, Financial Services, Healthcare & Life Sciences. Every control carries a priority (high / medium / low) per sector, plus sector-specific notes and regulatory context (e.g. DORA, PRA SS1/23, MDR/IVDR, Machinery Regulation, Cyber Resilience Act).

### Headline results (v1.0)

- **28 controls → 244 mappings**
- **100% coverage** of OWASP LLM 2026, OWASP Agentic 2026, OECD, ISO/IEC 42001 Annex A (38/38) and the selected EU AI Act articles
- **20 / 24 MIT risk subdomains** treated. The four left open - power centralisation, devaluation of human effort, competitive dynamics, AI welfare - are systemic risks that one organisation's control set can't meaningfully treat. They are deliberately kept visible as gaps rather than forced into a mapping.

---

## Dashboard

A single self-contained HTML page (no server, no dependencies) with five views:

| View | What it answers |
|---|---|
| **Overview** | Coverage per framework, controls by mitigation category, sector priority, sector context |
| **Crosswalk matrix** | Every control × every framework, as item IDs or counts. Click a control for guidance, audit evidence and all mappings. Export the filtered view to CSV |
| **Risk heatmap** | For each MIT risk subdomain, how many controls and framework items address it. Untreated risks are flagged red |
| **Pivot explorer** | "Which ISO 42001 controls help evidence EU AI Act Art. 14?" - pick any item, any target framework, and see the path through the unified controls |
| **Gaps** | Framework items with no control under the current filters |

Global filters (sector + minimum priority, mitigation category, free-text search) apply to every view. Light and dark themes, mobile friendly.

---

## Quick start

### Windows (PowerShell)

```powershell
git clone https://github.com/bhatearohi/ai-control-crosswalk.git
cd ai-control-crosswalk
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m crosswalk build
start docs\index.html
```

### macOS / Linux

```bash
git clone https://github.com/bhatearohi/ai-control-crosswalk.git
cd ai-control-crosswalk
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m crosswalk build
open docs/index.html        # or xdg-open on Linux
```

## Command line

```bash
python -m crosswalk validate                     # referential-integrity checks
python -m crosswalk build                        # dashboard + CSV / Excel / Markdown exports
python -m crosswalk stats --sector finance       # coverage using only high-priority finance controls
python -m crosswalk gaps                         # items no control addresses
python -m crosswalk query LLM01 --to ISO42001    # pivot: prompt injection -> ISO 42001
python -m crosswalk query Art.14 --to OWASP-ASI  # pivot: human oversight -> agentic threats
```

Example:

```
$ python -m crosswalk query LLM01 --to ISO42001
LLM01 - Prompt Injection  (OWASP LLM)
Linked via controls: AICC-11, AICC-12

Related ISO 42001 items:
  A.6.1.3    Processes for responsible AI system design and development   [via AICC-12]
  A.6.2.2    AI system requirements and specification   [via AICC-12]
  A.6.2.4    AI system verification and validation   [via AICC-11]
```

## Outputs

| File | For |
|---|---|
| `docs/index.html` | Interactive dashboard (data embedded - works offline or on GitHub Pages) |
| `docs/data.json` | Full dataset for other tools |
| `exports/ai_control_crosswalk.xlsx` | Matrix, control detail, long mapping, coverage and sources sheets - ready for a GRC tool import |
| `exports/crosswalk_long.csv` | One row per control-to-requirement mapping |
| `exports/CROSSWALK.md` | Readable matrix for GitHub |

## Publish the dashboard on GitHub Pages

1. Push the repo to GitHub.
2. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
3. Push to `main`. The workflow validates the data, runs the tests, rebuilds the dashboard and deploys it.

---

## Project structure

```
ai-control-crosswalk/
├── data/
│   ├── controls.yaml              # the 28 unified controls and their mappings  <- edit here
│   ├── sectors.yaml               # sector profiles and regulatory context
│   └── frameworks/                # one YAML per framework (items, source, licence notes)
├── crosswalk/                     # Python package: loader, validator, analysis, build, CLI
├── dashboard/template.html        # dashboard source (data injected at build time)
├── docs/                          # built dashboard (GitHub Pages root)
├── exports/                       # built CSV / Excel / Markdown
├── tests/                         # pytest suite
└── .github/workflows/ci.yml       # validate -> test -> build -> deploy
```

## Control model

Each control in `data/controls.yaml` carries:

```yaml
- id: AICC-15
  title: Human oversight and intervention
  category: MITM-GOV                    # MIT mitigation category
  objective: ...
  guidance: [...]                       # how to implement
  evidence: [...]                       # what an auditor would ask for
  maps:
    MIT: [MIT-5.1, MIT-5.2, MIT-7.1]
    OWASP-ASI: [ASI09, ASI10]
    OECD: [OECD-1.2, OECD-1.4, OECD-1.5]
    ISO42001: [A.9.2, A.9.3]
    EUAIA: [Art.14, Art.26]
  sectors: {manufacturing: high, finance: high, healthcare: high}
  sector_notes:
    healthcare: Clinician remains the decision-maker; guard against automation bias.
```

## Methodology

- **Control-centric, not item-to-item.** Frameworks are linked *through* implementable controls, the way a GRC function actually evidences compliance. This avoids the false precision of direct "Art. X = Clause Y" equivalences.
- **Mapping test:** a control maps to an item only if implementing it would produce evidence an auditor could cite for that item.
- **Gaps are a feature.** Coverage is computed, not asserted, and anything unmapped is surfaced.
- **Validated data.** Every id is checked against the framework files on every build, so a typo can't silently create a false mapping.

## Limitations and disclaimer

- Mappings are **analyst judgement** ("supports / contributes to"), not official equivalences published by MIT, OWASP, OECD, ISO or the EU.
- EU AI Act **application dates are not hard-coded** because they have been the subject of amendment proposals. Check the Official Journal for the current position.
- ISO/IEC 42001 control text is copyrighted and is **not reproduced**. Only identifiers and short titles are used.
- Sector notes are orientation, **not legal advice**.

## Roadmap

- [ ] Add NIST AI RMF 1.0 and ISO/IEC 23894 as frameworks
- [ ] Map to the MIT mitigation **subcategories** (23) once the taxonomy is finalised
- [ ] Link to MIT AI Incident Tracker data to show real incidents per control
- [ ] Control maturity self-assessment with a scored gap report
- [ ] OSCAL export for GRC tool import

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Proposals to add or challenge a mapping are very welcome - please include the reasoning.

## Author

**Arohi Bhate** - Cyber Risk & Compliance | ISO/IEC 27001:2022 Lead Auditor
[LinkedIn](https://uk.linkedin.com/in/arohi-bhate) · [Portfolio](https://arohibhate.com) · [GitHub](https://github.com/bhatearohi)

## Licence

Code and original mappings: MIT (see [LICENSE](LICENSE)). Framework names and identifiers belong to their owners; see the notes in each `data/frameworks/*.yaml` file.
