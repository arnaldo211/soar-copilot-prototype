// app.js - VERSÃO 10.0 (com Autenticação)
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Seleção dos Elementos e Configurações ---
    const queryBtn = document.getElementById('query-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const ipInput = document.getElementById('ip-input');
    const resultsBody = document.getElementById('results-body');
    const loadingSpinner = document.getElementById('loading-spinner');

    const API_BASE_URL = 'http://127.0.0.1:5000';
    // Chave secreta para autenticar com a API.
    const API_SECRET_KEY = 'secret-key-for-ip-intel-api-12345-xyz';

    // --- 2. Funções Auxiliares ---

    const showLoading = (isLoading ) => {
        loadingSpinner.classList.toggle('hidden', !isLoading);
    };

    const addRowToTable = (data, status = 'Consultado') => {
        const row = document.createElement('tr');
        let statusClass = '';
        if (status.includes('cached')) statusClass = 'status-cached';
        if (status.includes('analyzed')) statusClass = 'status-analyzed';
        if (status.includes('error') || status.includes('Unauthorized')) statusClass = 'status-error';

        const getValue = (value) => (value !== null && value !== undefined) ? value : 'N/A';

        row.innerHTML = `
            <td>${getValue(data.ip || data.IP)}</td>
            <td>${getValue(data.hostname)}</td>
            <td>${getValue(data.country)}</td>
            <td>${getValue(data.city)}</td>
            <td>${getValue(data.open_ports)}</td>
            <td>${getValue(data.abuse_score)}</td>
            <td class="${statusClass}">${status}</td>
        `;
        resultsBody.appendChild(row);
    };

    // --- 3. Event Listeners dos Botões ---

    // Evento do botão "Consultar do Banco"
    queryBtn.addEventListener('click', async () => {
        const ips = ipInput.value.trim().split('\n').filter(ip => ip);
        if (ips.length === 0) {
            alert('Por favor, insira pelo menos um endereço de IP para consultar.');
            return;
        }

        resultsBody.innerHTML = '';
        showLoading(true);

        try {
            const queryPromises = ips.map(ip => {
                return fetch(`${API_BASE_URL}/query/${ip}`, {
                    headers: { 'X-API-Key': API_SECRET_KEY } // <-- AUTENTICAÇÃO
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => ({ ip: ip, error: err.error }));
                    }
                    return response.json();
                })
                .catch(networkError => ({ ip: ip, error: networkError.message }));
            });

            const results = await Promise.all(queryPromises);

            results.forEach(result => {
                if (result.error) {
                    addRowToTable({ ip: result.ip }, `Erro: ${result.error}`);
                } else {
                    addRowToTable(result);
                }
            });

        } catch (error) {
            alert(`Ocorreu um erro inesperado: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // Evento do botão "Analisar IPs"
    analyzeBtn.addEventListener('click', async () => {
        const ips = ipInput.value.trim().split('\n').filter(ip => ip);
        if (ips.length === 0) {
            alert('Por favor, insira pelo menos um endereço de IP para analisar.');
            return;
        }

        resultsBody.innerHTML = '';
        showLoading(true);

        try {
            const analyzeResponse = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': API_SECRET_KEY // <-- AUTENTICAÇÃO
                },
                body: JSON.stringify({ ips: ips })
            });
            const analyzeData = await analyzeResponse.json();

            if (!analyzeResponse.ok) {
                throw new Error(analyzeData.error || 'Erro desconhecido na análise');
            }

            const detailPromises = analyzeData.analysis_summary.map(summary => {
                return fetch(`${API_BASE_URL}/query/${summary.ip}`, {
                    headers: { 'X-API-Key': API_SECRET_KEY } // <-- AUTENTICAÇÃO
                }).then(res => res.json());
            });

            const detailedReports = await Promise.all(detailPromises);

            detailedReports.forEach((report, index) => {
                const status = analyzeData.analysis_summary[index].status;
                addRowToTable(report, status);
            });

        } catch (error) {
            alert(`Erro no processo de análise: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

}); // Fim do document.addEventListener
