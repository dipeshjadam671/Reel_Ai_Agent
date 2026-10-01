import json
import re
import time
from typing import Optional, Dict, Any, List
from backend.app.integrations.llm.base import LLMProvider, LLMResponse

class MockLLMProvider(LLMProvider):
    def __init__(self, model_name: str = "mock-gpt-4o"):
        self.model_name = model_name

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        start_time = time.time()
        prompt_lower = prompt.lower()
        sys_lower = (system_prompt or "").lower()

        # Extract topic with priority on explicit topic markers
        topic = None
        t_match = re.search(r'Topic:\s*["\']?([^"\'\n\r]+)["\']?', prompt, re.IGNORECASE)
        if t_match and t_match.group(1).strip().lower() != "string":
            topic = t_match.group(1).strip()
        if not topic:
            t_match = re.search(r'web search results for\s*["\']([^"\']+)["\']', prompt, re.IGNORECASE)
            if t_match and t_match.group(1).strip().lower() != "string":
                topic = t_match.group(1).strip()
        if not topic:
            t_match = re.search(r'"topic":\s*["\']([^"\']+)["\']', prompt, re.IGNORECASE)
            if t_match and t_match.group(1).strip().lower() != "string":
                topic = t_match.group(1).strip()
        if not topic:
            t_match = re.search(r'"title":\s*["\']([^"\']+)["\']', prompt, re.IGNORECASE)
            if t_match and t_match.group(1).strip().lower() != "string":
                topic = t_match.group(1).strip()
        if not topic:
            topic = "Technology Innovation"
        else:
            for prefix in ["The Unspoken Truth About ", "The Shocking Truth About ", "The Secret Truth About ", "The Hidden "]:
                if topic.startswith(prefix):
                    topic = topic[len(prefix):]
            topic = topic.replace("⚡", "").replace("📱", "").replace("🚀", "").replace("\\u26a1", "").replace("\u26a1", "").strip()

        seed_match = re.search(r'MANDATORY USER INSTRUCTIONS / SEED SCRIPT:\s*"""(.*?)"""', prompt, re.DOTALL)
        if not seed_match:
            seed_match = re.search(r'User Provided Seed Notes:\s*"(.*?)"', prompt, re.DOTALL)
        if not seed_match:
            seed_match = re.search(r'User Context / Directives:\s*(.*?)(?=\n\n|$)', prompt, re.DOTALL)
        seed_script = seed_match.group(1).strip() if seed_match else ""

        lang_match = re.search(r'target language\s*["\']?([a-zA-Z_-]+)["\']?', prompt, re.IGNORECASE)
        if not lang_match:
            lang_match = re.search(r'Target Language:\s*["\']?([a-zA-Z_-]+)["\']?', prompt, re.IGNORECASE)
        if not lang_match:
            lang_match = re.search(r'adapt.*?to\s*["\']?([a-zA-Z_-]+)["\']?', prompt, re.IGNORECASE)
        lang = lang_match.group(1).lower().strip() if lang_match else "en"

        cta_match = re.search(r'"call_to_action":\s*["\']([^"\']+)["\']', prompt)
        call_to_action = cta_match.group(1).strip() if cta_match else "Which side are you on? Comment your vote below and follow!"

        claims_from_prompt = re.findall(r'- FACT:\s*([^\n]+)', prompt)

        # 1. Compliance Gate Check
        if "compliance" in sys_lower or "compliance" in prompt_lower:
            data = {
                "passed": True,
                "score": 0.99,
                "policy_checks": {
                    "content_safety": "PASSED",
                    "hate_speech": "PASSED",
                    "asset_licensing": "PASSED",
                    "ai_disclosure": "INCLUDED",
                    "platform_guidelines": "COMPLIANT"
                },
                "issues": [],
                "warnings": []
            }
            content = json.dumps(data) if json_mode else "Compliance passed with score 0.99"

        # 2. QA Critic
        elif "quality control" in sys_lower or "qa_critic" in sys_lower or "critic" in sys_lower or "qa" in sys_lower:
            data = {
                "passed": True,
                "score": 0.94,
                "breakdown": {
                    "script_quality": 0.95,
                    "audio_clarity": 0.92,
                    "visual_coherence": 0.96,
                    "pacing": 0.93
                },
                "issues": [],
                "warnings": ["Audio track volume adjusted to standard -14 LUFS"]
            }
            content = json.dumps(data) if json_mode else "QA check passed with score 0.94"

        # 3. Fact Checker
        elif "fact-checker" in sys_lower or "fact_checker" in sys_lower or "fact-check" in prompt_lower:
            data = {
                "fact_check_passed": True,
                "confidence_score": 0.98,
                "verified_claims": [
                    {"claim": f"Core assertions for {topic} verified against research sources.", "status": "VERIFIED", "evidence": "Verified with technical benchmarks and documentation."}
                ],
                "flagged_claims": []
            }
            content = json.dumps(data) if json_mode else "All factual claims verified."

        # 4. Researcher (placed before trend scout to prevent search snippet matching "trends")
        elif "researcher" in sys_lower or "extract key research sources" in prompt_lower or "web search results for" in prompt_lower:
            results_found = []
            title_matches = re.findall(r'-\s*Title:\s*([^\n]+)', prompt)
            url_matches = re.findall(r'URL:\s*([^\n]+)', prompt)
            domain_matches = re.findall(r'Domain:\s*([^\n]+)', prompt)
            snippet_matches = re.findall(r'Snippet:\s*([^\n]+)', prompt)

            for i in range(len(title_matches)):
                t = title_matches[i].strip()
                u = url_matches[i].strip() if i < len(url_matches) else f"https://techinsights.org/{topic.lower().replace(' ', '-')}"
                d = domain_matches[i].strip() if i < len(domain_matches) else "techinsights.org"
                s = snippet_matches[i].strip() if i < len(snippet_matches) else f"Detailed insights and verified data on {topic}."
                results_found.append({
                    "title": t,
                    "url": u,
                    "domain": d,
                    "summary": s,
                    "credibility_score": 0.96
                })

            if not results_found:
                results_found = [
                    {
                        "title": f"Complete 2026 Benchmark Guide to {topic}",
                        "url": f"https://techinsights.org/{topic.lower().replace(' ', '-')}",
                        "domain": "techinsights.org",
                        "summary": f"Comprehensive performance breakdown and latest verified benchmarks on {topic}.",
                        "credibility_score": 0.97
                    },
                    {
                        "title": f"Industry Analysis: Key Metrics and Breakthroughs in {topic}",
                        "url": f"https://consumerreports.com/{topic.lower().replace(' ', '-')}-overview",
                        "domain": "consumerreports.com",
                        "summary": f"User adoption metrics, hardware efficiency, and market trends for {topic}.",
                        "credibility_score": 0.95
                    }
                ]

            claims_data = [
                {"claim": f"{topic} has demonstrated major technical and performance upgrades in 2026.", "source_url": results_found[0]["url"], "verified": True, "confidence": 0.98},
                {"claim": f"Optimizing core configurations in {topic} yields measurable speed and efficiency gains.", "source_url": results_found[1]["url"] if len(results_found) > 1 else results_found[0]["url"], "verified": True, "confidence": 0.96}
            ]

            data = {
                "sources": results_found,
                "claims": claims_data
            }
            content = json.dumps(data) if json_mode else f"Research summary on {topic} completed."

        # 5. Trend Scout
        elif "trend scout" in sys_lower or "social media trend scout" in sys_lower or "viral short-form video trends" in prompt_lower:
            data = {
                "trends": [
                    {
                        "angle": f"The Shocking Reality Behind {topic}",
                        "search_volume": "180K / week",
                        "relevance_score": 0.98,
                        "viral_hook_idea": f"Why 99% of people are completely wrong about {topic}.",
                    },
                    {
                        "angle": f"The 2026 {topic} Shift Nobody Saw Coming",
                        "search_volume": "125K / week",
                        "relevance_score": 0.94,
                        "viral_hook_idea": f"The single change in {topic} that changes everything.",
                    }
                ]
            }
            content = json.dumps(data) if json_mode else f"Top trending angle: The Shocking Reality Behind {topic}"

        # 6. Storyboard
        elif "creative director" in sys_lower or "storyboard" in sys_lower or "storyboard" in prompt_lower:
            scenes_data = []
            try:
                scenes_match = re.search(r'(\[.*?\{.*?"scene_number".*?\}.*?\])', prompt, re.DOTALL)
                if scenes_match:
                    scenes_data = json.loads(scenes_match.group(1))
            except Exception:
                pass

            if not scenes_data:
                scenes_data = [
                    {"scene_number": 1, "duration_seconds": 4.0, "visual_description": f"Cinematic hero shot of {topic} with vibrant studio lighting"},
                    {"scene_number": 2, "duration_seconds": 5.5, "visual_description": f"Detailed macro demonstration of {topic}"},
                    {"scene_number": 3, "duration_seconds": 5.5, "visual_description": f"High performance workflow visualization for {topic}"},
                    {"scene_number": 4, "duration_seconds": 4.0, "visual_description": f"Engaging call to action animated badge for {topic}"}
                ]

            cam_angles = ["medium_close_up", "macro_zoom", "wide_cinematic", "close_up"]
            transitions = ["whip_pan", "glitch_cut", "hard_cut", "fade_to_black"]

            sb_scenes = []
            for i, sc in enumerate(scenes_data):
                sb_scenes.append({
                    "scene_number": sc.get("scene_number", i + 1),
                    "duration_seconds": float(sc.get("duration_seconds", 4.5)),
                    "visual_prompt": sc.get("visual_description", f"Cinematic visual for scene {i+1}"),
                    "media_type": "video",
                    "transition": transitions[i % len(transitions)],
                    "subtitle_style": "karaoke_pop",
                    "camera_angle": cam_angles[i % len(cam_angles)]
                })

            data = {
                "total_duration_seconds": sum(s["duration_seconds"] for s in sb_scenes),
                "music_mood": "energetic_tech",
                "target_bpm": 128,
                "scenes": sb_scenes
            }
            content = json.dumps(data) if json_mode else f"Storyboard generated with {len(sb_scenes)} scenes."

        # 7. Localization
        elif "localization" in sys_lower or "translate" in prompt_lower or "idiomatically adapt" in prompt_lower:
            in_script = {}
            first_brace = prompt.find("{")
            last_brace = prompt.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                try:
                    in_script = json.loads(prompt[first_brace:last_brace + 1])
                except Exception:
                    pass

            target_lang = lang or "hi"
            in_scenes = in_script.get("scenes", [])

            if target_lang == "hi":
                default_hi_vo = [
                    f"क्या आप {topic} के बारे में यह चौंकाने वाला सच जानते हैं? 90% लोगों को इसका अंदाज़ा भी नहीं है।",
                    "पुराने तरीकों में आपका बहुत समय और बैटरी बर्बाद होती है, जिसे ज्यादातर लोग नज़रअंदाज़ कर देते हैं।",
                    "लेकिन इस नए अपग्रेड को ऑन करते ही आपकी परफॉरमेंस 3 गुना तेज़ हो जाती है और बैटरी भी बचती है।",
                    "क्या आप इसे आज़माने वाले हैं? नीचे कमेंट में अपनी राय बताएं और ऐसे ही टिप्स के लिए फॉलो करें!"
                ]
                default_hi_overlay = [
                    f"{topic.upper()} का सच! ⚡",
                    "बड़ा नुकसान! ⚠️",
                    "3X तेज़ परफॉरमेंस 🚀",
                    "नीचे कमेंट करें! 👇"
                ]
                hindi_scenes = []
                num_scenes = len(in_scenes) if in_scenes else 4
                for i in range(num_scenes):
                    sc = in_scenes[i] if i < len(in_scenes) and isinstance(in_scenes[i], dict) else {}
                    sc_num = sc.get("scene_number", i + 1)
                    dur = sc.get("duration_seconds", 4.0 if i in [0, num_scenes - 1] else 5.5)
                    pres = sc.get("presenter_visible", True if i in [0, num_scenes - 1] else False)
                    bg = sc.get("background_query", f"{topic} technology")
                    vis = sc.get("visual_description", f"High production cinematic shot of {topic}")

                    hindi_scenes.append({
                        "scene_number": sc_num,
                        "duration_seconds": dur,
                        "visual_description": vis,
                        "voiceover_text": default_hi_vo[i % len(default_hi_vo)],
                        "on_screen_text": default_hi_overlay[i % len(default_hi_overlay)],
                        "presenter_visible": pres,
                        "background_query": bg
                    })

                data = {
                    "title": f"{topic}: पूरा सच और गुप्त बातें ⚡",
                    "hook": hindi_scenes[0]["voiceover_text"] if hindi_scenes else f"क्या आप {topic} के बारे में यह सच जानते हैं?",
                    "language": "hi",
                    "scenes": hindi_scenes,
                    "claims": in_script.get("claims", [{"claim": f"{topic} upgrades verified.", "verified": True}]),
                    "call_to_action": "नीचे कमेंट करें और डेली टिप्स के लिए फॉलो करें!"
                }
            elif target_lang == "es":
                default_es_vo = [
                    f"El 99% de las personas están completamente equivocadas sobre {topic}.",
                    "Los métodos tradicionales te hacen perder horas de esfuerzo y batería sin que te des cuenta.",
                    "Las últimas pruebas confirman que esta técnica duplica tu rendimiento en menos de la mitad del tiempo.",
                    "¿Vas a probar esto hoy? ¡Deja tu opinión en los comentarios y síguenos!"
                ]
                default_es_overlay = [
                    f"¡LA VERDAD DE {topic.upper()}! ⚡",
                    "¡EL GRAN ERROR! ⚠️",
                    "RENDIMIENTO 2X 🚀",
                    "¡COMENTA ABAJO! 👇"
                ]
                es_scenes = []
                num_scenes = len(in_scenes) if in_scenes else 4
                for i in range(num_scenes):
                    sc = in_scenes[i] if i < len(in_scenes) and isinstance(in_scenes[i], dict) else {}
                    sc_num = sc.get("scene_number", i + 1)
                    dur = sc.get("duration_seconds", 4.0 if i in [0, num_scenes - 1] else 5.5)
                    pres = sc.get("presenter_visible", True if i in [0, num_scenes - 1] else False)
                    bg = sc.get("background_query", f"{topic} technology")
                    vis = sc.get("visual_description", f"High production cinematic shot of {topic}")

                    es_scenes.append({
                        "scene_number": sc_num,
                        "duration_seconds": dur,
                        "visual_description": vis,
                        "voiceover_text": default_es_vo[i % len(default_es_vo)],
                        "on_screen_text": default_es_overlay[i % len(default_es_overlay)],
                        "presenter_visible": pres,
                        "background_query": bg
                    })

                data = {
                    "title": f"La Verdad Oculta de {topic} ⚡",
                    "hook": es_scenes[0]["voiceover_text"] if es_scenes else f"La verdad sobre {topic}",
                    "language": "es",
                    "scenes": es_scenes,
                    "claims": in_script.get("claims", [{"claim": f"{topic} verified.", "verified": True}]),
                    "call_to_action": "¡Comenta abajo tu opinión y síguenos para más!"
                }
            else:
                data = in_script if in_script else {
                    "title": f"The Shocking Truth About {topic} ⚡",
                    "hook": f"Everything you were told about {topic} is based on an outdated myth.",
                    "language": target_lang,
                    "scenes": []
                }
                data["language"] = target_lang

            content = json.dumps(data) if json_mode else data.get("hook", "Localized script")

        # 8. Scriptwriter
        elif "scriptwriter" in sys_lower or "script" in sys_lower or "write a powerful" in prompt_lower or "write a high-converting" in prompt_lower:
            topic_lower = topic.lower()

            if seed_script:
                seed_lines = [l.strip() for l in seed_script.strip().split("\n") if l.strip()]
                hook_seed = seed_lines[0] if seed_lines else f"The real truth about {topic}"
                body_seed = seed_lines[1] if len(seed_lines) > 1 else "Modern testing reveals massive performance differences."
                proof_seed = seed_lines[2] if len(seed_lines) > 2 else "Verified benchmarks confirm dramatic gains."

                data = {
                    "title": f"The Unspoken Truth About {topic} ⚡",
                    "hook": f"Here is the truth about {topic} that nobody is talking about: {hook_seed}",
                    "language": lang,
                    "scenes": [
                        {
                            "scene_number": 1,
                            "duration_seconds": 4.0,
                            "visual_description": f"Cinematic dynamic split-screen introducing {topic} with glowing neon HUD",
                            "voiceover_text": f"Here is the truth about {topic} that nobody is talking about: {hook_seed}",
                            "on_screen_text": f"{topic.upper()} EXPOSED ⚡",
                            "presenter_visible": True,
                            "background_query": f"{topic} breakthrough technology"
                        },
                        {
                            "scene_number": 2,
                            "duration_seconds": 5.5,
                            "visual_description": f"Fast-paced macro demonstration showing unexpected friction and problem: {body_seed}",
                            "voiceover_text": f"While everyone follows the default advice, {body_seed}",
                            "on_screen_text": "THE HIDDEN FLAW ⚠️",
                            "presenter_visible": False,
                            "background_query": f"{topic} close up details"
                        },
                        {
                            "scene_number": 3,
                            "duration_seconds": 5.5,
                            "visual_description": f"High-contrast proof breakdown illustrating concrete facts: {proof_seed}",
                            "voiceover_text": f"Independent real-world verification proves it: {proof_seed}",
                            "on_screen_text": "PROVEN RESULTS 🚀",
                            "presenter_visible": False,
                            "background_query": f"{topic} data analytics benchmark"
                        },
                        {
                            "scene_number": 4,
                            "duration_seconds": 4.0,
                            "visual_description": "Presenter pointing to interactive comment badge overlay",
                            "voiceover_text": f"Would you switch right now, or stick to what you have? Drop your vote below and follow!",
                            "on_screen_text": "DROP YOUR VOTE! 👇",
                            "presenter_visible": True,
                            "background_query": "subscribe follow button modern"
                        }
                    ],
                    "claims": claims_from_prompt or [{"claim": f"User verified points for {topic}.", "verified": True}],
                    "call_to_action": call_to_action
                }
            elif any(k in topic_lower for k in ["hydrogen", "ev", "electric car", "tesla", "car", "vehicle"]):
                data = {
                    "title": "Electric vs Hydrogen: The 2026 Winner Revealed ⚡",
                    "hook": "99% of drivers think Electric cars won the race, but this Hydrogen breakthrough changes everything.",
                    "language": lang,
                    "scenes": [
                        {
                            "scene_number": 1,
                            "duration_seconds": 4.0,
                            "visual_description": "Split screen comparing rapid 3-minute hydrogen pump refuel versus long EV charging line with neon HUD stats",
                            "voiceover_text": "99% of drivers think Electric cars won the race, but this Hydrogen breakthrough changes everything.",
                            "on_screen_text": "EV VS HYDROGEN ⚡",
                            "presenter_visible": True,
                            "background_query": "electric car charging station technology"
                        },
                        {
                            "scene_number": 2,
                            "duration_seconds": 5.5,
                            "visual_description": "Thermal degradation scan of lithium battery in winter versus continuous hydrogen fuel cell operation",
                            "voiceover_text": "While lithium battery packs lose 20% range in freezing winter and take 45 minutes to recharge, Hydrogen refuels in just 3 minutes flat.",
                            "on_screen_text": "3-MIN REFUEL VS HOURS ⏱️",
                            "presenter_visible": False,
                            "background_query": "hydrogen fuel cell car engine"
                        },
                        {
                            "scene_number": 3,
                            "duration_seconds": 5.5,
                            "visual_description": "High tech animated global infrastructure map showing zero-emission green hydrogen transit corridors",
                            "voiceover_text": "Toyota and BMW just doubled down on solid-state fuel cells delivering over 700 miles per tank with zero toxic mineral mining.",
                            "on_screen_text": "700+ MILE RANGE 🚀",
                            "presenter_visible": False,
                            "background_query": "futuristic highway concept transportation"
                        },
                        {
                            "scene_number": 4,
                            "duration_seconds": 4.0,
                            "visual_description": "Presenter holding interactive digital voting badge with subscribe animation",
                            "voiceover_text": "Would you buy a 3-minute refuel Hydrogen car, or stick with battery EV? Comment your vote below and follow!",
                            "on_screen_text": "WHICH WINS? VOTE! 👇",
                            "presenter_visible": True,
                            "background_query": "subscribe follow button modern"
                        }
                    ],
                    "claims": [
                        {"claim": "Hydrogen vehicles refuel in 3 minutes with over 500 miles range.", "verified": True}
                    ],
                    "call_to_action": call_to_action
                }
            elif any(k in topic_lower for k in ["iphone", "apple", "phone", "smartphone", "android", "samsung"]):
                data = {
                    "title": f"The Hidden {topic} Setting Apple Never Wanted You to Find 📱",
                    "hook": f"If you own an {topic}, there is a hidden hardware setting that completely changes your device.",
                    "language": lang,
                    "scenes": [
                        {
                            "scene_number": 1,
                            "duration_seconds": 4.0,
                            "visual_description": f"Cinematic macro shot of {topic} glowing display with dynamic island fluid animation",
                            "voiceover_text": f"If you own an {topic}, there is a hidden hardware setting that completely changes your device.",
                            "on_screen_text": f"SECRET {topic.upper()} TRICK! 📱",
                            "presenter_visible": True,
                            "background_query": "sleek modern smartphone display"
                        },
                        {
                            "scene_number": 2,
                            "duration_seconds": 5.5,
                            "visual_description": "Fast screen navigation entering Camera menu toggling Apple ProRes and 4K Cinema stabilization",
                            "voiceover_text": "First, open Camera settings and toggle on ProRes with Cinema stabilization. Your video quality will instantly jump 400%.",
                            "on_screen_text": "CINEMA 4K UNLOCKED 🎥",
                            "presenter_visible": False,
                            "background_query": "professional mobile video production"
                        },
                        {
                            "scene_number": 3,
                            "duration_seconds": 5.5,
                            "visual_description": "Battery health analysis graph showing background app refresh power consumption drop to zero",
                            "voiceover_text": "Next, disable Background App Refresh and Analytics tracking to immediately reclaim up to 4 extra hours of daily battery life.",
                            "on_screen_text": "DOUBLE BATTERY LIFE 🔋",
                            "presenter_visible": False,
                            "background_query": "fast charging battery technology"
                        },
                        {
                            "scene_number": 4,
                            "duration_seconds": 4.0,
                            "visual_description": "Presenter holding phone and pointing to comment prompt badge overlay",
                            "voiceover_text": f"Are you using these features on your phone, or is your battery still draining? Comment your model below and follow for daily tips!",
                            "on_screen_text": "DROP YOUR MODEL! 👇",
                            "presenter_visible": True,
                            "background_query": "subscribe follow button modern"
                        }
                    ],
                    "claims": [
                        {"claim": f"Optimizing settings on {topic} doubles battery longevity and enables ProRes.", "verified": True}
                    ],
                    "call_to_action": call_to_action
                }
            elif any(k in topic_lower for k in ["ai", "artificial intelligence", "deepseek", "chatgpt", "claude", "agent", "llm", "antigravity"]):
                data = {
                    "title": f"The {topic} Benchmark That Exposes Big Tech ⚡",
                    "hook": f"The newest {topic} benchmark just dropped, and it exposes a massive lie the tech giants told us.",
                    "language": lang,
                    "scenes": [
                        {
                            "scene_number": 1,
                            "duration_seconds": 4.0,
                            "visual_description": "High-tech neon server room with holographic AI architecture neural network visualization",
                            "voiceover_text": f"The newest {topic} benchmark just dropped, and it exposes a massive lie the tech giants told us.",
                            "on_screen_text": f"{topic.upper()} EXPOSED ⚡",
                            "presenter_visible": True,
                            "background_query": "artificial intelligence neural network concept"
                        },
                        {
                            "scene_number": 2,
                            "duration_seconds": 5.5,
                            "visual_description": "Benchmark graph comparison showing open weights crushing closed proprietary models at a fraction of compute cost",
                            "voiceover_text": "While everyone pays expensive monthly fees for closed APIs, lightweight open architectures just matched frontier models at 10% of the cost.",
                            "on_screen_text": "90% CHEAPER & FASTER 🚀",
                            "presenter_visible": False,
                            "background_query": "data analytics dashboard futuristic technology"
                        },
                        {
                            "scene_number": 3,
                            "duration_seconds": 5.5,
                            "visual_description": "Developer screen showing automated multi-agent code workflows running completely local on laptop hardware",
                            "voiceover_text": "Engineers are now automating 70% of repetitive pipeline builds while running full inference locally with zero cloud dependence.",
                            "on_screen_text": "100% LOCAL PRIVACY 🔒",
                            "presenter_visible": False,
                            "background_query": "software developer coding modern tech"
                        },
                        {
                            "scene_number": 4,
                            "duration_seconds": 4.0,
                            "visual_description": "Presenter gesturing to dynamic voting poll badge with follow prompt",
                            "voiceover_text": "Are you still paying for closed AI models, or switching to open source? Drop your opinion below and follow!",
                            "on_screen_text": "WHICH SIDE ARE YOU ON? 👇",
                            "presenter_visible": True,
                            "background_query": "follow button animation"
                        }
                    ],
                    "claims": [
                        {"claim": f"Modern open-weight {topic} matches frontier models at a fraction of compute costs.", "verified": True}
                    ],
                    "call_to_action": call_to_action
                }
            else:
                data = {
                    "title": f"The Shocking Truth About {topic} ⚡",
                    "hook": f"Everything you were told about {topic} is based on an outdated myth from five years ago.",
                    "language": lang,
                    "scenes": [
                        {
                            "scene_number": 1,
                            "duration_seconds": 4.0,
                            "visual_description": f"High-energy cinematic visuals introducing {topic} with dramatic lighting and glitch transitions",
                            "voiceover_text": f"Everything you were told about {topic} is based on an outdated myth from five years ago.",
                            "on_screen_text": f"{topic.upper()} REVEALED ⚡",
                            "presenter_visible": True,
                            "background_query": f"{topic} technology breakthrough"
                        },
                        {
                            "scene_number": 2,
                            "duration_seconds": 5.5,
                            "visual_description": f"Data visualization graph and real-world testing footage demonstrating hidden friction in {topic}",
                            "voiceover_text": "The conventional approach burns hours of wasted effort and produces diminishing returns that 90% of people simply accept as normal.",
                            "on_screen_text": "THE HIDDEN PROBLEM ⚠️",
                            "presenter_visible": False,
                            "background_query": f"{topic} performance benchmark"
                        },
                        {
                            "scene_number": 3,
                            "duration_seconds": 5.5,
                            "visual_description": "Split screen showing modern high-efficiency technique accelerating results by 300%",
                            "voiceover_text": "Brand-new verified data shows that modern high-efficiency methods deliver 3 times greater results in less than half the time.",
                            "on_screen_text": "3X FASTER RESULTS 📈",
                            "presenter_visible": False,
                            "background_query": "modern high speed tech workflow"
                        },
                        {
                            "scene_number": 4,
                            "duration_seconds": 4.0,
                            "visual_description": "Presenter directly asking viewer for their thoughts with interactive poll badge",
                            "voiceover_text": "Are you sticking with the old way, or ready to upgrade? Comment your perspective below and follow for daily deep dives!",
                            "on_screen_text": "COMMENT YOUR VIEW! 👇",
                            "presenter_visible": True,
                            "background_query": "follow button animation"
                        }
                    ],
                    "claims": [
                        {"claim": f"Recent advancements in {topic} deliver measurable efficiency gains.", "verified": True}
                    ],
                    "call_to_action": call_to_action
                }
            content = json.dumps(data) if json_mode else data["hook"]

        else:
            data = {"status": "success", "message": "Standard mock response"}
            content = json.dumps(data) if json_mode else "Standard mock completion"

        latency = (time.time() - start_time) * 1000.0
        return LLMResponse(
            content=content,
            model=self.model_name,
            input_tokens=150,
            output_tokens=300,
            cost_usd=0.0,
            latency_ms=latency
        )
