# Multi-Agent Specifications

## Hierarchical Multi-Agent Topology

The system uses a hierarchical multi-agent architecture where specialist agents operate within bounded subgraphs, orchestrated by the **Cycle Supervisor**. Specialist agents never directly call unrelated specialist agents; all context flows through the strongly typed `CycleState`.

---

## 1. Supervisor Agent (`supervisor.py`)
- **Role**: Master workflow orchestrator.
- **Responsibilities**:
  - Manages `CycleState` life cycle across subgraphs.
  - Verifies budget caps before dispatching compute-intensive or paid API jobs.
  - Controls retry budgets and backoff policies.
  - Triggers LangGraph `interrupt()` for human approval and resumes execution on user action.
  - Emits telemetry, audit logs, and cost accrual records.

---

## 2. Research Subgraph
- **Trend Scout (`trend_scout.py`)**:
  - Discovers high-performing angles, search volume, and community questions regarding the configured topic.
- **Researcher (`researcher.py`)**:
  - Executes targeted web queries, extracts article summaries, aggregates reputable sources, and compiles verified factual claims.
- **Novelty Guard (`novelty_guard.py`)**:
  - Compares prospective angles and claims against historical workspace scripts using pgvector embeddings and GraphRAG. Rejects redundant concepts.

---

## 3. Scripting Subgraph
- **Scriptwriter (`scriptwriter.py`)**:
  - Creates structured scripts featuring strong 3-second hooks, scene-by-scene visual cues, voiceover lines, and explicit calls to action.
- **Localization Agent (`localization.py`)**:
  - Idiomatically adapts the script to English, Hindi, Hinglish, Spanish, etc., preserving cultural context and comedic timing.
- **Fact Checker (`fact_checker.py`)**:
  - Validates factual assertions against research sources, annotating unverified claims.

---

## 4. Media Subgraph
- **Storyboard Agent (`storyboard.py`)**:
  - Converts script scenes into visual prompts, duration timings, transition directives, and caption placements.
- **Asset Curator (`asset_curator.py`)**:
  - Searches licensed b-roll video clips and images from Pexels, Unsplash, or mock assets. Preserves license URL, attribution text, and provider IDs.
- **Music Selector (`music_selector.py`)**:
  - Matches royalty-free background soundtracks to tone, mood, and target BPM.

---

## 5. Production Subgraph
- **Voice Agent (`voice.py`)**:
  - Dispatches script text to TTS engine (ElevenLabs, OpenAI, EdgeTTS, or Mock), extracting audio files and word-level timestamps.
- **Presenter Agent (`presenter.py`)**:
  - Dispatches presenter script segment to HeyGen/D-ID avatar engine to generate vertical portrait talking-head video footage.
- **Caption Agent (`caption.py`)**:
  - Generates synchronized word-by-word animated subtitle tracks (SRT/ASS).
- **Thumbnail Agent (`thumbnail.py`)**:
  - Extracts keyframe images and overlays title typography for click-worthy covers.
- **Editor / FFmpeg (`editor.py`)**:
  - Coordinates rendering job with the media renderer.

---

## 6. Compliance & QA Subgraph
- **Compliance Gate (`compliance.py`)**:
  - Validates copyright licensing, platform policies, AI disclosure mandates, and safety guidelines. Hard stop if policy breached.
- **QA Critic (`critic.py`)**:
  - Evaluates video pacing, audio-voice balance, subtitle alignment, visual interest, and overall quality score.

---

## 7. Publishing & Analytics Subgraph
- **Publisher (`publisher.py`)**:
  - Executes platform-specific publishing to YouTube Shorts, Instagram Reels, and TikTok via authenticated OAuth adapters.
- **Analytics Agent (`analytics.py`)**:
  - Polls platform metrics (views, retention, likes, shares, comments) to feed post-performance analytics.
