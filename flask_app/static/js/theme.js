function setTheme(theme) {
    document.documentElement.className = theme;
    localStorage.setItem('theme', theme);
}

document.addEventListener('DOMContentLoaded', function () {
    const saved = localStorage.getItem('theme') || 'theme-conquestace';
    setTheme(saved);
    document.getElementById('toggle-theme').addEventListener('click', function () {
        const current = document.documentElement.className;
        const next = current === 'theme-conquestace' ? 'theme-conquestace-light' : 'theme-conquestace';
        setTheme(next);
    });
});
