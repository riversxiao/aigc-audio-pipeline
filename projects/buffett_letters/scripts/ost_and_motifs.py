"""Canonical Documentary & Late-Night Study OST Palette + Sonic Motifs for《穿越周期的信》.

Sharing canonical `bgm_prompt` strings across acts of the same emotional arc across all 12 Season-1 episodes:
1. Establishes a distinctive NPR / Planet Money × BBC Financial Documentary × Omaha Study sonic identity.
2. Enables automatic SHA-256 stem-cache reuse in `ACE-Step 1.5 XL` on Colab 96GB G4, cutting multi-episode BGM generation time by >80%.
"""

from __future__ import annotations

BUFFETT_DOCUMENTARY_OST: dict[str, str] = {
    # Act 1: Crisis / Bubble Tension (Wall Street storm seen from a calm late-night room)
    "crisis_pulse_cello_piano": (
        "Cinematic financial documentary underscore, muted felt piano ostinato, tense low chamber cello pulse "
        "and subtle upright bass pizzicato in a quiet late-night broadcast room, restrained suspense, "
        "purely acoustic instrumental, no drums, no singing, no vocals"
    ),
    # Act 2: Omaha Study & Business Craftsmanship (Warm American fingerstyle guitar & wood resonance)
    "omaha_study_acoustic_guitar": (
        "Warm intimate American Heartland acoustic fingerstyle guitar and gentle upright double bass duet, "
        "cozy late-night mahogany study atmosphere, thoughtful and grounded storytelling underscore, "
        "purely instrumental, no drums, no singing, no vocals"
    ),
    # Act 3: Candid Confession & Sober Reflection (Minimalist jazz-inflected felt piano & warm strings)
    "candid_reflection_felt_piano": (
        "Intimate late-night reflective chamber music, warm minimalist felt piano chords and lyrical solo cello, "
        "honest candid conversation mood, subtle analog warmth, purely instrumental, no drums, no singing, no vocals"
    ),
    # Act 4: Three-Tier Playbook & Long-Term Conviction (Uplifting horizon acoustic guitar, piano & warm cello)
    "long_horizon_conviction": (
        "Inspiring warm American documentary finale underscore, fingerpicked steel-string acoustic guitar, "
        "luminous warm piano melody and hopeful chamber strings building gentle forward momentum across decades, "
        "purely instrumental, no singing, no vocals"
    ),
}

BUFFETT_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "vintage_report_page_turn": {
        "sfx_prompt": (
            "Crisp tactile turn of a heavy vintage cotton-paper annual report page on a quiet mahogany study desk, "
            "subtle warm room tone, pure foley, no human voice"
        ),
        "duration_seconds": 2.2,
    },
    "omaha_typewriter_carriage": {
        "sfx_prompt": (
            "Authentic 1980s mechanical typewriter short keystroke burst ending with a crisp metallic carriage return "
            "bell ding in a quiet wooden study, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "nyse_crisis_bell_distant": {
        "sfx_prompt": (
            "Distant resonant brass stock exchange closing bell echoing softly into a quiet late-night broadcast room, "
            "solemn financial documentary transition, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "studio_coffee_cup_settle": {
        "sfx_prompt": (
            "Warm ceramic coffee mug gently set down onto a wooden coaster in an intimate late-night podcast studio, "
            "subtle cozy room presence, pure foley, no human voice"
        ),
        "duration_seconds": 1.6,
    },
}
