import os
import json
import logging
import random # Importa o módulo random
from google import genai
from google.genai import types
from ..core.config import GEMINI_API_KEY, CHAPTERS_DIR, IMAGES_DIR

# ============================================================================
# MIGRAÇÃO PARA SDK NOVO - 05/Out/2025
# ============================================================================
# Configura o cliente do Gemini (SDK novo)
client = genai.Client(api_key=GEMINI_API_KEY)

# Configuração para thinking desabilitado (latência otimizada)
NO_THINKING_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    temperature=0.2,
    top_p=0.95,
    top_k=40,
)

# Configuração para JSON com thinking desabilitado
JSON_NO_THINKING_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    response_mime_type="application/json",
    temperature=0.2,
    top_p=0.95,
    top_k=40,
)

logging.info("✅ Gemini client initialized with SDK novo (thinking disabled for optimal latency)")

def list_available_files(directory: str, extension: str) -> list:
    """Lista todos os arquivos com uma determinada extensão em um diretório."""
    try:
        files = [f for f in os.listdir(directory) if f.endswith(extension)]
        if not files:
            raise FileNotFoundError(f"Nenhum arquivo '{extension}' encontrado em {directory}")
        return files
    except FileNotFoundError as e:
        logging.error(f"O diretório não foi encontrado: {directory}")
        raise e

async def extract_keywords(query: str) -> list[str]:
    """Usa a IA para extrair e traduzir para o inglês os termos clínicos chave da consulta."""
    # SDK NOVO: Nota - API é síncrona, mas podemos usar em contexto async
    prompt = f"""
    From the following clinical description, which may be in any language, please identify all key neurological signs and symptoms.
    Focus on the core clinical findings and ignore laterality (e.g., 'right', 'left', 'direita', 'esquerda').
    Provide the **English translation** for these findings.
    Return them as a comma-separated list. Be comprehensive.
    Description: "{query}"
    English Keywords:
    """
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=NO_THINKING_CONFIG
    )
    keywords = [k.strip() for k in response.text.split(',')]
    return [k for k in keywords if k] # Remove strings vazias

def search_chapters_for_snippets(keywords: list[str]) -> str:
    """
    Busca por palavras-chave em todos os capítulos e extrai os parágrafos
    inteiros que as contêm.
    """
    all_snippets = set()
    chapter_files = list_available_files(CHAPTERS_DIR, '_extracted.txt')

    for filename in chapter_files:
        try:
            with open(os.path.join(CHAPTERS_DIR, filename), 'r', encoding='utf-8') as f:
                # Lê o arquivo inteiro e divide em parágrafos (blocos separados por linhas vazias)
                paragraphs = f.read().split('\n\n')
            
            for paragraph in paragraphs:
                if not paragraph.strip():
                    continue # Pula parágrafos vazios
                
                for keyword in keywords:
                    if keyword.lower() in paragraph.lower():
                        snippet = (f"--- Snippet from {filename} ---\n" + paragraph.strip() + "\n")
                        all_snippets.add(snippet)
                        # Uma vez que um parágrafo é adicionado, não precisa ser verificado novamente
                        break
        except Exception as e:
            logging.warning(f"Could not process file {filename}: {e}")

    if not all_snippets:
        return "No relevant information found for the given keywords."

    # Não reduz mais o contexto para garantir que toda a informação relevante seja usada
    # snippet_list = list(all_snippets)
    # if len(snippet_list) > 5: 
    #     sample_size = int(len(snippet_list) * 0.8)
    #     sampled_snippets = random.sample(snippet_list, k=sample_size)
    #     logging.info(f"Reduced snippets from {len(snippet_list)} to {len(sampled_snippets)} for performance.")
    #     return "\n".join(sampled_snippets)

    return "\n".join(all_snippets)


