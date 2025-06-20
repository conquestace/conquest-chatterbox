async function fetchAudio(url, options, audioEl) {
    const resp = await fetch(url, options);
    if (!resp.ok) {
        alert('Error processing request');
        return;
    }
    const blob = await resp.blob();
    const urlObj = URL.createObjectURL(blob);
    audioEl.src = urlObj;
    audioEl.style.display = 'block';
    audioEl.play();
}

function bindJsonForm(formId, url, audioId) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {};
        new FormData(form).forEach((v, k) => { data[k] = v; });
        await fetchAudio(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }, document.getElementById(audioId));
    });
}

function bindForm(formId, url, audioId) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = new FormData(form);
        await fetchAudio(url, { method: 'POST', body: data }, document.getElementById(audioId));
    });
}

document.addEventListener('DOMContentLoaded', function () {
    bindJsonForm('tts-form', '/api/tts', 'tts-audio');
    bindForm('vc-form', '/api/vc', 'vc-audio');
    bindForm('edit-splice', '/api/edit/splice', 'edit-audio');
    bindForm('edit-trim', '/api/edit/trim', 'edit-audio');
    bindForm('edit-insert', '/api/edit/insert', 'edit-audio');
    bindForm('edit-delete', '/api/edit/delete', 'edit-audio');
    bindForm('edit-crossfade', '/api/edit/crossfade', 'edit-audio');
});
