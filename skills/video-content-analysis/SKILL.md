---
name: video-content-analysis
description: Convert FGD/webinar/SBCC video files into a structured artefact pack (transcript, frames, manifest, Tier 1 BLUF summary) the existing MEL specialists can consume. Use when Ane asks to "analyse a video", "transcribe a focus group", "process a webinar recording", "summarise a meeting recording", or runs `/analyze-video <path>`. Tiered transcription (local Whisper for sensitive; M365 Stream for internal/public). Privacy + consent validated by construction. Per-run feedback prompt feeds the self-improvement loop.
version: 0.6.0-stage6
---

# video-content-analysis

`/analyze-video <path>` produces a manifest-led artefact pack from one video file. Downstream specialists (qualitative-coding-specialist, intersectionality-analyst, gender-transformative-assessor, sbcc-campaign-mel-specialist) consume the manifest directly.

## When to use

Trigger for any request that names a video, recording, FGD, webinar, training session, or SBCC clip and asks for transcript, summary, speaker analysis, or downstream coding. Trigger when Ane types `/analyze-video <path>` directly.

Do not trigger for live audio capture (file-based only in v1) or non-video media (audio-only files are out of v1 scope).

## Required inputs

Ask in one batch. The first three are required.

1. **Video path** (required). Local file. Supported containers: mp4, mkv, mov, webm.
2. **Privacy tier** (required). One of `sensitive`, `internal`, `public`. Default `sensitive`. Sensitive content (FGDs, interviews, anything with informed-consent constraints) stays on the local machine. Internal/public content can use Microsoft 365 Stream captions when available.
3. **Consent status** (required). One of `not_applicable`, `consent_internal_use_only`, `consent_research_anonymised`, `consent_research_attributed`, `consent_publication_anonymised`, `consent_publication_attributed`, `consent_unclear`. `consent_unclear` blocks downstream analysis.
4. **Language hint** (optional). Two-letter code for Whisper (e.g. `ro`, `en`, `fr`). Omit to auto-detect.
5. **Run diarization?** (optional, default no). `--diarize` runs pyannote.audio after transcription. Required for whose-voices-were-heard analysis. Adds ~50% to runtime.
6. **Brand-template Word summary?** (optional, default no). `--brand-summary` writes `summary.docx` in IPPF Visual Identity 2025 alongside the plain `summary.md`.
7. **Output directory** (optional). Default `<video-parent>/<video-stem>.video-analysis/`.
8. **Microsoft 365 caption file** (optional, internal/public only). Local `.vtt` path the user has already fetched via the Microsoft 365 MCP server. Skips Whisper.

## Method

### Step 1 — gather inputs

Ask Ane for required inputs 1–3 in one message. If `--diarize`, `--brand-summary`, or a caption path were passed in the invocation, do not re-ask. Honour the explicit values.

### Step 2 — capture consent metadata when missing

If consent metadata is incomplete (status set but no `documented_in` / `documented_date` / `responsible_person`), ask Ane in a second focused batch. Persist the captured values into the orchestrator call so they land in the manifest.

### Step 3 — invoke the orchestrator

Use Bash to run the venv Python with a one-line `analyze_video(...)` call. Force the ffmpeg PATH extension before the run. Pass the captured kwargs.

```powershell
$env:PATH = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin;$env:PATH"
& 'C:/Users/AGasser/OneDrive/GitHub/personal-skills/skills/video-content-analysis/venv/Scripts/python.exe' -c @'
from pathlib import Path
from ane_package.video.orchestrator import analyze_video
from ane_package.video.types import ConsentMetadata, ConsentStatus, PrivacyTier
result = analyze_video(
    Path(r"<VIDEO PATH>"),
    privacy_tier=PrivacyTier.<TIER>,
    consent=ConsentMetadata(
        status=ConsentStatus.<STATUS>,
        documented_in=r"<PATH OR NOTE>",
        documented_date="<ISO DATE OR EMPTY>",
        responsible_person="<NAME OR EMPTY>",
    ),
    language=<"ro" OR None>,
    diarize=<True OR False>,
    brand_summary=<True OR False>,
    output_dir=<PATH OR None>,
    m365_caption_path=<PATH OR None>,
)
print("MANIFEST:", result.manifest_path)
print("SUMMARY:", result.summary_path)
print("BRAND_SUMMARY:", result.brand_summary_path)
'@
```