def load_all_chapters_content() -> str:
    """
    Carrega todo o conteúdo de todos os capítulos em uma única string.
    Usado como fallback quando a busca por keywords não retorna resultados suficientes.
    """
    all_content = []
    chapter_files = list_available_files(CHAPTERS_DIR, '_extracted.txt')
    
    for filename in chapter_files:
        try:
            with open(os.path.join(CHAPTERS_DIR, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                # Adiciona header do capítulo para contexto
                all_content.append(f"\n\n=== CHAPTER: {filename} ===\n{content}")
        except Exception as e:
            logging.warning(f"Could not load file {filename}: {e}")
    
    return "\n".join(all_content)


async def get_syndrome_inference(query: str, context_snippets: str, image_list: list) -> dict:
    """Usa o Gemini para inferir síndromes com base nos trechos e na lista de imagens."""
    # SDK NOVO: usa client com JSON config e thinking desabilitado
    image_list_str = "\n".join(image_list)
    prompt = f"""
    Act as a neurology expert. Analyze the clinical presentation: "{query}".

    Base your analysis ONLY on the following snippets extracted from neurological literature:
    Context Snippets: --- {context_snippets} ---

    From the list of available images, select the most relevant one for each identified syndrome.
    Available Image Files: --- {image_list_str} ---

    Your main goal is to identify the most likely neurological syndromes.
    - The syndrome `name` must be a standard, common name (e.g., "Weber's Syndrome"), not a long description.
    - For `suggested_image`, you MUST perform a self-correction step: does the image filename truly and accurately represent the syndrome's pathology and location?
    - If no image is a clear match, you MUST return `null` for the `suggested_image` field. It is better to provide no image than an incorrect one.
    
    Populate two distinct lists:
    1.  `ischemic_syndromes`: A list of up to **four (4)** of the most probable clinically distinct ISCHEMIC syndromes. If you are very confident in one, you can provide fewer.
    2.  `hemorrhagic_syndromes`: A list of up to **two (2)** of the most probable HEMORRHAGIC syndromes.

    For each syndrome in both lists:
    - Provide a concise justification (`reasoning`) based ONLY on the provided context snippets.
    - Select **exactly one** illustrative image filename from the provided list or `null`. The filename must be an EXACT match.
    - **Do not use the same image filename for more than one syndrome.**

    If no relevant syndromes are found based on the context, return empty lists.

    Respond **in English**, with this strict JSON format:
    {{
      "ischemic_syndromes": [
        {{
          "name": "Ischemic Syndrome 1",
          "artery": "Artery involved",
          "location": "Anatomical location",
          "reasoning": "A concise justification for this specific ischemic syndrome.",
          "suggested_image": "exact_filename_from_list.png"
        }}
      ],
      "hemorrhagic_syndromes": [
        {{
          "name": "Hemorrhagic Syndrome 1",
          "artery": "Artery/Vessel involved",
          "location": "Anatomical location",
          "reasoning": "A concise justification for this specific hemorrhagic syndrome.",
          "suggested_image": "exact_filename_from_list.png"
        }}
      ]
    }}
    """
    # SDK NOVO: chamada síncrona (API não tem versão async)
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=JSON_NO_THINKING_CONFIG
    )
    try:
        # Tenta carregar o JSON e retorna o dicionário que será validado pelo Pydantic
        return json.loads(response.text)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from Gemini response: {response.text}")
        # Retorna uma resposta válida e vazia para o frontend não quebrar
        return {"ischemic_syndromes": [], "hemorrhagic_syndromes": []}


async def get_syndrome_inference_with_full_context(query: str, full_chapters_content: str, image_list: list) -> dict:
    """
    Usa o Gemini para inferir síndromes usando TODO o conteúdo dos capítulos.
    Usado quando a busca por keywords não retorna resultados suficientes.
    """
    # SDK NOVO: usa client com JSON config e thinking desabilitado
    image_list_str = "\n".join(image_list)
    prompt = f"""
    Act as a neurology expert. You have been given a clinical presentation that didn't match well with keyword searches.
    Your task is to perform a COMPREHENSIVE SEMANTIC SEARCH across ALL the neurological literature provided below.
    
    Clinical presentation to analyze: "{query}"

    IMPORTANT INSTRUCTIONS:
    1. Search for clinical patterns, synonyms, related symptoms, and indirect references throughout the ENTIRE content below
    2. Consider that the query might use different terminology than the literature
    3. Look for partial matches and related clinical findings
    4. The syndrome names, locations, and arteries MUST come from the literature provided, not from general knowledge
    
    === COMPLETE NEUROLOGICAL LITERATURE DATABASE ===
    {full_chapters_content}
    === END OF LITERATURE DATABASE ===

    Available Image Files: 
    {image_list_str}

    Your main goal is to identify the most likely neurological syndromes based on semantic matching with the literature.
    - The syndrome `name` must be a SHORT, STANDARD name (e.g., "MCA syndrome", "Broca's aphasia"), NOT a long description
    - For `suggested_image`, select the most relevant filename or `null`
    - Base your reasoning on specific passages from the literature
    
    Populate two distinct lists:
    1. `ischemic_syndromes`: Up to four (4) most probable ISCHEMIC syndromes
    2. `hemorrhagic_syndromes`: Up to two (2) most probable HEMORRHAGIC syndromes

    For each syndrome:
    - Name MUST be concise (max 3-4 words), standard neurological terminology
    - Artery and location MUST be extracted from the literature
    - Provide reasoning that references specific content from the chapters
    - Select one image or `null`

    If after comprehensive search no relevant syndromes match the presentation, return empty lists.

    Respond in this JSON format:
    {{
      "ischemic_syndromes": [
        {{
          "name": "Syndrome name from literature",
          "artery": "Artery from literature",
          "location": "Location from literature",
          "reasoning": "Justification referencing specific chapter content",
          "suggested_image": "filename.png or null"
        }}
      ],
      "hemorrhagic_syndromes": [
        {{
          "name": "Syndrome name from literature",
          "artery": "Artery from literature", 
          "location": "Location from literature",
          "reasoning": "Justification referencing specific chapter content",
          "suggested_image": "filename.png or null"
        }}
      ]
    }}
    """

    try:
        # SDK NOVO: chamada síncrona (API não tem versão async)
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=JSON_NO_THINKING_CONFIG
        )
        result_text = response.text
        
        # Tentativa de corrigir JSON com vírgula faltando
        if result_text.strip().endswith('],\n}') or result_text.strip().endswith('],\r\n}'):
            # Remove vírgula extra no final
            result_text = result_text.rstrip()
            if result_text.endswith(',\n}'):
                result_text = result_text[:-3] + '\n}'
            elif result_text.endswith(',\r\n}'):
                result_text = result_text[:-4] + '\r\n}'
        
        return json.loads(result_text)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON from Gemini response: {response.text}")
        logging.error(f"JSON Error details: {e}")
        
        # Tentativa de correção mais agressiva
        try:
            # Remove possíveis vírgulas extras antes de }
            fixed_text = result_text.replace(',\n}', '\n}').replace(',\r\n}', '\r\n}').replace(', }', ' }')
            return json.loads(fixed_text)
        except:
            return {"ischemic_syndromes": [], "hemorrhagic_syndromes": []}
    except Exception as e:
        logging.error(f"Error in full context inference: {e}")
        return {"ischemic_syndromes": [], "hemorrhagic_syndromes": []}


