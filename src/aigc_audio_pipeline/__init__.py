"""aigc-audio-pipeline: Production Chinese radio-drama & multi-cast audio drama engine."""

from .batch_queue import BatchWorkspace, canonical_episode_stem, measure_ebur128, run_episode_queue
from .compiler import (
    compile_episode_cue_sheet,
    extract_spoken_quotes_in_chapter,
    parse_chapter_paragraphs,
    save_episode_scripts,
)
from .drama3_adapter import (
    export_colab_96gb_bundle,
    strip_drama3_markup,
    translate_cue_to_drama3_input,
    trim_edge_silence_wav,
)
from .polyphones import apply_xianxia_polyphone_overrides, compute_tts_text_override

__version__ = "1.1.0"

__all__ = [
    "__version__",
    "BatchWorkspace",
    "apply_xianxia_polyphone_overrides",
    "canonical_episode_stem",
    "compile_episode_cue_sheet",
    "compute_tts_text_override",
    "export_colab_96gb_bundle",
    "extract_spoken_quotes_in_chapter",
    "measure_ebur128",
    "parse_chapter_paragraphs",
    "run_episode_queue",
    "save_episode_scripts",
    "strip_drama3_markup",
    "translate_cue_to_drama3_input",
    "trim_edge_silence_wav",
]
