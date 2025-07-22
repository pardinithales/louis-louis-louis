# Sistema LouIS - Resumo Técnico-Científico

## Louis Inference System: Inteligência Artificial Aplicada ao Diagnóstico Neurovascular

### Resumo Executivo

O LouIS é um sistema de inferência baseado em inteligência artificial desenvolvido para auxiliar no diagnóstico sindrômico e topográfico em neurologia vascular. Utilizando técnicas avançadas de processamento de linguagem natural (PLN) e recuperação de informação aumentada (RAG - Retrieval Augmented Generation), o sistema analisa descrições clínicas em texto livre e fornece hipóteses diagnósticas estruturadas.

### Arquitetura Técnica

#### 1. **Modelo Base**
- **LLM Principal**: Google Gemini 2.5 Flash
- **Configuração**: Temperature 0.2 para maior precisão
- **Formato de Resposta**: JSON estruturado

#### 2. **Pipeline de Processamento**

```
1. Extração de Palavras-chave
   └─> Identificação e tradução de termos clínicos
   
2. Busca Contextual (RAG)
   ├─> Busca por snippets em capítulos processados
   └─> Fallback para busca semântica completa
   
3. Inferência Especializada
   ├─> Síndromes Isquêmicas (até 4)
   ├─> Síndromes Hemorrágicas (até 2)
   └─> Matching com imagens anatômicas
```

#### 3. **Base de Conhecimento**
- **52 capítulos** de literatura neurovascular especializada
- Pré-processamento cuidadoso com estrutura Q&A
- Formato otimizado para recuperação contextual
- Imagens anatômicas correlacionadas

### Diferenciais Técnicos

#### 1. **Sistema Anti-Alucinação**
- Inferências baseadas APENAS em snippets recuperados
- Sem uso de conhecimento genérico do modelo
- Referências textuais explícitas para cada diagnóstico

#### 2. **Otimização de Hiperparâmetros**
- Temperature ajustada para precisão diagnóstica
- Limites de resposta calibrados (4 isquêmicas, 2 hemorrágicas)
- Threshold adaptativo para busca contextual vs. semântica

#### 3. **Busca Inteligente em Dois Níveis**
- **Nível 1**: Busca por palavras-chave com extração de parágrafos completos
- **Nível 2**: Busca semântica completa quando snippets < 3

### Validação Científica

#### Metodologia
- **Design**: Estudo de validação cruzada
- **Randomização**: Apresentação aleatória de casos
- **Grupos**: Estratificação por experiência profissional
- **Métricas**: Acurácia diagnóstica + Usabilidade (SUS)

#### Aspectos Éticos
- Aprovação CEP HC-FMRP/USP
- Anonimização via últimos 5 dígitos CPF
- Conformidade LGPD e Res. CNS 466/12

### Stack Tecnológico

#### Backend
- **Framework**: FastAPI (Python)
- **IA**: Google Generative AI SDK
- **BD**: SQLite com SQLAlchemy ORM
- **Containerização**: Docker

#### Frontend
- **Interface**: HTML5, CSS3, JavaScript vanilla
- **Design**: Responsivo e acessível
- **UX**: Otimizado para profissionais médicos

#### Infraestrutura
- **Hospedagem**: VPS Ubuntu
- **Proxy**: Traefik com SSL automático
- **Domínio**: https://louis.tpfbrain.com

### Inovações Implementadas

1. **RAG Especializado**: Sistema de recuperação otimizado para terminologia médica
2. **Fallback Inteligente**: Busca semântica completa para casos complexos
3. **Validação Contextual**: Cada inferência vinculada a evidência textual
4. **Interface Dual**: Modo inferência livre + Modo validação estruturada

### Perspectivas Futuras

- Expansão da base de conhecimento
- Fine-tuning de modelo específico
- Integração com sistemas hospitalares
- Análise de neuroimagem

---

**Contato Técnico**: Dr. Thales Pardini Fagundes - pardinithales@gmail.com 