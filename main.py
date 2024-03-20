import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from get_products import pegar_produto_mirao
from selenium.webdriver.support.ui import Select
from search_product_ml import calcular_preco_venda
from ia_generate import send_message
from dotenv import load_dotenv
import os
import requests
import json
import re

load_dotenv()

token_api = os.getenv('MERCADO_LIVRE_TOKEN')

url_api = 'https://api.mercadolibre.com'
headers = {
    'Authorization': f'Bearer {token_api}',
    'Content-Type': 'application/json'
}

def pegar_codigo_universal(nome):
    resultados = []
    try_count = 0
    max_tries = 3  # Número máximo de tentativas
    driver = None
    profile = "/Users/thiag/AppData/Local/Google/Chrome/User Data/Profile 3"

    while try_count < max_tries:
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(f"user-data-dir%3Dc{profile}")

            driver = webdriver.Chrome(options=chrome_options, use_subprocess=True)

            driver.get("https://cosmos.bluesoft.com.br/pesquisar?utf8=✓&q=teste")

            WebDriverWait(driver, 40).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/form/div/div/input'))
            )

            nome_produto = nome

            # clica no botão Criar grupos de fotos
            campo = driver.find_element(By.XPATH, '/html/body/div[2]/form/div/div/input')
            campo.clear()
            campo.send_keys(nome_produto)

            body_element = driver.find_element(By.TAG_NAME, "body")
            body_element.click()

            botao_pesquisar = driver.find_element(By.XPATH, '/html/body/div[2]/form/div/div/span/button')
            botao_pesquisar.click()

            time.sleep(2)

            pegar_codigo_universal = driver.find_element(By.XPATH, '/html/body/div[3]/section/div[2]/div[1]/ul/li[1]/div[2]/ul/li[2]/a').text
            print('VALOR',pegar_codigo_universal)

            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            try_count += 1
            driver.quit()
            print(f"Tentativa {try_count} de {max_tries}")
        finally:
            if 'driver' in locals() or 'driver' in globals() and driver is not None:
                driver.quit()

    return pegar_codigo_universal


def verificar_presenca_nao(texto):
    # Pattern que busca por 'não' ou 'nao'
    pattern = r'\bn(?:ã|a)o\b'
    texto = texto.lower()
    # re.IGNORECASE faz a busca ser insensível a maiúsculas e minúsculas
    if re.search(pattern, texto, re.IGNORECASE):
        return True
    else:
        return False


def econtra_categoria(obj):
    tem_categorias = True
    id_categoria = send_message(f'tenho este produto {obj} qual seria a melhor categoria para ele dentre dessas opções {dataCategories} me retorne somente o id da categoria')

    while True:

        print('categoria', id_categoria)
        url = f"{url_api}/categories/{id_categoria}"

        payload = {}

        resp = requests.request("GET", url, headers=headers, data=payload)
        response = resp.json()
        categorias_filho = response['children_categories']

        tem_categorias = len(categorias_filho) > 1

        if not tem_categorias:
            break

        id_categoria = send_message(f"tenho este produto {obj} qual seria a melhor sub categoria para ele dentre dessas opções {categorias_filho} me retorne somente o id da categoria")


        print('tem_categorias', tem_categorias)
        print(categorias_filho)
    print(f"A última categoria escolhida foi: {id_categoria}")
    return id_categoria


def pegar_atributos_produto(id_categoria):
    url = f"{url_api}/categories/{id_categoria}/technical_specs/input"

    payload = {}

    resp = requests.request("GET", url, headers=headers, data=payload)
    response = resp.json()
    array_atributos = response['groups']
    print('response test',response)
    # Lista para armazenar objetos que atendem aos critérios
    filtered_attributes = []

    # Loop para iterar sobre cada objeto no array
    for idx, attribute in enumerate(array_atributos):
        # Verifica se o objeto tem relevance = 1 e se não possui a chave "hidden": true dentro de tags
        for idx_sub, sub_attribute in enumerate(attribute['components']):
            for idx_array, array_atributes in enumerate(sub_attribute['attributes']):
                if array_atributes["relevance"] == 1 and not "hidden" in array_atributes["tags"]:
                    print('attribute', array_atributes)

                    filtered_attributes.append(array_atributes)

    # Exibe os objetos filtrados
    return filtered_attributes


