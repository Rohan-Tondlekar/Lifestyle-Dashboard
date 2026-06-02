function updateMacroBar(elementId, value, target) {
    const bar = document.getElementById(elementId);
    if (!bar) return;
    const pct = Math.min(100, Math.round((value / target) * 100));
    bar.style.width = pct + '%';
    bar.setAttribute('aria-valuenow', pct);
}
