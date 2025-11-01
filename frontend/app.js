// app.js - VERSÃO FINAL E CORRIGIDA
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Seleção dos Elementos do HTML ---
    const queryBtn = document.getElementById('query-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const ipInput = document.getElementById('ip-input');
    const resultsBody = document.getElementById('results-body');
    const loadingSpinner = document.getElementById('loading-spinner');

    const API_BASE_URL = 'http://127.0.0.1:5000';

    // --- 2. Funções Auxiliares ---

    // Função para mostrar/esconder o spinner de carregamento
    const showLoading = (isLoading ) => {
        loadingSpinner.classList.toggle('hidden', !isLoading);
    };

    // Função para adicionar uma linha de resultado na tabela
    const addRowToTable = (data, status = 'Consultado') => {
        const row = document.createElement('tr');
        
        let statusClass = '';
        if (status.includes('cached')) statusClass = 'status-cached';
        if (status.includes('analyzed')) statusClass = 'status-analyzed';
        if (status.includes('error')) statusClass = 'status-error';

        // Função auxiliar para verificar se um valor existe (incluindo 0)
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
	// NOVA VERSÃO APRIMORADA do Evento do botão "Consultar do Banco"
queryBtn.addEventListener('click', async () => {
    const ips = ipInput.value.trim().split('\n').filter(ip => ip); // Pega TODOS os IPs
    if (ips.length === 0) {
        alert('Por favor, insira pelo menos um endereço de IP para consultar.');
        return;
    }

    resultsBody.innerHTML = ''; // Limpa a tabela
    showLoading(true);

    try {
        // Prepara uma lista de "promessas" para buscar cada IP no banco
        const queryPromises = ips.map(ip => {
            return fetch(`${API_BASE_URL}/query/${ip}`)
                .then(response => {
                    if (!response.ok) {
                        // Se a API retornar um erro (ex: 404 Not Found),
                        // criamos um objeto de erro para exibir na tabela.
                        return response.json().then(err => ({ ip: ip, error: err.error }));
                    }
                    return response.json();
                })
                .catch(networkError => {
                    // Se houver um erro de rede, também criamos um objeto de erro.
                    return { ip: ip, error: networkError.message };
                });
        });

        // Executa todas as consultas em paralelo e espera por todas
        const results = await Promise.all(queryPromises);

        // Agora que temos todos os resultados, preenchemos a tabela
        results.forEach(result => {
            if (result.error) {
                addRowToTable({ ip: result.ip }, `Erro: ${result.error}`);
            } else {
                addRowToTable(result); // O status padrão 'Consultado' será usado
            }
        });

    } catch (error) {
        // Este catch é para erros inesperados no Promise.all
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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ips: ips })
            });
            const analyzeData = await analyzeResponse.json();

            if (!analyzeResponse.ok) {
                throw new Error(analyzeData.error || 'Erro desconhecido na análise');
            }

            const detailPromises = analyzeData.analysis_summary.map(summary => {
                return fetch(`${API_BASE_URL}/query/${summary.ip}`).then(res => res.json());
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
