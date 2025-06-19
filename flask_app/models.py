try:
    import torch
    from chatterbox.tts import ChatterboxTTS
    from chatterbox.vc import ChatterboxVC
except ModuleNotFoundError as e:  # pragma: no cover - torch heavy
    raise ImportError(
        "Required dependencies for Chatterbox are not installed."
    ) from e

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

tts_model = None
vc_model = None


def get_tts_model() -> ChatterboxTTS:
    global tts_model
    if tts_model is None:
        tts_model = ChatterboxTTS.from_pretrained(DEVICE)
    return tts_model


def get_vc_model() -> ChatterboxVC:
    global vc_model
    if vc_model is None:
        vc_model = ChatterboxVC.from_pretrained(DEVICE)
    return vc_model
