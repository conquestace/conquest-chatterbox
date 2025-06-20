try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # For Python <3.8

__version__ = version("chatterbox-tts")


# Lazy import heavy modules so basic utilities like ``audio_editing`` can be
# used without installing the full set of dependencies required for TTS/VC.
try:  # pragma: no cover - optional heavy deps
    from .tts import ChatterboxTTS
    from .vc import ChatterboxVC
except Exception:  # noqa: BLE001
    ChatterboxTTS = None
    ChatterboxVC = None
from .audio_editing import (
    splice_audios,
    trim_audio,
    insert_audio,
    delete_segment,
    crossfade,
)
