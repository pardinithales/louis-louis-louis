document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('search-button');
    const queryTextarea = document.getElementById('clinical-query');
    const resultsContainer = document.getElementById('results-container');
    const loader = document.getElementById('loader');

    searchButton.addEventListener('click', async () => {
        const query = queryTextarea.value.trim();
        if (!query) {
            alert('Please enter the clinical findings.');
            return;
        }

        // Clear previous results and show loader
        resultsContainer.innerHTML = '';
        loader.classList.remove('hidden');

        try {
            // A URL agora aponta para o subdomínio da API em produção
            const apiUrl = `https://app-louis.tpfbrain.com/infer/`;
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            // Combina as síndromes isquêmicas e hemorrágicas em uma única lista para exibição
            const allSyndromes = [...data.ischemic_syndromes, ...data.hemorrhagic_syndromes];
            displayResults(allSyndromes);

        } catch (error) {
            console.error('Fetch error:', error);
            displayError(error.message);
        } finally {
            // Hide loader
            loader.classList.add('hidden');
        }
    });

    function displayResults(syndromes) {
        resultsContainer.innerHTML = ''; // Clear again in case of error display
        if (!syndromes || syndromes.length === 0) {
            resultsContainer.innerHTML = '<p>No relevant syndromes found for the provided clinical case.</p>';
            return;
        }

        syndromes.forEach((syndrome, index) => {
            const card = document.createElement('div');
            card.className = 'syndrome-card';

            // Adiciona uma classe especial para o quinto card (hemorrágico)
            if (index === 4) {
                card.classList.add('hemorrhagic-card');
            }

            let imageHtml = '';
            if (syndrome.suggested_image) {
                // A URL da imagem também aponta para o domínio da API
                const imageUrl = `https://app-louis.tpfbrain.com/images/${syndrome.suggested_image}`;
                imageHtml = `<img src="${imageUrl}" alt="${syndrome.name || 'Syndrome Image'}">`;
            }

            card.innerHTML = `
                <h3>${syndrome.name || 'N/A'}</h3>
                <p><strong>Artery Involved:</strong> ${syndrome.artery || 'Not specified'}</p>
                <p><strong>Anatomical Location:</strong> ${syndrome.location || 'Not specified'}</p>
                <p><strong>Reasoning:</strong> ${syndrome.reasoning || 'Not specified'}</p>
                ${imageHtml}
            `;
            resultsContainer.appendChild(card);
        });
    }

    function displayError(message) {
        resultsContainer.innerHTML = '';
        const errorCard = document.createElement('div');
        errorCard.className = 'syndrome-card';
        errorCard.style.backgroundColor = '#FCE8E6';
        errorCard.style.borderColor = '#F4C7C3';
        errorCard.innerHTML = `
            <h3>Error</h3>
            <p>An error occurred while analyzing the case. Please try again.</p>
            <p><strong>Details:</strong> ${message}</p>
        `;
        resultsContainer.appendChild(errorCard);
    }
}); 