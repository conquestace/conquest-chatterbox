import io
from flask import Blueprint, request, send_file
import soundfile as sf

from chatterbox.audio_editing import (
    splice_audios,
    trim_audio,
    insert_audio,
    delete_segment,
    crossfade,
)

editing_bp = Blueprint("editing", __name__)


def _load_audio(file_storage):
    data, sr = sf.read(file_storage)
    return data, sr


def _write_audio(wav, sr):
    buf = io.BytesIO()
    sf.write(buf, wav, sr, format="wav")
    buf.seek(0)
    return send_file(buf, mimetype="audio/wav", as_attachment=True, download_name="output.wav")


@editing_bp.route("/splice", methods=["POST"])
def splice_route():
    a1 = request.files.get("audio1")
    a2 = request.files.get("audio2")
    if not a1 or not a2:
        return {"error": "two audio files required"}, 400
    wav1, sr1 = _load_audio(a1)
    wav2, sr2 = _load_audio(a2)
    if sr1 != sr2:
        return {"error": "sampling rates must match"}, 400
    joined = splice_audios([wav1, wav2])
    return _write_audio(joined, sr1)


@editing_bp.route("/trim", methods=["POST"])
def trim_route():
    audio = request.files.get("audio")
    start = float(request.form.get("start", 0))
    end = float(request.form.get("end", 0))
    if not audio:
        return {"error": "audio required"}, 400
    wav, sr = _load_audio(audio)
    trimmed = trim_audio(wav, start_sec=start, end_sec=end, sr=sr)
    return _write_audio(trimmed, sr)


@editing_bp.route("/insert", methods=["POST"])
def insert_route():
    base = request.files.get("base")
    insert = request.files.get("insert")
    pos = float(request.form.get("position", 0))
    if not base or not insert:
        return {"error": "both base and insert audio required"}, 400
    b_wav, sr = _load_audio(base)
    i_wav, _ = _load_audio(insert)
    out = insert_audio(b_wav, i_wav, pos, sr=sr)
    return _write_audio(out, sr)


@editing_bp.route("/delete", methods=["POST"])
def delete_route():
    audio = request.files.get("audio")
    start = float(request.form.get("start", 0))
    end = float(request.form.get("end", 0))
    if not audio:
        return {"error": "audio required"}, 400
    wav, sr = _load_audio(audio)
    out = delete_segment(wav, start, end, sr=sr)
    return _write_audio(out, sr)


@editing_bp.route("/crossfade", methods=["POST"])
def crossfade_route():
    a1 = request.files.get("audio1")
    a2 = request.files.get("audio2")
    dur = float(request.form.get("duration", 0.01))
    if not a1 or not a2:
        return {"error": "two audio files required"}, 400
    wav1, sr1 = _load_audio(a1)
    wav2, sr2 = _load_audio(a2)
    if sr1 != sr2:
        return {"error": "sampling rates must match"}, 400
    out = crossfade(wav1, wav2, duration_sec=dur, sr=sr1)
    return _write_audio(out, sr1)
