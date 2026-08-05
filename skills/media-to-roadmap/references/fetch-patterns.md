# Fetch patterns per source type

Proven retrieval recipes, carried from the 2026-08-04 hand runs (Thariq article, Isenberg video). Fetch through context-mode so raw transcripts and page bytes stay out of the conversation; only extracted claims enter it. Every pattern here degrades explicitly — when a fetch fails, the roadmap names what was NOT read rather than papering over it.

## YouTube video

Two layers, in order:

1. **Description + metadata** — fetch the watch page and parse `ytInitialPlayerResponse` out of the page source (JSON blob in an inline `<script>`). Gives title, channel, date, description, chapter list. Cheap and reliable.
2. **Transcript** — from `ytInitialPlayerResponse.captions.playerCaptionsTracklistRenderer.captionTracks[]`, take the `baseUrl` of the wanted track and fetch it (`&fmt=json3` for JSON). **Known failure:** YouTube increasingly requires a POT token on caption URLs; the fetch returns empty or 403. Fallback: work from the description + chapters and say so in the roadmap's Source section — a scan of chapters is honest; a reconstructed transcript is not.

A long transcript never enters the conversation whole. Index it (`ctx_fetch_and_index` or fetch inside `ctx_execute`), then query for the concrete-technique passages.

## Podcast

Most podcasts ship show notes pages with a summary and often a transcript link — fetch those first. If only audio exists and no transcript is published, the scan runs on the show notes and the roadmap says so; this skill does not transcribe audio (that is video-content-analysis's pipeline, reserved for MEL research files).

## Blog article / documentation page

Straight `ctx_fetch_and_index`, then query. Watch for: multi-page series (fetch the parts actually cited), and paywalled pages returning a teaser — a teaser-only fetch is a failed fetch and gets flagged, not summarised as if complete.

## X.com / Twitter thread

Login-gated: direct fetch returns the shell page. Route through web search (the thread text is usually mirrored in search results, thread-reader mirrors, or coverage articles). Attribute to the mirror actually read, not to x.com, and flag that the primary was unreachable. A thread recalled from training data is a fabrication risk, never acceptable.

## GitHub repo / README

Fetch the raw file (`raw.githubusercontent.com`) rather than the HTML page. For a repo proposed for adoption, read the actual code of the load-bearing part before classifying above Assess — a README claim is marketing until the source confirms it.
