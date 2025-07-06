document.addEventListener('DOMContentLoaded', () => {
    // --- Seletores de Elementos ---
    const clinicalCaseTextarea = document.getElementById('clinical-case');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('results-container');
    
    // Abas
    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const validationTab = document.getElementById('validation-tab');

    // Validação
    const consentModal = document.getElementById('validation-consent-modal');
    const validationCasesContainer = document.getElementById('validation-cases-container');
    const cpfInput = document.getElementById('cpf-input');
    const cpfError = document.getElementById('cpf-error');
    const consentAgreeBtn = document.getElementById('consent-agree-btn');
    const validationCaseList = document.getElementById('validation-case-list');
    const userGroupNotification = document.getElementById('user-group-notification');
    
    // Admin
    const adminAccessBtn = document.getElementById('admin-access-btn');
    const adminPanel = document.getElementById('admin-panel');
    const viewAnswersBtn = document.getElementById('view-answers-btn');
    const deleteAnswersBtn = document.getElementById('delete-answers-btn');
    const downloadCsvBtn = document.getElementById('download-csv-btn');

    // Detecta o ambiente para definir a URL base da API
    const getApiBaseUrl = () => {
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000'; // Ambiente de desenvolvimento local
        }
        // Aponta para o subdomínio da API em produção
        return 'https://app-louis.tpfbrain.com';
    };
    const API_BASE_URL = getApiBaseUrl();

    // As variáveis de sessão/usuário agora são lidas dentro das funções para garantir que estão sempre atualizadas.

    // --- Lógica das Abas ---
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetContent = document.getElementById(tab.id.replace('-tab', '-content'));
            if (targetContent) {
                targetContent.classList.add('active');
            }

            // Lógica específica da aba de validação
            if (tab.id === 'validation-tab') {
                handleValidationTabClick();
            }
        });
    });

    function handleValidationTabClick() {
        const userIdentifier = localStorage.getItem('userIdentifier');
        if (userIdentifier) {
            consentModal.style.display = 'none';
            // AQUI ESTÁ A CORREÇÃO:
            validationCasesContainer.style.display = 'block';

            // Lê o grupo da sessão ATUAL. Se não existir, randomiza e salva.
            let userGroup = sessionStorage.getItem('userGroup');
            if (!userGroup) {
                userGroup = Math.random() < 0.5 ? 'louis_group' : 'control_group';
                sessionStorage.setItem('userGroup', userGroup);
                console.log('Novo grupo de sessão sorteado:', userGroup); // LOG PARA DEBUG
            }
            
            setupValidationUIForGroup(userGroup);
            loadValidationCases();
        } else {
            consentModal.style.display = 'flex';
            validationCasesContainer.style.display = 'none';
        }
    }

    function setupValidationUIForGroup(group) {
        const inferenceTab = document.getElementById('inference-tab');
        if (group === 'control_group') {
            userGroupNotification.innerHTML = '<strong>Grupo Controle:</strong> Você foi selecionado para responder aos casos sem a ajuda da ferramenta de inferência. A aba "Inferência" está desativada.';
            inferenceTab.style.display = 'none'; // Esconde a aba
        } else {
            userGroupNotification.innerHTML = '<strong>Grupo Louis:</strong> Você pode usar a aba "Inferência" para consultar a IA antes de submeter suas respostas.';
            inferenceTab.style.display = 'block'; // Garante que a aba está visível
        }
        userGroupNotification.style.display = 'block';
    }

    consentAgreeBtn.addEventListener('click', async () => {
        const cpfValue = cpfInput.value.trim();
        if (cpfValue.length === 5 && /^\d{5}$/.test(cpfValue)) {
            cpfError.style.display = 'none';
            consentAgreeBtn.disabled = true;
            consentAgreeBtn.textContent = 'Gerando PDF...';

            try {
                // Etapa 1: Gerar e baixar o PDF de consentimento
                const response = await fetch(`${API_BASE_URL}/consent/generate/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    // Reutilizando a estrutura do AdminActionRequest, passando o CPF no campo 'password'
                    body: JSON.stringify({ password: cpfValue })
                });

                if (!response.ok) {
                    throw new Error('Falha ao gerar o PDF de consentimento.');
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `TCLE_Louis_${cpfValue}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                
                // Etapa 2: Continuar com a lógica original
                localStorage.setItem('userIdentifier', cpfValue);
                handleValidationTabClick();

            } catch (error) {
                alert(`Ocorreu um erro: ${error.message}`);
            } finally {
                consentAgreeBtn.disabled = false;
                consentAgreeBtn.textContent = 'Concordo em Participar';
            }
        } else {
            cpfError.style.display = 'block';
        }
    });

    // --- Lógica do Admin ---
    adminAccessBtn.addEventListener('click', () => {
        const password = prompt('Por favor, insira a senha de administrador:');
        if (password === 'admin') {
            adminPanel.style.display = 'block';
            adminAccessBtn.style.display = 'none';
        } else if (password) { // Se o usuário digitou algo, mas não é a senha correta
            alert('Senha incorreta.');
        }
    });

    downloadCsvBtn.addEventListener('click', async () => {
        const password = prompt('Para baixar o dataset, por favor, insira a senha de administrador:');
        if (password !== 'admin') {
            if (password) alert('Senha incorreta.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/admin/download_csv/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: 'admin' })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Falha ao gerar o dataset.');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'louis_validation_dataset.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            alert(`Erro: ${error.message}`);
        }
    });

    viewAnswersBtn.addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/validation_submissions/`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Falha ao buscar as respostas.');
            }
            const submissions = await response.json();
            displaySubmissions(submissions);
        } catch (error) {
            alert(`Erro: ${error.message}`);
        }
    });

    deleteAnswersBtn.addEventListener('click', async () => {
        const confirmation = confirm('ATENÇÃO: Isso apagará PERMANENTEMENTE todas as respostas de validação. Deseja continuar?');
        if (!confirmation) return;

        try {
            const response = await fetch(`${API_BASE_URL}/delete_validation_submissions/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: 'admin' })
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || 'Falha ao apagar as respostas.');
            }
            alert(result.message);

        } catch (error) {
            alert(`Erro: ${error.message}`);
        }
    });

    function displaySubmissions(submissions) {
        if (submissions.length === 0) {
            alert('Nenhuma resposta de validação foi encontrada no banco de dados.');
            return;
        }

        // Agrupa as respostas por usuário
        const submissionsByUser = submissions.reduce((acc, sub) => {
            if (!acc[sub.user_identifier]) {
                acc[sub.user_identifier] = [];
            }
            acc[sub.user_identifier].push(sub);
            return acc;
        }, {});

        // Cria o conteúdo do modal
        let modalContentHtml = '<h1>Respostas Armazenadas</h1>';
        for (const userId in submissionsByUser) {
            modalContentHtml += `<div class="user-answers"><h4>Usuário (CPF final): ${userId}</h4>`;
            submissionsByUser[userId].forEach(sub => {
                modalContentHtml += `<div class="answer-item"><strong>${sub.case_id}:</strong><p>${sub.answer}</p></div>`;
            });
            modalContentHtml += `</div>`;
        }

        // Cria e exibe o modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'view-answers-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-button" style="float: right; cursor: pointer; font-size: 1.5rem;">&times;</span>
                ${modalContentHtml}
            </div>
        `;
        document.body.appendChild(modal);

        modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay') || e.target.classList.contains('close-button')) {
                document.body.removeChild(modal);
            }
        });
    }

    // --- Carregar Casos de Validação ---
    async function loadValidationCases() {
        if (validationCaseList.childElementCount > 0) return; // Não recarregar se já estiver populado

        try {
            const response = await fetch(`${API_BASE_URL}/validation_cases/`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const cases = await response.json();

            validationCaseList.innerHTML = '';
            cases.forEach(caseItem => {
                const item = document.createElement('div');
                item.className = 'validation-case-item';
                item.innerHTML = `
                    <h3>${caseItem.case_id}</h3>
                    <p>${caseItem.clinical_history}</p>
                    <div class="validation-answer-area">
                        <textarea id="answer-${caseItem.case_id}" placeholder="Digite sua hipótese aqui..."></textarea>
                        <button class="button-primary" data-case-id="${caseItem.case_id}">Salvar Resposta</button>
                        <p class="submission-feedback" style="display: none;"></p>
                    </div>
                `;
                validationCaseList.appendChild(item);
            });
        } catch (error) {
            console.error('Falha ao carregar os casos de validação:', error);
            validationCaseList.innerHTML = '<p>Erro ao carregar casos. Tente recarregar a página.</p>';
        }
    }
    
    // --- Submeter Resposta de Validação ---
    validationCaseList.addEventListener('click', async (e) => {
        if (e.target.tagName === 'BUTTON' && e.target.dataset.caseId) {
            const userIdentifier = localStorage.getItem('userIdentifier');
            const userGroup = sessionStorage.getItem('userGroup'); // Garante que pegamos o valor mais atual
            const button = e.target;
            const caseId = button.dataset.caseId;
            const answerTextarea = document.getElementById(`answer-${caseId}`);
            const answer = answerTextarea.value.trim();
            const feedbackEl = button.nextElementSibling;

            if (!answer) {
                alert('Por favor, digite sua resposta antes de salvar.');
                return;
            }

            button.disabled = true;
            button.textContent = 'Salvando...';
            feedbackEl.style.display = 'none';

            try {
                const response = await fetch(`${API_BASE_URL}/submit_validation_answer/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_identifier: userIdentifier,
                        case_id: caseId,
                        user_group: userGroup,
                        answer: answer
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Falha ao salvar a resposta.');
                }
                
                button.textContent = 'Salvo!';
                button.style.backgroundColor = '#28a745';
                answerTextarea.disabled = true;
                
                // Feedback explícito para o usuário
                feedbackEl.textContent = `Resposta para "${caseId}" salva com sucesso: "${answer}"`;
                feedbackEl.style.display = 'block';

            } catch (error) {
                console.error('Erro ao salvar resposta:', error);
                alert(`Erro: ${error.message}`);
                button.disabled = false;
                button.textContent = 'Salvar Resposta';
            }
        }
    });


    // --- Lógica de Inferência ---
    submitBtn.addEventListener('click', async () => {
        const query = clinicalCaseTextarea.value.trim();

        if (!query) {
            alert('Por favor, insira um quadro clínico.');
            return;
        }

        loader.style.display = 'block';
        resultsContainer.innerHTML = ''; // Bug corrigido: resultsContainer agora existe.

        try {
            const response = await fetch(`${API_BASE_URL}/infer/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Erro na inferência:', error);
            if (resultsContainer) {
                resultsContainer.innerHTML = `<div class="error-message"><strong>Erro:</strong> ${error.message}</div>`;
            }
        } finally {
            loader.style.display = 'none';
        }
    });

    function displayResults(data) {
        if (!resultsContainer) return; // Checagem de segurança
        resultsContainer.innerHTML = '';
        const title = document.createElement('h2');
        title.textContent = 'Resultados da Análise';
        resultsContainer.appendChild(title);
        
        const grid = document.createElement('div');
        grid.className = 'results-grid';
    
        const ischemicSection = createSyndromeSection('Síndromes Isquêmicas Prováveis', data.ischemic_syndromes);
        const hemorrhagicSection = createSyndromeSection('Síndromes Hemorrágicas Prováveis', data.hemorrhagic_syndromes, 'hemorrhagic-section');
    
        if (data.ischemic_syndromes.length === 0 && data.hemorrhagic_syndromes.length === 0) {
            resultsContainer.innerHTML += '<p>Nenhuma síndrome relevante encontrada para o caso clínico fornecido.</p>';
        } else {
            grid.appendChild(ischemicSection);
            grid.appendChild(hemorrhagicSection);
            resultsContainer.appendChild(grid);
        }
    }
    
    function createSyndromeSection(title, syndromes, customClass = '') {
        const section = document.createElement('div');
        section.className = 'syndrome-section';
        if (customClass) {
            section.classList.add(customClass);
        }
    
        const sectionTitle = document.createElement('h3');
        sectionTitle.textContent = title;
        section.appendChild(sectionTitle);
    
        if (syndromes.length > 0) {
            syndromes.forEach(syndrome => {
                const card = document.createElement('div');
                card.className = 'result-card';
                card.innerHTML = `
                    <h4>${syndrome.name || 'Nome não disponível'}</h4>
                    <div class="card-content">
                        <div class="card-image">
                            <img src="${API_BASE_URL}/images/${syndrome.suggested_image}" alt="Imagem de ${syndrome.name}" onerror="this.src='assets/louis-logo.png'; this.alt='Imagem padrão';">
                        </div>
                        <div class="card-details">
                            <p><strong>Artéria:</strong> ${syndrome.artery || 'Não especificada'}</p>
                            <p><strong>Localização Anatômica:</strong> ${syndrome.location || 'Não especificada'}</p>
                            <p><strong>Justificativa:</strong> ${syndrome.reasoning || 'Não fornecida'}</p>
                        </div>
                    </div>
                `;
                section.appendChild(card);
            });
        } else {
            const noResultMessage = document.createElement('p');
            noResultMessage.textContent = 'Nenhuma síndrome correspondente encontrada nesta categoria.';
            section.appendChild(noResultMessage);
        }
        return section;
    }
}); 