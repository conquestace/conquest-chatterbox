from flask import Blueprint, request, send_file, jsonify
import io
import soundfile as sf

from ..models import get_tts_model
from ..utils import set_seed


tts_bp = Blueprint("tts", __name__)


@tts_bp.route("/tts", methods=["POST"])
def tts():
    data = request.get_json() or {}
    text = data.get("text", "")
    audio_prompt_path = data.get("audio_prompt_path")
    exaggeration = float(data.get("exaggeration", 0.5))
    temperature = float(data.get("temperature", 0.8))
    seed_num = int(data.get("seed", 0))
    cfg_weight = float(data.get("cfg_weight", 0.5))
    min_p = float(data.get("min_p", 0.05))
    top_p = float(data.get("top_p", 1.0))
    repetition_penalty = float(data.get("repetition_penalty", 1.2))

    if seed_num:
        set_seed(seed_num)

    model = get_tts_model()
    wav = model.generate(
        text,
        audio_prompt_path=audio_prompt_path,
        exaggeration=exaggeration,
        temperature=temperature,
        cfg_weight=cfg_weight,
        min_p=min_p,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
    )

    buf = io.BytesIO()
    sf.write(buf, wav.squeeze(0).cpu().numpy(), model.sr, format="wav")
    buf.seek(0)
    return send_file(buf, mimetype="audio/wav", as_attachment=True, download_name="output.wav")
