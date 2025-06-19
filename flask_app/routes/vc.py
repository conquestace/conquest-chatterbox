import io
import tempfile
import soundfile as sf
from flask import Blueprint, request, send_file

from ..models import get_vc_model


vc_bp = Blueprint("vc", __name__)


@vc_bp.route("/vc", methods=["POST"])
def voice_convert():
    if "audio" not in request.files:
        return {"error": "audio file required"}, 400

    audio_file = request.files["audio"]
    target_file = request.files.get("target_voice")

    with tempfile.NamedTemporaryFile(suffix=".wav") as src_tmp:
        audio_file.save(src_tmp.name)
        target_path = None
        if target_file:
            tgt_tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            target_file.save(tgt_tmp.name)
            target_path = tgt_tmp.name
        model = get_vc_model()
        wav = model.generate(src_tmp.name, target_voice_path=target_path)

    buf = io.BytesIO()
    sf.write(buf, wav.squeeze(0).cpu().numpy(), model.sr, format="wav")
    buf.seek(0)
    return send_file(buf, mimetype="audio/wav", as_attachment=True, download_name="converted.wav")
