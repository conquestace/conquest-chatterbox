try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # For Python <3.8

__version__ = version("chatterbox-tts")


try:
    from .tts import ChatterboxTTS
    from .vc import ChatterboxVC
except Exception:  # optional when dependencies missing
    ChatterboxTTS = None
    ChatterboxVC = None
from .audio_editing import (
    splice_audios,
    trim_audio,
    insert_audio,
    delete_segment,
    crossfade,
)
