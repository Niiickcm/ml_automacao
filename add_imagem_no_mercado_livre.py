import json
from utils import baixar_e_redimensionar_imagens
from ml_webscrapping import obter_imagens_e_produtos
import requests
import os

url_api = 'https://api.mercadolibre.com'
token_api  = 'APP_USR-1511993846027051-031318-398da912eed14b451f2b0c0bdb4558b3-1685976816'
headers = {
    'Authorization': f'Bearer {token_api}',
}

def add_imagem_mercado_livre_request(produtos):
    diretorio_base = "imagens"
    produtos_com_imagens = obter_imagens_e_produtos(diretorio_base)

    for idx, produto in enumerate(produtos):
        nome_produto = produto['nome']

        nome_produto_limpo = "".join(x for x in nome_produto if x.isalnum() or x in " -_").rstrip()
        imagens = produtos_com_imagens[nome_produto_limpo]
        array_imagens = []
        print('Produto: ',idx)
        for index, imagem in enumerate(imagens):
            caminho_da_imagem = os.path.abspath(imagem.filename)  # Assegure-se que 'imagem' tem um atributo 'filename'
            url = f"{url_api}/pictures/items/upload"

            with open(caminho_da_imagem, 'rb') as file:
                files = {'file': (os.path.basename(caminho_da_imagem), file, 'image/png')}
                resp = requests.post(url, headers=headers, files=files)

                if resp.ok:
                    response = resp.json()
                    print(f'teste {index}', response)
                    imagem_url = response['variations'][0]['url']
                    array_imagens.append(imagem_url)

        print('array_imagens',array_imagens)
        string_urls = ', '.join(array_imagens)
        print('string_urls', string_urls)
        produto['images'] = f"{string_urls}"

        with open('produtos.json', 'w', encoding='utf-8') as arquivo:
            json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


def executa_formatador_adiciona_json():
    # Abrir o arquivo JSON para leitura
    with open('produtos.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Acessar o array de produtos
    produtos = data

    #baixar_e_redimensionar_imagens(produtos)
    add_imagem_mercado_livre_request(produtos)



executa_formatador_adiciona_json()