async def run_full_inference_process(query: str):
    """Orquestra o novo processo de inferência baseado em RAG."""
    logging.info("Step 1: Extracting keywords from query...")
    keywords = await extract_keywords(query)
    logging.info(f"Extracted keywords: {keywords}")

    logging.info("Step 2: Searching for paragraph snippets across all chapters...")
    context_snippets = search_chapters_for_snippets(keywords)
    snippet_count = len(context_snippets.split('--- Snippet from')) - 1
    logging.info(f"Found {snippet_count} relevant snippets.")
    
    # Log para visibilidade do contexto exato enviado para a IA
    if snippet_count > 0:
        logging.info(f"Context being sent to AI:\n{context_snippets}")

    # Listar imagens disponíveis (usado em ambos os caminhos)
    logging.info("Step 3: Listing available images.")
    available_images = list_available_files(IMAGES_DIR, '.png')
    logging.info(f"Found {len(available_images)} images.")

    # Decisão: usar busca específica ou busca semântica completa
    MIN_SNIPPETS_THRESHOLD = 3  # Threshold configurável
    
    if snippet_count >= MIN_SNIPPETS_THRESHOLD:
        # Caminho normal: snippets suficientes encontrados
        logging.info(f"Step 4: Using standard inference with {snippet_count} snippets...")
        inference_result = await get_syndrome_inference(query, context_snippets, available_images)
    else:
        # Fallback: poucos ou nenhum snippet encontrado
        logging.info(f"Step 4: Insufficient snippets ({snippet_count} < {MIN_SNIPPETS_THRESHOLD}). Loading full context for semantic search...")
        
        # Detectar se a query é complexa (mais de 30 palavras sugere descrição detalhada)
        query_word_count = len(query.split())
        if query_word_count > 30:
            logging.info(f"Complex query detected ({query_word_count} words). Full semantic search is recommended.")
        
        # Carregar todo o conteúdo dos capítulos
        full_content = load_all_chapters_content()
        content_size_kb = len(full_content.encode('utf-8')) / 1024
        logging.info(f"Loaded {content_size_kb:.1f}KB of chapter content for comprehensive search.")
        
        # Usar inferência com contexto completo
        inference_result = await get_syndrome_inference_with_full_context(query, full_content, available_images)
        logging.info("Full context semantic inference complete.")
    
    return inference_result 