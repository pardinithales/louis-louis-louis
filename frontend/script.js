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
    const userTypeSelection = document.getElementById('user-type-selection');
    const userTypeSelect = document.getElementById('user-type-select');
    const userTypeError = document.getElementById('user-type-error');
    const submitUserTypeBtn = document.getElementById('submit-user-type-btn');
    const susQuestionnaire = document.getElementById('sus-questionnaire');
    const susForm = document.getElementById('sus-form');
    const submitSusBtn = document.getElementById('submit-sus-btn');
    const susError = document.getElementById('sus-error');
    const susSuccess = document.getElementById('sus-success');
    
    // Admin
    const adminAccessBtn = document.getElementById('admin-access-btn');
    const adminPanel = document.getElementById('admin-panel');
    const viewAnswersBtn = document.getElementById('view-answers-btn');
    const deleteAnswersBtn = document.getElementById('delete-answers-btn');
    const downloadCsvBtn = document.getElementById('download-csv-btn');
    const viewSusBtn = document.getElementById('view-sus-btn');

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
        console.log('DEBUG: Verificando userIdentifier:', userIdentifier);
        
        if (userIdentifier) {
            console.log('DEBUG: userIdentifier existe, escondendo modal de consentimento');
            consentModal.style.display = 'none';
            validationCasesContainer.style.display = 'block';

            const userType = localStorage.getItem('userType');
            console.log('DEBUG: Verificando userType:', userType);
            
            if (!userType) {
                console.log('DEBUG: userType não existe, mostrando seleção de userType');
                console.log('DEBUG: userTypeSelection element:', userTypeSelection);
                userTypeSelection.style.display = 'block';
                validationCaseList.style.display = 'none';
                susQuestionnaire.style.display = 'none';
                console.log('DEBUG: Configurou displays - userTypeSelection: block, validationCaseList: none, susQuestionnaire: none');
            } else {
                console.log('DEBUG: userType já existe:', userType, '- pulando para casos');
                userTypeSelection.style.display = 'none';
                setupValidationUIForGroup(sessionStorage.getItem('userGroup'));
                loadValidationCases();
                checkAllCasesSubmitted(); // Checa se SUS deve ser mostrado
            }
        } else {
            console.log('DEBUG: userIdentifier não existe, mostrando modal de consentimento');
            consentModal.style.display = 'flex';
            validationCasesContainer.style.display = 'none';
        }
    }

    function setupValidationUIForGroup(group) {
        console.log('DEBUG: setupValidationUIForGroup chamada com grupo:', group);
        
        // Lê o grupo da sessão ATUAL. Se não existir, randomiza e salva.
        let userGroup = sessionStorage.getItem('userGroup');
        if (!userGroup) {
            userGroup = Math.random() < 0.5 ? 'louis_group' : 'control_group';
            sessionStorage.setItem('userGroup', userGroup);
            console.log('DEBUG: Novo grupo de sessão sorteado:', userGroup);
        }
        console.log('DEBUG: Grupo final sendo usado:', userGroup);
        
        const inferenceTab = document.getElementById('inference-tab');
        if (userGroup === 'control_group') {
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

    // Listener para submeter tipo de usuário
    submitUserTypeBtn.addEventListener('click', () => {
        const selectedType = userTypeSelect.value;
        console.log('DEBUG: Tipo de usuário selecionado:', selectedType);
        
        if (selectedType) {
            localStorage.setItem('userType', selectedType);
            console.log('DEBUG: userType salvo no localStorage:', selectedType);
            userTypeError.style.display = 'none';
            userTypeSelection.style.display = 'none';
            setupValidationUIForGroup(sessionStorage.getItem('userGroup'));
            loadValidationCases();
        } else {
            console.log('DEBUG: Nenhum tipo selecionado, mostrando erro');
            userTypeError.style.display = 'block';
        }
    });

    // Função para checar se todos os casos foram submetidos
    function checkAllCasesSubmitted() {
        const saveButtons = document.querySelectorAll('.validation-case-item button');
        const allSubmitted = Array.from(saveButtons).every(btn => btn.textContent === 'Salvo!');
        console.log('DEBUG: checkAllCasesSubmitted - botões encontrados:', saveButtons.length);
        console.log('DEBUG: checkAllCasesSubmitted - todos submetidos:', allSubmitted);
        
        if (allSubmitted && saveButtons.length > 0) {
            console.log('DEBUG: Todos os casos foram submetidos, mostrando SUS');
            susQuestionnaire.style.display = 'block';
        } else {
            console.log('DEBUG: Nem todos os casos foram submetidos, escondendo SUS');
            susQuestionnaire.style.display = 'none';
        }
    }

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

    viewSusBtn.addEventListener('click', async () => {
        console.log('DEBUG: Botão Ver Respostas SUS clicado');
        try {
            const response = await fetch(`${API_BASE_URL}/sus_responses/`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Falha ao buscar as respostas SUS.');
            }
            const susResponses = await response.json();
            console.log('DEBUG: Respostas SUS recebidas:', susResponses);
            displaySUSResponses(susResponses);
        } catch (error) {
            console.error('DEBUG: Erro ao buscar respostas SUS:', error);
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

    function displaySUSResponses(susResponses) {
        console.log('DEBUG: Exibindo respostas SUS:', susResponses.length);
        
        if (susResponses.length === 0) {
            alert('Nenhuma resposta SUS foi encontrada no banco de dados.');
            return;
        }

        // Cria o conteúdo do modal
        let modalContentHtml = '<h1>Respostas SUS Armazenadas</h1>';
        modalContentHtml += '<p>Total de respostas: ' + susResponses.length + '</p>';
        
        susResponses.forEach(response => {
            modalContentHtml += `<div class="user-answers">`;
            modalContentHtml += `<h4>Usuário (CPF final): ${response.user_identifier}</h4>`;
            modalContentHtml += `<p><strong>Data:</strong> ${new Date(response.created_at).toLocaleString('pt-BR')}</p>`;
            modalContentHtml += `<div class="answer-item">`;
            for (let i = 1; i <= 10; i++) {
                modalContentHtml += `<p><strong>Q${i}:</strong> ${response[`q${i}`]}</p>`;
            }
            // Calcular pontuação SUS
            const susScore = calculateSUSScore(response);
            modalContentHtml += `<p><strong>Pontuação SUS:</strong> ${susScore}/100</p>`;
            modalContentHtml += `</div></div>`;
        });

        // Cria e exibe o modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'view-sus-modal';
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

    function calculateSUSScore(response) {
        let score = 0;
        // Questões ímpares (1,3,5,7,9): contribuição = resposta - 1
        for (let i of [1, 3, 5, 7, 9]) {
            score += response[`q${i}`] - 1;
        }
        // Questões pares (2,4,6,8,10): contribuição = 5 - resposta
        for (let i of [2, 4, 6, 8, 10]) {
            score += 5 - response[`q${i}`];
        }
        // Multiplicar por 2.5 para obter o score de 0-100
        return score * 2.5;
    }

    // --- Carregar Casos de Validação ---
    async function loadValidationCases() {
        console.log('DEBUG: loadValidationCases chamada');
        console.log('DEBUG: validationCaseList.childElementCount:', validationCaseList.childElementCount);
        
        if (validationCaseList.childElementCount > 0) {
            console.log('DEBUG: Casos já carregados, verificando se todos foram submetidos');
            checkAllCasesSubmitted(); // Verifica o status mesmo se já carregado
            return; // Não recarregar se já estiver populado
        }

        const userIdentifier = localStorage.getItem('userIdentifier');
        console.log('DEBUG: userIdentifier para carregar casos:', userIdentifier);
        
        if (!userIdentifier) {
            console.error('Identificador do usuário não encontrado para carregar os casos.');
            validationCaseList.innerHTML = '<p>Erro: Identificador de usuário não encontrado. Por favor, complete o passo de consentimento.</p>';
            return;
        }

        try {
            console.log('DEBUG: Fazendo requisição para:', `${API_BASE_URL}/validation_cases/?user_identifier=${userIdentifier}`);
            
            // Adiciona o user_identifier como um parâmetro de query
            const response = await fetch(`${API_BASE_URL}/validation_cases/?user_identifier=${userIdentifier}`);
            console.log('DEBUG: Response status:', response.status);
            console.log('DEBUG: Response ok:', response.ok);
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const cases = await response.json();
            console.log('DEBUG: Casos recebidos:', cases.length, cases);

            // Buscar submissões já realizadas pelo usuário
            let userSubmissions = [];
            try {
                const submissionsResponse = await fetch(`${API_BASE_URL}/validation_submissions/`);
                if (submissionsResponse.ok) {
                    const allSubmissions = await submissionsResponse.json();
                    // Filtrar apenas as submissões do usuário atual
                    userSubmissions = allSubmissions.filter(sub => sub.user_identifier === userIdentifier);
                    console.log('DEBUG: Submissões do usuário encontradas:', userSubmissions.length);
                }
            } catch (error) {
                console.error('Erro ao buscar submissões:', error);
            }

            // Criar um mapa de casos já respondidos
            const answeredCases = {};
            userSubmissions.forEach(sub => {
                answeredCases[sub.case_id] = sub.answer;
            });

            validationCaseList.innerHTML = '';
            validationCaseList.style.display = 'block'; // Garante que está visível
            console.log('DEBUG: Limpou validationCaseList e definiu display como block');
            
            cases.forEach((caseItem, index) => {
                console.log(`DEBUG: Processando caso ${index + 1}:`, caseItem.case_id);
                const isAnswered = answeredCases.hasOwnProperty(caseItem.case_id);
                const previousAnswer = answeredCases[caseItem.case_id] || '';
                
                const item = document.createElement('div');
                item.className = 'validation-case-item';
                item.innerHTML = `
                    <h3>${caseItem.case_id}</h3>
                    <p>${caseItem.clinical_history}</p>
                    <div class="validation-answer-area">
                        <textarea id="answer-${caseItem.case_id}" placeholder="Exemplo de resposta estruturada:&#10;&#10;Hipótese diagnóstica: Síndrome de Wallenberg&#10;Artéria afetada: Artéria cerebelar póstero-inferior (PICA)&#10;Localização anatômica: Bulbo lateral&#10;&#10;Descreva sua análise de forma clara e organizada." ${isAnswered ? 'disabled' : ''}>${previousAnswer}</textarea>
                        <button class="button-primary" data-case-id="${caseItem.case_id}" ${isAnswered ? 'style="background-color: #28a745;"' : ''}>${isAnswered ? 'Salvo!' : 'Salvar Resposta'}</button>
                        <p class="submission-feedback" style="${isAnswered ? 'display: block;' : 'display: none;'}">${isAnswered ? `Resposta para "${caseItem.case_id}" salva com sucesso: "${previousAnswer}"` : ''}</p>
                    </div>
                `;
                validationCaseList.appendChild(item);
            });
            console.log('DEBUG: Todos os casos foram adicionados ao DOM');
            
        } catch (error) {
            console.error('Falha ao carregar os casos de validação:', error);
            validationCaseList.innerHTML = '<p>Erro ao carregar casos. Tente recarregar a página.</p>';
        }
        // Após popular validationCaseList
        checkAllCasesSubmitted();
        console.log('DEBUG: loadValidationCases concluída');
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
                        answer: answer,
                        user_type: localStorage.getItem('userType')
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

                // Checa se todos os casos foram submetidos para mostrar o SUS
                checkAllCasesSubmitted();

            } catch (error) {
                console.error('Erro ao salvar resposta:', error);
                alert(`Erro: ${error.message}`);
                button.disabled = false;
                button.textContent = 'Salvar Resposta';
            }
        }
    });

    // Listener para submeter SUS
    submitSusBtn.addEventListener('click', async () => {
        console.log('DEBUG: Botão SUS clicado');
        const formData = new FormData(susForm);
        const responses = {};
        let complete = true;
        
        // Debug: verificar cada resposta
        for (let i = 1; i <= 10; i++) {
            const q = formData.get(`q${i}`);
            console.log(`DEBUG: q${i} = ${q}`);
            if (!q) {
                complete = false;
                console.log(`DEBUG: Questão q${i} não respondida`);
                break;
            }
            responses[`q${i}`] = parseInt(q);
        }

        console.log('DEBUG: Formulário completo?', complete);
        console.log('DEBUG: Respostas coletadas:', responses);

        if (!complete) {
            susError.style.display = 'block';
            console.log('DEBUG: Mostrando erro de formulário incompleto');
            return;
        }

        const userIdentifier = localStorage.getItem('userIdentifier');
        console.log('DEBUG: userIdentifier para SUS:', userIdentifier);

        submitSusBtn.disabled = true;
        submitSusBtn.textContent = 'Enviando...';

        const requestData = {
            user_identifier: userIdentifier,
            ...responses
        };
        console.log('DEBUG: Dados a serem enviados:', requestData);

        try {
            const url = `${API_BASE_URL}/submit_sus/`;
            console.log('DEBUG: Enviando para:', url);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            console.log('DEBUG: Response status:', response.status);
            console.log('DEBUG: Response ok:', response.ok);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('DEBUG: Erro na resposta:', errorData);
                throw new Error(errorData.detail || 'Falha ao enviar respostas SUS.');
            }

            const successData = await response.json();
            console.log('DEBUG: Resposta de sucesso:', successData);

            susError.style.display = 'none';
            susSuccess.style.display = 'block';
            console.log('DEBUG: SUS enviado com sucesso!');
            
            // Desabilitar o formulário após submissão bem-sucedida
            susForm.querySelectorAll('input').forEach(input => input.disabled = true);
            submitSusBtn.disabled = true;

        } catch (error) {
            console.error('DEBUG: Erro ao enviar SUS:', error);
            alert(`Erro: ${error.message}`);
            submitSusBtn.disabled = false;
            submitSusBtn.textContent = 'Enviar Respostas SUS';
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