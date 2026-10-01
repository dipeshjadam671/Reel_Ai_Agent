# Content Generation & Publishing Workflow

```
[Start Cycle]
      │
      ▼
[Trend Scout] ──► Discovers viral angles & user search queries
      │
      ▼
[Researcher] ──► Aggregates sources, quotes & verified claims
      │
      ▼
[Novelty Guard] ──► Queries pgvector & GraphRAG for duplicate scripts
      │
      ├─► (If Novelty Score < 0.70) ──► Re-query alternate angle
      │
      ▼ (Novelty >= 0.70)
[Scriptwriter] ──► Creates hook, scenes, claims, on-screen text & CTA
      │
      ▼
[Localization] ──► Idiomatically adapts script (e.g. Hindi, Spanish)
      │
      ▼
[Fact Checker] ──► Verifies claims against compiled research
      │
      ▼
[Storyboard] ──► Defines scene layout, timing cues & camera framing
      │
      ├───────────────────────┬───────────────────────┐
      ▼                       ▼                       ▼
[Voice Agent]          [Presenter Agent]       [Asset Curator]
(TTS Waveform)         (Avatar Video)          (Licensed Media)
      │                       │                       │
      └───────────────────────┼───────────────────────┘
                              │
                              ▼
                       [Caption Agent] ──► Animated subtitle track
                              │
                              ▼
                     [Editor / FFmpeg] ──► Vertical 9:16 MP4 Render
                              │
                              ▼
                     [Compliance Gate] ──► Content & copyright check
                              │
                              ▼
                        [QA Critic] ──► Score pacing, audio & visuals
                              │
                              ▼
                   [HUMAN APPROVAL GATE] (LangGraph Interrupt)
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
        [REJECT]                            [APPROVE]
     (With feedback)                            │
            │                                   ▼
            ▼                              [PUBLISHER]
   [Regenerate Script]               (YouTube / Insta / TikTok)
                                                │
                                                ▼
                                           [ANALYTICS]
```
