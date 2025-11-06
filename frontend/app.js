// app.js - VERSÃO 13.0 (FINAL E CORRIGIDA)
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Seleção dos Elementos e Configurações ---
    const queryBtn = document.getElementById('query-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const ipInput = document.getElementById('ip-input');
    const resultsTable = document.getElementById('results-table');
    const resultsBody = document.getElementById('results-body');
    const loadingSpinner = document.getElementById('loading-spinner');
    const internalModeCheckbox = document.getElementById('internal-mode-checkbox');

    const API_BASE_URL = 'http://127.0.0.1:5000';
    const API_SECRET_KEY = 'secret-key-for-ip-intel-api-12345-xyz';

    let currentTableData = [];

    // --- 2. Funções Auxiliares ---

    const showLoading = (isLoading ) => {
        loadingSpinner.classList.toggle('hidden', !isLoading);
    };

    const renderTable = (data, isInternal = false) => {
        resultsBody.innerHTML = '';
        currentTableData = data;
        exportCsvBtn.classList.toggle('hidden', data.length === 0);

        const headers = resultsTable.querySelector('thead tr');
        if (isInternal) {
            headers.innerHTML = `
                <th data-column="ip">IP</th>
                <th data-column="open_ports_details">Portas e Serviços</th>
                <th data-column="security_recommendations">Recomendações</th>
                <th data-column="status">Status</th>
            `;
        } else {
            headers.innerHTML = `
                <th data-column="ip">IP</th>
                <th data-column="hostname">Hostname</th>
                <th data-column="country">País</th>
                <th data-column="city">Cidade</th>
                <th data-column="open_ports">Portas Abertas</th>
                <th data-column="abuse_score">Score Abuso (%)</th>
                <th data-column="status">Status</th>
            `;
        }

        data.forEach(item => {
            const row = document.createElement('tr');
            let statusClass = '';
            if (item.status?.includes('cached')) statusClass = 'status-cached';
            if (item.status?.includes('analyzed')) statusClass = 'status-analyzed';
            if (item.status?.includes('error') || item.status?.includes('Unauthorized')) statusClass = 'status-error';

            const getValue = (value) => (value !== null && value !== undefined) ? value : 'N/A';

            if (isInternal) {
                // AQUI ESTÁ A CORREÇÃO FINAL E SIMPLIFICADA
                const recommendationsText = Array.isArray(item.security_recommendations) ? item.security_recommendations.map(r => `[${r.risk}] ${r.details}`).join('; ') : getValue(item.security_recommendations);

                row.innerHTML = `
                    <td>${getValue(item.ip)}</td>
                    <td>${getValue(item.open_ports_details)}</td>
                    <td>${recommendationsText}</td>
                    <td class="${statusClass}">${getValue(item.status)}</td>
                `;
            } else {
                row.innerHTML = `
                    <td>${getValue(item.ip)}</td>
                    <td>${getValue(item.hostname)}</td>
                    <td>${getValue(item.country)}</td>
                    <td>${getValue(item.city)}</td>
                    <td>${getValue(item.open_ports)}</td>
                    <td>${getValue(item.abuse_score)}</td>
                    <td class="${statusClass}">${getValue(item.status)}</td>
                `;
            }
            resultsBody.appendChild(row);
        });
    };

    // --- 3. Event Listeners ---

    queryBtn.addEventListener('click', async () => {
        const ips = ipInput.value.trim().split('\n').filter(ip => ip);
        if (ips.length === 0) {
            alert('Por favor, insira pelo menos um endereço de IP para consultar.');
            return;
        }
        showLoading(true);
        try {
            const queryPromises = ips.map(ip =>
                fetch(`${API_BASE_URL}/query/${ip}`, { headers: { 'X-API-Key': API_SECRET_KEY } })
                .then(res => res.ok ? res.json() : res.json().then(err => ({ ip, status: `Erro: ${err.error}` })))
                .catch(err => ({ ip, status: `Erro: ${err.message}` }))
            );
            const results = await Promise.all(queryPromises);
            renderTable(results.map(r => ({ ...r, status: r.status || 'Consultado' })), false);
        } catch (error) {
            alert(`Ocorreu um erro inesperado: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    analyzeBtn.addEventListener('click', async () => {
        const ips = ipInput.value.trim().split('\n').filter(ip => ip);
        if (ips.length === 0) {
            alert('Por favor, insira pelo menos um endereço de IP para analisar.');
            return;
        }
        showLoading(true);
        try {
            const isInternalMode = internalModeCheckbox.checked;
            const endpoint = isInternalMode ? `${API_BASE_URL}/analyze/internal` : `${API_BASE_URL}/analyze`;

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-Key': API_SECRET_KEY },
                body: JSON.stringify({ ips })
            });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro desconhecido na análise');
            }

            if (isInternalMode) {
                renderTable(data.map(item => ({ ...item, status: item.status || 'Analisado (Interno)' })), true);
            } else {
                const detailPromises = data.analysis_summary.map(summary =>
                    fetch(`${API_BASE_URL}/query/${summary.ip}`, { headers: { 'X-API-Key': API_SECRET_KEY } })
                    .then(res => res.json().then(details => ({ ...details, status: summary.status })))
                );
                const detailedReports = await Promise.all(detailPromises);
                renderTable(detailedReports, false);
            }
        } catch (error) {
            alert(`Erro no processo de análise: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    exportCsvBtn.addEventListener('click', () => {
        if (currentTableData.length === 0) return;
        const headers = Array.from(resultsTable.querySelectorAll('thead th')).map(th => th.dataset.column);
        const csvRows = [headers.join(',')];
        currentTableData.forEach(item => {
            const row = headers.map(header => {
                let value = item[header];
                if (header === 'security_recommendations' && Array.isArray(value)) {
                    value = value.map(r => `[${r.risk}] ${r.details}`).join('; ');
                }
                const escaped = ('' + (value ?? '')).replace(/"/g, '""');
                return `"${escaped}"`;
            });
            csvRows.push(row.join(','));
        });
        const csvString = csvRows.join('\n');
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'ip_intelligence_report.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    resultsTable.querySelector('thead').addEventListener('click', (e) => {
        if (e.target.tagName !== 'TH') return;
        const headerCell = e.target;
        const columnKey = headerCell.dataset.column;
        if (!columnKey) return;
        const sortOrder = headerCell.dataset.sortOrder = headerCell.dataset.sortOrder === 'asc' ? 'desc' : 'asc';
        const sortedData = [...currentTableData].sort((a, b) => {
            const valA = a[columnKey] ?? '';
            const valB = b[columnKey] ?? '';
            if (Array.isArray(valA)) return 0;
            if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
            if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
            return 0;
        });
        renderTable(sortedData, internalModeCheckbox.checked);
    });
});
