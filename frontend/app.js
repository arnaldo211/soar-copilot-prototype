// app.js - VERSÃO 11.0 (com Exportação e Ordenação)
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Seleção dos Elementos e Configurações ---
    const queryBtn = document.getElementById('query-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const ipInput = document.getElementById('ip-input');
    const resultsTable = document.getElementById('results-table');
    const resultsBody = document.getElementById('results-body');
    const loadingSpinner = document.getElementById('loading-spinner');

    const API_BASE_URL = 'http://127.0.0.1:5000';
    const API_SECRET_KEY = 'secret-key-for-ip-intel-api-12345-xyz';

    // Variável para armazenar os dados atuais da tabela
    let currentTableData = [];

    // --- 2. Funções Auxiliares ---

    const showLoading = (isLoading ) => {
        loadingSpinner.classList.toggle('hidden', !isLoading);
    };

    // Função para renderizar a tabela com base nos dados atuais
    const renderTable = (data) => {
        resultsBody.innerHTML = ''; // Limpa a tabela antes de renderizar
        currentTableData = data; // Armazena os dados atuais

        if (data.length > 0) {
            exportCsvBtn.classList.remove('hidden'); // Mostra o botão de exportar
        } else {
            exportCsvBtn.classList.add('hidden'); // Esconde se não houver dados
        }

        data.forEach(item => {
            const row = document.createElement('tr');
            let statusClass = '';
            if (item.status.includes('cached')) statusClass = 'status-cached';
            if (item.status.includes('analyzed')) statusClass = 'status-analyzed';
            if (item.status.includes('error') || item.status.includes('Unauthorized')) statusClass = 'status-error';

            const getValue = (value) => (value !== null && value !== undefined) ? value : 'N/A';

            row.innerHTML = `
                <td>${getValue(item.ip)}</td>
                <td>${getValue(item.hostname)}</td>
                <td>${getValue(item.country)}</td>
                <td>${getValue(item.city)}</td>
                <td>${getValue(item.open_ports)}</td>
                <td>${getValue(item.abuse_score)}</td>
                <td class="${statusClass}">${getValue(item.status)}</td>
            `;
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
            renderTable(results.map(r => ({ ...r, status: r.status || 'Consultado' })));
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
            const analyzeResponse = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-Key': API_SECRET_KEY },
                body: JSON.stringify({ ips })
            });
            const analyzeData = await analyzeResponse.json();
            if (!analyzeResponse.ok) throw new Error(analyzeData.error || 'Erro na análise');

            const detailPromises = analyzeData.analysis_summary.map(summary =>
                fetch(`${API_BASE_URL}/query/${summary.ip}`, { headers: { 'X-API-Key': API_SECRET_KEY } })
                .then(res => res.json().then(data => ({ ...data, status: summary.status })))
            );
            const detailedReports = await Promise.all(detailPromises);
            renderTable(detailedReports);
        } catch (error) {
            alert(`Erro no processo de análise: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // **NOVA FUNCIONALIDADE: Exportar para CSV**
    exportCsvBtn.addEventListener('click', () => {
        if (currentTableData.length === 0) return;

        const headers = Object.keys(currentTableData[0]);
        const csvRows = [headers.join(',')]; // Cabeçalho do CSV

        currentTableData.forEach(item => {
            const values = headers.map(header => {
                const escaped = ('' + (item[header] ?? '')).replace(/"/g, '""'); // Escapa aspas
                return `"${escaped}"`;
            });
            csvRows.push(values.join(','));
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

    // **NOVA FUNCIONALIDADE: Ordenação da Tabela**
    resultsTable.querySelectorAll('thead th').forEach(headerCell => {
        let sortOrder = 'asc'; // 'asc' ou 'desc'
        headerCell.addEventListener('click', () => {
            const columnKey = headerCell.dataset.column;
            if (!columnKey) return;

            // Alterna a ordem de classificação
            sortOrder = (sortOrder === 'asc') ? 'desc' : 'asc';

            const sortedData = [...currentTableData].sort((a, b) => {
                const valA = a[columnKey] ?? '';
                const valB = b[columnKey] ?? '';

                if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
                if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
                return 0;
            });
            renderTable(sortedData);
        });
    });

}); // Fim do document.addEventListener
