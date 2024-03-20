import time
import json
from ia_generate import send_message
#FORMATAR DESCRIÇÃO
def formatar_descricao(descricao):
    prompt_final = 'Compromisso com Você' \
                   'Sua satisfação é nossa prioridade! Oferecemos produtos de qualidade, compra 100% segura e um atendimento ao cliente excepcional. Conte com suporte completo antes e após a compra. Qualquer dúvida, estamos aqui para ajudar.' \
                   'Qualidade Garantida | Suporte Total'

    prompt = 'Nenhuma das descriçãoes são explicitas, descrição de produtos!' \
             'Seja Objetivo: Comece com informações claras e diretas. Evite longos textos. Detalhes técnicos devem vir por último, para quem busca especificidades.' \
             'Seja Claro: Descreva o produto de forma clara. Responda:' \
             'Para que serve?' \
             'O que faz?' \
             'Como se usa?' \
             'Quais as principais características?' \
             'Características Detalhadas: Liste e explique as principais características do produto. Isso evita dúvidas e reduz perguntas, agilizando vendas.' \
             'Exemplos de Uso: Demonstre como o produto pode ser utilizado, destacando benefícios práticos e cotidianos.' \
             'Conexão Emocional: Utilize exemplos que despertem emoções, mostrando como o produto pode melhorar a vida do cliente.' \
             'Formatação Clara: Organize as informações começando pelo mais importante. Inclua funcionalidades, exemplos de uso e características técnicas em ordem de relevância. Finalize esclarecendo dúvidas sobre compra e frete.' \
             'Sem Exageros: Descreva o produto sinceramente, evitando superlativos que gerem desconfiança.' \
             f'O texto da descrição é este: {descricao}' \
             f'Ao final dele adicione este texto: {prompt_final}'

    time.sleep(3)
    try:
        descricao_nova = send_message(prompt)
    except Exception as e:
        descricao_nova = send_message(f'formate e remova os htmls dessa descrição. Somente adicione os dados referente ao produto: {descricao}')
        print(f'Erro ao editar descrição:', e)

    return descricao_nova

def executa_formatador_adiciona_json():
    # Abrir o arquivo JSON para leitura
    with open('produtos.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Acessar o array de produtos
    produtos = data

    # Iterar sobre cada produto no array
    for idx, produto in enumerate(produtos):
        produto['descricao'] = formatar_descricao(produto['descricao'])
        print(f'produto novo {idx} ', produto['descricao'])

    # Salvar os dados modificados de volta para o arquivo JSON
    with open('produtos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


executa_formatador_adiciona_json()