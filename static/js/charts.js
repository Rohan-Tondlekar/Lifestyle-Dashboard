function initWeightChart(labels, data) {
    const isDark = document.documentElement.classList.contains('dark');
    const accent = isDark ? '#3b82f6' : '#6366f1';
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)';
    const tickColor = '#64748b';

    new Chart(document.getElementById('weightChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Weight (kg)',
                data: data,
                borderColor: accent,
                backgroundColor: accent + '1a',
                tension: 0.3,
                fill: true,
                pointBackgroundColor: accent,
                pointRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: gridColor }, ticks: { color: tickColor } },
                x: { grid: { display: false }, ticks: { color: tickColor } }
            }
        }
    });
}