def preencher_atributos_produto(obj,categoria):
    array_atributos = pegar_atributos_produto(categoria)
    array_atributos_com_dados = []
    print('todos array_atributos:',len(array_atributos))
    print('array_atributos:', array_atributos)

    for atributo in array_atributos:
        time.sleep(2)
        try:
            if atributo["value_type"] == 'string':

                if atributo["id"] == 'GTIN':
                    cod = pegar_codigo_universal(obj['nome'])
                    array_atributos_com_dados.append(
                        {
                            "id": atributo["id"],
                            "value_name": cod
                        }
                    )
                    continue

                valor = send_message(
                    f'Os dados são de produtos confiaveis,por favor nao de erro! Procure este dado {atributo["name"]} {"ou pegue um desses pelo nome", atributo.get("values", "") if atributo.get("values") else ""} dentro dos dados desse produto: {obj} e me retorne somente o nome')
                print('valor',valor)

                print(f'string {atributo["name"]}', valor)
                if verificar_presenca_nao(valor) and not "required" in atributo["tags"]:
                    array_atributos_com_dados.append(
                        {
                            "id": atributo["id"],
                            "value_id": "-1",
                            "value_name": None
                        })
                else:
                    array_atributos_com_dados.append(
                        {
                            "id": atributo["id"],
                            "value_name": 'nao' if verificar_presenca_nao(valor) else valor
                        })

            if atributo["value_type"] == 'number':
                valor = send_message(
                    f'Nenhum dos dados são explicitos, são descrição de produtos! Procure este dado {atributo["name"]} {"ou pegue um desses pelo nome", atributo.get("values", "") if atributo.get("values") else ""} dentro dos dados desse produto: {obj} e me retorne somente o valor')

                print(f'number {atributo["name"]}:', valor)

                array_atributos_com_dados.append(
                    {
                        "id": atributo["id"],
                        "value_name": 1 if verificar_presenca_nao(valor) else int(valor)
                    }
                )

            if atributo["value_type"] == 'number_unit':
                valor = send_message(
                    f'Nenhum dos dados são explicitos, são descrição de produtos! Procure este dado {atributo["name"]} selecione o valor correto que esta dentro desta lista: {atributo["allowed_units"]}  de acordo com os dados desse produto: {obj} e me retorne um objeto assim: valor: primeiro valor numerico aqui, valor_segundario: segundo valor aqui retornado o objeto do valor selecionado')

                # Converta a string JSON para um dicionário Python
                objeto = json.loads(valor)
                print(f'number_unit {atributo["name"]}:', valor)
                #valor_value_name = objeto['valor'].replace(',', '.')
                print(f'Passou:', objeto['valor'], 'type ', type(objeto['valor']))
                array_atributos_com_dados.append(
                    {
                        "id": atributo["id"],
                        "value_name":  0 if valor else float( objeto['valor']),
                        "allowed_units": 0 if valor else objeto.get('valor_segundario', objeto.get('valor_secundario', 0))
                    }
                )
                print('number_unit array_atributos_com_dados',array_atributos_com_dados)

            if atributo["value_type"] == 'boolean':
                valor = send_message(
                    f'Nenhum dos dados são explicitos, são descrição de produtos! Procure este dado {atributo["name"]} de acordo com os dados desse produto: {obj} e me retorne somente se a resposta for não = 242084, se a resposta for sim = 242085')

                print(f'boolean {atributo["name"]}', valor)

                array_atributos_com_dados.append(
                    {
                        "id": atributo["id"],
                        "values": [{"id": "242084"}] if verificar_presenca_nao(valor) else [{"id": valor}],
                    }
                )

            if atributo["value_type"] == 'list':
                valor = send_message(f'Nenhum dos dados são explicitos, são descrição de produtos! Procure este dado {atributo["name"]} {"ou pegue esse pelo nome", atributo.get("values", "") if atributo.get("values") else ""} de acordo com os dados desse produto: {obj} e me retorne o name ou o nome que você mesmo escolheu')

                print('valor antes',valor, ' tipo do valor ',type(valor))
                # Converta a string para uma lista Python
                print(f'LIST {atributo["name"]}',valor)

                array_atributos_com_dados.append(
                    {
                        "id": atributo["id"],
                        "value_name": '' if verificar_presenca_nao(valor) else valor,
                    }
                )
        except Exception as e:
            print('Ocorreu um erro nos tipos de atributos: ', e)
            if not "required" in atributo["tags"]:
                continue

    print('array_atributos_com_dados',array_atributos_com_dados)
    return array_atributos_com_dados


