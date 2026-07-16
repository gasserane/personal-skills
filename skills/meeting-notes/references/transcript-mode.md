# Recordings and transcripts mode

Turn a meeting recording (voice or video file) or an existing transcript into a structured note. This mode also anchors the catch-all rule: any capture method not covered elsewhere (chat log, email thread used as minutes, whiteboard photo) is normalised to text first, then continues from step 2.

## Flow

1. **Recording to transcript.** For a video or audio file, use the local video-content-analysis pipeline (`/analyze-video`): it transcribes and diarises locally and applies the consent and privacy validators by construction, so participants' voices never enter a cloud tool. If the meeting platform already produced a transcript (a Teams .vtt or .docx), prefer it: platform transcripts are free and usually name the speakers.

   **Consent check first.** A recording of other people carries more privacy weight than Ane's own dictation. Confirm the recording was made with participants' knowledge before processing; if consent is unclear, stop and ask.

2. **Transcript to structure.** Read the transcript in full. Segment into topics using the agenda if one exists (a prep sheet from prep mode, or the meeting invite), natural breaks otherwise. Extract candidate takeaways, decisions, and actions with owner and deadline as spoken. Quote-check every candidate decision against the transcript wording: "we should" is a proposal, "we agreed" is a decision.

3. **Interview.** Batch clarifying questions per the dictation-mode discipline (max 5 per topic, only what changes the note). Transcripts need fewer questions than dictation because the wording is verbatim, but three defect types survive verbatim capture: proposals that sound like decisions, actions without deadlines or owners, and unknown speakers or misheard names from auto-transcription. Verify names against context and memory; never guess.

4. **Draft, confirm, write** per the shared note structure and milestone-write rule: per-topic drafts for correction, then one write of the `.md` and branded `.docx`.

5. **Transcript handling after the note.** Ask Ane whether to keep or delete the transcript file, and where. Quote third parties in the note only as far as the note needs; anything shareable follows summary-anonymisation. Never write GBV, SOGIESC, or service-user identifiers from a transcript into a note.
