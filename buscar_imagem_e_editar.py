import time

import undetected_chromedriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json

def check_atualizou_img(produto, produtos):
    produto['alterou_imagem'] = True

    # Salvar os dados modificados de volta para o arquivo JSON
    with open('produtos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


def continua_operacao(driver,produto):
    button = produto.find_element(By.CSS_SELECTOR, '.lXbkTc')
    button.click()

    guia_ids = driver.window_handles
    driver.switch_to.window(guia_ids[-1])
    print('ENTROU 3')
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.ui-pdp-gallery__figure'))
    )
    print('ENTROU 4')

    print('ENTROU 5')
    # Encontrando todos os elementos de imagem dentro de elementos com a classe 'ui-pdp-gallery__figure'
    # Encontre todos os elementos <figure> que contêm as imagens
    spans = driver.find_elements(By.CSS_SELECTOR, "div.ui-pdp-gallery__column span")

    # Lista para armazenar as URLs das imagens
    image_urls = []
    print('spans', spans)
    # Percorra cada elemento <figure> encontrado
    for span in spans:
        try:
            # Tente encontrar a tag <img> dentro da tag <figure>
            img = span.find_element(By.CSS_SELECTOR, 'figure img')
            img_url = img.get_attribute('src')
            print('img_url', img_url)
            # Se a tag <img> for encontrada e o 'src' obtido, adicione à lista
            image_urls.append(img_url)
        except NoSuchElementException:
            continue

    return image_urls
    # Exibir a lista de URLs coletadas
    print('image_urls', image_urls)


def buscar_imagem_produto(produto_url_name):
    profile = "/Users/thiag/AppData/Local/Google/Chrome/User Data/Profile 3"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir%3Dc{profile}")

    driver = webdriver.Chrome(options=chrome_options, use_subprocess=True)
    driver.get(f"https://google.com")

    element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]')))
    driver.execute_script("arguments[0].click();", element)

    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[3]/c-wiz/div[2]/div/div[3]/div[2]/c-wiz/div[2]/input'))
    )
    print('1')
    input = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[3]/c-wiz/div[2]/div/div[3]/div[2]/c-wiz/div[2]/input')
    input.send_keys(produto_url_name)
    print('2')
    button = driver.find_element(By.CSS_SELECTOR, 'div.Qwbd3')
    button.click()

    time.sleep(4)
    # Encontrar todos os elementos que contêm informações dos produtos
    produtos = driver.find_elements(By.CSS_SELECTOR, 'div.Vd9M6')

    for produto in produtos:
        try:
            # Extrair o título
            titulo = produto.find_element(By.CSS_SELECTOR, '.fjbPGe').text
            print('titulo', titulo, ' verificação: ',titulo.lower() == 'mercado livre')
            if titulo.lower() == 'mercado livre':
                print('1')
                link_element = produto.find_element(By.CSS_SELECTOR, '.lXbkTc')
                # Extraindo o valor do atributo href
                print('2')
                href_value = link_element.get_attribute('href')


                padrao_1 = 'https://www.mercadolivre.com.br/pagina/'
                padrao_2 = 'https://lista.mercadolivre.com.br/'
                padrao_3 = 'https://www.mercadolivre.com.br/blog/'
                # Usando o método .startswith() para verificar se a URL começa com o padrão
                comeca_com_padrao_1 = href_value.startswith(padrao_1)
                comeca_com_padrao_2 = href_value.startswith(padrao_2)
                comeca_com_padrao_3 = href_value.startswith(padrao_3)

                if comeca_com_padrao_1:
                    continue

                if comeca_com_padrao_2:
                    continue

                if comeca_com_padrao_3:
                    continue

                img_array = continua_operacao(driver,produto)

                driver.quit()
                return img_array
                break

            # O preço não está disponível de forma explícita no HTML fornecido.
            # Você precisará ajustar o seletor conforme a estrutura do HTML para o preço.
            # preço = produto.find_element(By.CSS_SELECTOR, 'seletor_para_o_preço').text

            print(f'Título: {titulo}')
            # print(f'Preço: {preço}\n') # Descomente quando o seletor do preço estiver correto
        except Exception as e:
            print(f'Erro ao processar o produto {href_value}: {e}')

    driver.quit()
    return []


def executa_formatador_adiciona_json():
    # Abrir o arquivo JSON para leitura
    with open('produtos.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Acessar o array de produtos
    produtos = data

    posicao_ultimo_true = None
    for i in range(len(produtos) - 1, -1, -1):
        if produtos[i]["alterou_imagem"] == True:
            posicao_ultimo_true = i
            break

    # Filtrar os objetos a partir do último com "alterou_imagem": true
    objetos_filtrados = produtos[posicao_ultimo_true:] if posicao_ultimo_true is not None else []
    print('objetos_filtrados: ',objetos_filtrados)

    # Iterar sobre cada produto no array
    for idx, produto in enumerate(objetos_filtrados):
        imagens = produto["images"].split(", ")
        primeira_imagem = imagens[0]

        if produto['alterou_imagem'] == True:
            continue


        images_array = buscar_imagem_produto(primeira_imagem)
        print('images_array: ', images_array)
        if len(images_array) == 0:
            continue

        urls_formatadas = ", ".join(images_array)
        produto['images'] = urls_formatadas

        check_atualizou_img(produto, produtos)
        print(f'produto imagem {idx}: ', produto['images'])


executa_formatador_adiciona_json()

