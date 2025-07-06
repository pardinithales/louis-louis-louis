import os
import json
import logging
import random # Importa o módulo random
import google.generativeai as genai
from ..core.config import GEMINI_API_KEY, CHAPTERS_DIR, IMAGES_DIR

# Configura o cliente do Gemini
genai.configure(api_key=GEMINI_API_KEY)

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
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    From the following clinical description, which may be in any language, please identify all key neurological signs and symptoms.
    Focus on the core clinical findings and ignore laterality (e.g., 'right', 'left', 'direita', 'esquerda').
    Provide the **English translation** for these findings.
    Return them as a comma-separated list. Be comprehensive.
    Description: "{query}"
    English Keywords:
    """
    response = await model.generate_content_async(prompt)
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


async def get_syndrome_inference(query: str, context_snippets: str, image_list: list) -> dict:
    """Usa o Gemini para inferir síndromes com base nos trechos e na lista de imagens."""
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json", "temperature": 0.2}
    )
    image_list_str = "\n".join(image_list)
    prompt = f"""
    Act as a neurology expert. Analyze the clinical presentation: "{query}".

    Base your analysis ONLY on the following snippets extracted from neurological literature:
    Context Snippets: --- {context_snippets} ---

    From the list of available images, select the most relevant one for each identified syndrome.
    Available Image Files: --- {image_list_str} ---

    Your main goal is to identify the most likely neurological syndromes.
    Populate two distinct lists:
    1.  `ischemic_syndromes`: A list of up to **four (4)** of the most probable clinically distinct ISCHEMIC syndromes. If you are very confident in one, you can provide fewer.
    2.  `hemorrhagic_syndromes`: A list of up to **two (2)** of the most probable HEMORRHAGIC syndromes.

    For each syndrome in both lists:
    - Provide a concise justification (`reasoning`) based ONLY on the provided context snippets.
    - Select **exactly one** illustrative image filename from the provided list. The filename must be an EXACT match.
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
    response = await model.generate_content_async(prompt)
    try:
        # Tenta carregar o JSON e retorna o dicionário que será validado pelo Pydantic
        return json.loads(response.text)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from Gemini response: {response.text}")
        # Retorna uma resposta válida e vazia para o frontend não quebrar
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

    if snippet_count == 0:
        # Lidar com o caso em que nenhum trecho é encontrado
        return {"ischemic_syndromes": [], "hemorrhagic_syndromes": []}
    
    logging.info("Step 3: Listing available images.")
    available_images = list_available_files(IMAGES_DIR, '.png')
    logging.info(f"Found {len(available_images)} images.")

    logging.info("Step 4: Starting final, diverse syndrome inference based on snippets...")
    inference_result = await get_syndrome_inference(query, context_snippets, available_images)
    logging.info("Final inference complete.")
    
    return inference_result 