### Step 4 — print the Tier 1 BLUF summary inline

Read `summary.md` from the orchestrator's return value and print it in the conversation. Add the manifest path on a final line so Ane can hand it to `/ann` or to a specialist.

### Step 5 — per-run feedback prompt

Run the feedback prompt before returning. Use the venv Python:

```powershell
& 'C:/Users/AGasser/OneDrive/GitHub/personal-skills/skills/video-content-analysis/venv/Scripts/python.exe' -c @'
from ane_package.video.feedback import prompt_verdict
v, n = prompt_verdict()
print(f"VERDICT={v.value}")
print(f"NOTE={n or ''}")
'@
```

If the verdict is `partial` or `failed`, append the verdict and note to `~/.claude/skills/video-content-analysis/telemetry.jsonl` so the next retrospective sees them. The orchestrator already wrote a telemetry line for the run; this second write is a verdict update keyed by source_hash. (Stage 6 collapses these into a single in-orchestrator call when the prompt timing is reworked.)

### Saving a regression fixture (verdict: partial / failed)

When a run finishes with `partial` or `failed`, the skill offers to save it as a regression fixture under `tests/video/fixtures/auto/<source_hash>/`.

Tier-gated:
- `privacy: public` AND `consent: not_applicable | consent_publication_*` → full save (source + transcript + frames + manifest)
- any other eligible verdict → metadata-only save (redacted manifest with consent + speaker labels + transcript text + source path stripped)
- `consent_unclear` → blocked entirely (regardless of verdict)

The auto-save directory is gitignored — auto-saved fixtures are local-only until you review and selectively commit.

### Step 6 — return

Return the manifest path, the summary path, and (if any) the brand-summary path to Ane. Suggest the next move:

- "Run `/ann analyse the focus group findings in <manifest>`" — for in-depth coding.
- "Run `/ann compute speaker time-share by gender across these 3 manifests`" — for batch cross-cuts.
- "Open `summary.docx` for the slide deck" — when `--brand-summary` was passed.

## Running the retrospective protocol

```powershell
/analyze-video --retrospective
```

Reads `~/.claude/skills/video-content-analysis/telemetry.jsonl`, computes performance against the seven anchors at `mel_wiki/wiki/calibration/video-content-analysis.md`, identifies recurring failures, and writes `~/.claude/skills/video-content-analysis/retrospectives/retrospective-YYYY-MM-DD.md`.

**Recommendations only.** The retrospective never edits the skill, the spec, or any code. Ane reviews and approves before any change ships.

The retrospective also fires automatically when `should_run_retrospective(state)` returns True at the end of any successful `/analyze-video` run — i.e., after 10 successful runs OR 4 weeks since the last retrospective, whichever is first.

## Output

- `manifest.json` — single source of truth for downstream specialists.
- `summary.md` — Tier 1 BLUF summary, plain markdown.
- `summary.docx` — IPPF Visual Identity 2025 brand template (when `--brand-summary`).
- `transcript.json` / `transcript.txt` / `transcript.vtt` — populated by the primitives.
- `frames/` — sequentially-numbered PNG frames.
- `network.log` — one-line audit trail.

## Calibration anchors

Operational quality benchmarks for this skill live at `mel_wiki/wiki/calibration/video-content-analysis.md` in the work folder.

Seven anchors:
- Schema validity (100% of manifests pass `manifest_v1.schema.json`)
- Transcription quality — Romanian (WER < 15% on the synthetic Romanian FGD fixture)
- Privacy enforcement (zero `network_egress != none` under `sensitive` tier)
- Consent enforcement (zero deliverables published from `consent_unclear` material)
- Data-gap detection (every `audio_quality_flags[]` flag maps to a `data_gaps[]` line; confidence-based extension gated on Stage 4.5)
- Performance (60-min FGD with diarization < 90 min wall-clock on this hardware)
- User satisfaction (≥ 80% of last 10 runs verdict ∈ {useful, partial})

The retrospective protocol consumes these anchors. See the section above.

**Evidence base:** Stage 5 implementation plan at `docs/superpowers/plans/2026-05-09-stage-5-skill-orchestrator.md`; design spec at `docs/superpowers/specs/2026-05-08-video-content-analysis-design.md` Sections 5–8 + 10; IPPF Visual Identity 2025 brand template at `ane_package.reporting.brand.IPPF_FORMAT_TEMPLATE`.
