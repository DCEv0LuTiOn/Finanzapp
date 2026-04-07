/**
 * Hilfsfunktionen für Farben
 */
function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    let color = '#';
    for (let i = 0; i < 3; i++) {
        const value = (hash >> (i * 8)) & 0xFF;
        const softValue = Math.min(Math.max(value, 70), 200); 
        color += softValue.toString(16).padStart(2, '0');
    }
    return color;
}

function getDynamicColor(label) {
    if (!label || label === "Keine Kategorie" || label === "null") return '#858796';
    return stringToColor(label);
}

/**
 * Hauptfunktion: Erstellt alle drei Charts
 */
function initFinanceChartsFromDict(dataDict) {
    const allLabels = Object.keys(dataDict);

    // 1. Daten für Ausgaben (Doughnut)
    const labelsAusgaben = allLabels.filter(l => dataDict[l].ausgaben !== 0);
    const valuesAusgaben = labelsAusgaben.map(l => Math.abs(dataDict[l].ausgaben));
    const colorsAusgaben = labelsAusgaben.map(l => getDynamicColor(l));

    // 2. Daten für Einnahmen (Doughnut)
    const labelsEinnahmen = allLabels.filter(l => dataDict[l].einnahmen !== 0);
    const valuesEinnahmen = labelsEinnahmen.map(l => dataDict[l].einnahmen);
    const colorsEinnahmen = labelsEinnahmen.map(l => getDynamicColor(l));

    // 3. Daten für Saldo / Bilanz (Balken)
    // Wir nehmen alle Kategorien, die überhaupt Aktivität hatten
    const labelsSaldo = allLabels.filter(l => dataDict[l].ausgaben !== 0 || dataDict[l].einnahmen !== 0);
    const valuesSaldo = labelsSaldo.map(l => (dataDict[l].einnahmen + dataDict[l].ausgaben));
    // Rot bei Verlust, Grün bei Gewinn
    const colorsSaldo = valuesSaldo.map(v => v >= 0 ? '#2ecc71' : '#e74c3c');

    // Gemeinsame Optionen für Doughnuts
    const doughnutOptions = {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
        padding: 24 // Gibt dem Chart Platz, damit Segmente beim Hover nicht abgeschnitten werden
        },
        plugins: { legend: { position: 'bottom' } }
    };

    // --- CHART INITIALISIERUNG ---

    // Ausgaben Kreismonster
    new Chart(document.getElementById('chartAusgaben'), {
        type: 'doughnut',
        data: {
            labels: labelsAusgaben,
            datasets: [{ data: valuesAusgaben, backgroundColor: colorsAusgaben, hoverOffset: 25 }]
        },
        options: doughnutOptions
    });

    // Einnahmen Kreismonster
    new Chart(document.getElementById('chartEinnahmen'), {
        type: 'doughnut',
        data: {
            labels: labelsEinnahmen,
            datasets: [{ data: valuesEinnahmen, backgroundColor: colorsEinnahmen, hoverOffset: 25 }]
        },
        options: doughnutOptions
    });

    // NEU: Saldo Balkendiagramm
    const ctxSaldo = document.getElementById('chartSaldo');
    if (ctxSaldo) {
        new Chart(ctxSaldo, {
            type: 'bar',
            data: {
                labels: labelsSaldo,
                datasets: [{
                    label: 'Saldo (€)',
                    data: valuesSaldo,
                    backgroundColor: colorsSaldo,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { 
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: { grid: { display: false } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` Saldo: ${ctx.raw.toFixed(2)} €`
                        }
                    }
                }
            }
        });
    }
}