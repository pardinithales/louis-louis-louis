import sys
import os

# Método mais robusto para adicionar o diretório raiz ao path
# Isso garante que o script encontre os módulos do 'backend'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.database import SessionLocal, engine
from backend.database import models, crud

# Dados dos casos clínicos (permanece o mesmo)
VALIDATION_CASES = {
    "CASO CLÍNICO 1": "Um homem de 72 anos, hipertenso, é levado ao pronto-socorro após um colapso súbito. Ao exame, ele está em coma, com pupilas puntiformes (1 mm) mas reativas à luz. Apresenta quadriparesia flácida e, ao estímulo doloroso, exibe posturas de descerebração. Os reflexos oculocefálicos estão ausentes para movimentos horizontais, mas há um movimento vertical mínimo dos olhos.",
    "CASO CLÍNICO 2": "Uma mulher de 55 anos, diabética, desenvolve agudamente vertigem, zumbido e surdez completa no ouvido esquerdo. O exame revela nistagmo horizontal, ataxia da marcha, paralisia de toda a hemiface esquerda (incluindo a testa) e perda da sensibilidade à dor e temperatura na hemiface esquerda. A força e a sensibilidade nos membros estão preservadas.",
    "CASO CLÍNICO 3": "Um homem de 68 anos, com fibrilação atrial, apresenta um quadro súbito de sonolência profunda e queixa-se de ver 'pessoas e animais coloridos e bem formados' no quarto, sem se sentir ameaçado. Ao exame, ele está sonolento, mas desperta com estímulos verbais. Apresenta paralisia completa do olhar vertical (para cima e para baixo), mas os movimentos horizontais estão intactos. As pupilas estão em posição média e reagem lentamente à luz. Não há déficits motores significativos nos membros.",
    "CASO CLÍNICO 4": "Um homem de 77 anos, destro, contador aposentado, é avaliado por um quadro agudo de dificuldade para realizar tarefas do dia a dia. Ele não consegue mais assinar o nome ou escrever um bilhete (agrafia), comete erros grosseiros em cálculos simples (acalculia), não consegue identificar os próprios dedos quando solicitado (agnosia digital) e confunde sua direita com a esquerda. A fluência da fala e a compreensão estão preservadas.",
    "CASO CLÍNICO 5": "Uma mulher de 72 anos, com histórico de estenose carotídea direita, apresenta início agudo de fraqueza na perna esquerda. Ao exame, ela está apática, com pouca iniciativa para falar (abulia) e demonstra um reflexo de preensão palmar à esquerda. A força no membro inferior esquerdo está grau 2/5, enquanto no membro superior esquerdo e face está 5/5. Ela também apresenta incontinência urinária desde o início do quadro.",
    "CASO CLÍNICO 6": "Um homem de 48 anos, destro, guitarrista profissional, acorda com uma fraqueza súbita e isolada na mão esquerda, com dificuldade para estender os dedos e o punho. Ele nega dor, dormência ou fraqueza em qualquer outra parte do corpo. O exame neurológico é inteiramente normal, exceto por uma paralisia dos extensores dos dedos e do punho esquerdos, mimetizando uma neuropatia radial.",
    "CASO CLÍNICO 7": "Um homem de 70 anos, destro e letrado, sofre um AVC. Após o evento, ele consegue escrever frases de forma coerente, mas é completamente incapaz de ler o que acabou de escrever ou qualquer outro texto. A nomeação de objetos e a fala estão normais. O exame de campo visual revela uma hemianopsia homônima direita completa.",
    "CASO CLÍNICO 8": "Um homem de 22 anos, sem comorbidades, sofreu um acidente de moto com movimento de chicote cervical há dois dias. Hoje, ele desenvolveu dor na região cervical e facial direita, seguida por uma sensação de 'pálpebra caída' e a pupila do olho direito menor que a esquerda. Não há outros déficits neurológicos.",
    "CASO CLÍNICO 9": "Uma mulher de 60 anos apresenta início agudo de paralisia do olho direito, com ptose e desvio 'para baixo e para fora'. Associado a isso, ela exibe um tremor grosseiro, de repouso e intenção, no braço e perna esquerdos. A força muscular no lado esquerdo está relativamente preservada.",
    "CASO CLÍNICO 10": "Um homem de 80 anos, com histórico de múltiplos AVCs, é trazido pela família por apresentar um comportamento estranho com a mão esquerda. Ele refere que a mão 'tem vida própria', desabotoando a camisa que ele acabou de abotoar com a mão direita e, por vezes, agindo de forma contrária à sua vontade (conflito intermanual). O exame revela apraxia ideomotora e tátil na mão esquerda, com força e sensibilidade normais. A mão direita funciona normalmente.",
    "CASO CLÍNICO 11": "Um homem de 67 anos, com hipertensão de longa data, apresenta início súbito de fraqueza no lado direito do corpo, poupando a face. Ao exame, há hemiparesia direita (braço e perna), perda da sensibilidade vibratória e proprioceptiva no hemicorpo direito, e a língua, quando protruída, desvia para o lado esquerdo.",
    "CASO CLÍNICO 12": "Um paciente de 65 anos, submetido a uma cirurgia de revascularização miocárdica com hipotensão prolongada, acorda com fraqueza nos dois braços, sendo incapaz de levantá-los contra a gravidade. A força nas pernas e na face está preservada. Ele é capaz de mover os dedos e as mãos, mas não os ombros.",
    "CASO CLÍNICO 13": "Um homem de 81 anos, com demência vascular, apresenta um quadro de anartria (incapacidade de articular palavras), disfagia severa e paralisia da porção inferior da face bilateralmente. Curiosamente, ele consegue sorrir e bocejar espontaneamente, mas não consegue mostrar os dentes ou sorrir sob comando (dissociação automático-voluntária).",
    "CASO CLÍNICO 14": "Uma mulher de 82 anos é trazida por quadro de confusão e desorientação espacial. Ela está claramente com a visão prejudicada, esbarrando em móveis, mas insiste que enxerga perfeitamente, chegando a descrever (de forma incorreta) as cores da roupa do examinador. O exame de reflexos pupilares e a fundoscopia são normais.",
    "CASO CLÍNICO 15": "Um homem de 68 anos, hipertenso, apresenta diplopia horizontal. Ao exame do olhar para a esquerda, o olho direito aduz até a linha média e apresenta nistagmo, enquanto o olho esquerdo não consegue se mover para além da linha média (paralisia do olhar para a esquerda). Ao tentar olhar para a direita, ambos os olhos se movem normalmente. A convergência está preservada.",
    "CASO CLÍNICO 16": "Um homem de 79 anos, com histórico de hipertensão, apresenta um quadro súbito de dor intensa, em queimação, no hemicorpo direito. O episódio inicial de AVC ocorreu há 6 meses, deixando-o com uma leve hemi-hipoestesia direita, que agora se transformou nesta dor excruciante, exacerbada por qualquer toque leve (alodinia).",
    "CASO CLÍNICO 17": "Uma mulher de 65 anos, com fibrilação atrial, apresenta um quadro súbito de hemiparesia, hemi-hipoestesia e hemianopsia homônima à direita. O déficit motor é proporcional em face, braço e perna.",
    "CASO CLÍNICO 18": "Um homem de 70 anos, destro, é admitido por um quadro súbito de confusão. Ao exame, ele está alerta. A fala é fluente e gramaticalmente correta, e a compreensão parece normal. No entanto, ele é incapaz de repetir frases simples como 'nem aqui, nem ali, nem lá'. A nomeação de objetos está relativamente preservada, com algumas parafasias fonêmicas. Não há déficits motores.",
    "CASO CLÍNICO 19": "Um homem de 59 anos, com hipertensão severa, é levado ao hospital com cefaleia intensa, vômitos e sonolência progressiva. Ao exame, ele está obnubilado. Há uma hemiplegia e hemi-hipoestesia à direita. Os olhos estão desviados tonicamente para a esquerda.",
    "CASO CLÍNICO 20": "Um homem de 67 anos, após um episódio de hipotensão severa, acorda com uma síndrome neurológica peculiar: ele consegue ver objetos isolados, mas não consegue perceber uma cena visual como um todo (simultanagnosia). Ele tem grande dificuldade em alcançar objetos sob orientação visual (ataxia óptica) e não consegue mover os olhos voluntariamente para um alvo (apraxia oculomotora).",
    "CASO CLÍNICO 21": "Uma mulher de 30 anos, usuária de contraceptivos orais, apresenta cefaleia há uma semana, que piorou progressivamente. Nas últimas 24 horas, desenvolveu uma crise convulsiva focal no braço direito, seguida por hemiparesia direita. Ao exame, além da hemiparesia, há papiledema bilateral na fundoscopia.",
    "CASO CLÍNICO 22": "Uma mulher de 64 anos apresenta-se com paralisia do III nervo craniano à esquerda (ptose, midríase, olho desviado inferolateralmente) e ataxia proeminente no braço e perna direitos. A força muscular está preservada.",
    "CASO CLÍNICO 23": "Um homem de 73 anos apresenta um quadro de vertigem, náuseas e vômitos. O exame revela uma síndrome de Horner à direita, ataxia apendicular e de marcha à direita, e perda da sensibilidade termoalgésica na face direita. No entanto, ele também apresenta hemiplegia completa do lado direito (braço e perna). A sensibilidade no hemicorpo esquerdo está normal.",
    "CASO CLÍNICO 24": "Um homem de 45 anos, após um trauma torácico fechado, desenvolve um quadro agudo de fraqueza nas duas pernas e perda da sensibilidade à dor e temperatura abaixo do nível do umbigo. A sensibilidade vibratória e a propriocepção estão preservadas em todos os membros. Ele também apresenta retenção urinária.",
    "CASO CLÍNICO 25": "Uma mulher de 66 anos, com hipertensão, é admitida por sonolência e confusão. Ao exame, ela está desorientada. Apresenta paralisia do olhar vertical, especialmente para cima, e as pupilas não reagem à luz, mas contraem durante a convergência (dissociação luz-perto). Ao tentar olhar para cima, os olhos convergem e se retraem nas órbitas (nistagmo de convergência-retração).",
    "CASO CLÍNICO 26": "Um homem de 58 anos, com fibrilação atrial, apresenta um quadro súbito de dificuldade de fala. Ao exame, ele tem uma fala não fluente, com grande esforço. A compreensão está intacta. A repetição de frases também está intacta, o que é notável. Apresenta hemiparesia direita, predominante na face e braço.",
    "CASO CLÍNICO 27": "Uma mulher de 60 anos é trazida ao hospital por um quadro de coma de início súbito. O exame neurológico revela ausência de resposta motora nos quatro membros. Ela está entubada. No entanto, ela consegue piscar voluntariamente e mover os olhos verticalmente para responder a perguntas de 'sim' ou 'não'. Os movimentos oculares horizontais estão ausentes.",
    "CASO CLÍNICO 28": "Um homem de 71 anos, com angiopatia amiloide, apresenta episódios transitórios e estereotipados de formigamento e contrações no braço direito, durando 1-2 minutos, várias vezes ao dia. Ele permanece consciente durante os episódios.",
    "CASO CLÍNICO 29": "Um homem de 50 anos, com histórico de hipertensão, apresenta início súbito de fraqueza no rosto e braço direitos, sem envolvimento da perna. Não há alterações de sensibilidade, linguagem ou visão.",
    "CASO CLÍNICO 30": "Um paciente com um aneurisma gigante da artéria carótida interna no segmento cavernoso apresenta-se com dor facial e oftalmoplegia completa à direita. Ao exame, há paralisia dos nervos III, IV e VI, além de hipoestesia na distribuição do ramo oftálmico (V1) e maxilar (V2) do nervo trigêmeo. A pupila direita está em miose e a acuidade visual está preservada."
}

def init_db():
    # Cria as tabelas no banco de dados (se não existirem)
    print("Criando tabelas do banco de dados, se necessário...")
    models.Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas.")

def populate():
    db = SessionLocal()
    try:
        print("Verificando e populando o banco de dados com casos de validação...")
        for case_id, history in VALIDATION_CASES.items():
            db_case = crud.get_validation_case(db, case_id=case_id)
            if not db_case:
                crud.create_validation_case(db, case_id=case_id, clinical_history=history)
                print(f"Caso '{case_id}' criado.")
            else:
                print(f"Caso '{case_id}' já existe.")
        print("Banco de dados populado com sucesso.")
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando o script de população do banco de dados...")
    init_db()
    populate() 