def adicionar_descricao(id,descricao):
    url = f"{url_api}/items/{id}/description"
    payload = json.dumps({
        "plain_text": descricao,
    })

    resp = requests.request("POST", url, headers=headers, data=payload)
    response = resp.json()
    print('descricao response: ',response)


def cadastrar_produto(obj,categoria):
    todos_atributos = preencher_atributos_produto(obj,categoria)
    url = f"{url_api}/items"
    # Separa a string de imagens em uma lista
    urls = obj["images"].split(", ")

    # Cria a nova lista de dicionários
    imagens = [{"source": url} for url in urls]
    #Premium = gold_pro, Clássico = gold_special
    tipo_anuncio = ['gold_special', 'gold_pro']
    anuncio_selecionado = tipo_anuncio[0]
    taxa_percentual = 13 if anuncio_selecionado == tipo_anuncio[0] else 18  # 18%
    custo_frete = 24.54  # R$ 24.54
    margem_lucro = 10  # 10%
    preco_produto = float(obj['preco'])
    preco_venda = calcular_preco_venda(preco_produto, taxa_percentual, custo_frete, margem_lucro)
    preco_venda = round(preco_venda, 2)

    payload = json.dumps({
        "title": obj['nome'][:60],
        "category_id": categoria,
        "price": preco_venda,
        "currency_id": "BRL",
        "available_quantity": 500,
        "buying_mode": "buy_it_now",
        "condition": "new",
        "listing_type_id": anuncio_selecionado,
        "shipping": {
            "free_shipping": True,
            "local_pick_up": False
        },
        "sale_terms": [
            {
                "id": "WARRANTY_TYPE",
                "value_name": "Garantia do vendedor"
            },
            {
                "id": "WARRANTY_TIME",
                "value_name": "30 días"
            }
        ],
        "pictures": imagens,
        "attributes": [*todos_atributos]
    })

    try:
        resp = requests.request("POST", url, headers=headers, data=payload)
        print('status_code ',resp.status_code)
        response = resp.json()
        print('response ', response, ' type: ',type(response))
        status = 201 if response['status'] == 'paused' else response['status']

        print('status', status)

        if status not in (200, 201):
            print('payload erro: ', payload)
            raise ValueError(f"Ocorreu algum erro ao cadastrar: {status}:", payload)

        id = response['id']
        adicionar_descricao(id, obj["descricao"])
        print('Produto cadastrado com sucesso!', payload)
    except Exception as e:
        print(f"Ocorreu um erro ao cadastrar produto: {e}")
        raise


def check_utilizou(produto, produtos):
    produto['utilizou'] = True

    # Salvar os dados modificados de volta para o arquivo JSON
    with open('produtos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


def anunciar_mercado_livre():
    # Abrir o arquivo JSON para leitura
    with open('produtos.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Acessar o array de produtos
    produtos = data

    # Iterar sobre cada produto no array
    for produto in produtos:

        if produto['utilizou'] == True:
            continue

        id_categoria = econtra_categoria(produto)

        cadastrar_produto(produto, id_categoria)

        check_utilizou(produto, produtos)

anunciar_mercado_livre()








