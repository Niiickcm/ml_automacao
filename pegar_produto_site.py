from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as webdriver
from selenium.webdriver.support.ui import Select
from ia_generate import send_message
import json
import re

def pegar_produto_dinka():
    driver = None  # Inicializa o driver como None
    produtos = []
    id_produto = 1
    pagina_atual = 1
    limite_produtos = 250 #3.503
    qtd_produtos_add = 0
    # CASO FOR MUDAR A CATEGORIA DO PRODUTO, MUDAR ESSAS VARIAVES E O PROMPT
    CATEGORIA = 'todos-produtos'
    SUB_CATEGORIA = 'fone-de-ouvido'

    profile = "/Users/thiag/AppData/Local/Google/Chrome/User Data/Profile 3"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir%3Dc{profile}")

    driver = webdriver.Chrome(options=chrome_options, use_subprocess=True)
    driver.get(f"https://dinka.com.br/categoria-produto/fornecedor-dropshipping/{CATEGORIA}/page/{pagina_atual}")
    while True:
        # Espera para garantir que os elementos da página estejam carregados
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.shop-container')))

        # Encontre todos os elementos 'product-item'
        product_items = driver.find_elements(By.CSS_SELECTOR, ".products > div.product-small")

        print('PAGINA:', pagina_atual)
        for index, produto in enumerate(product_items):

            print('PRODUTO ATUAL:', id_produto)

            element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, f'/html/body/div[2]/main/div/div/div/div[{ 3 if pagina_atual == 1 else 2}]/div[{index + 1}]/div/div[2]/div[2]/div[1]/p/a')))
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            driver.execute_script("arguments[0].click();", element)

            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[2]/main/div/div[2]/div/div[1]/div/div[2]/div[2]/p/span/bdi')))
                preco_texto = driver.find_element(By.XPATH,
                                                  '/html/body/div[2]/main/div/div[2]/div/div[1]/div/div[2]/div[2]/p/span/bdi').text
                preco_texto = preco_texto.replace(',', '.')
                preco = re.sub(r"[^0-9.]", "", preco_texto)
            except Exception as e:
                print(e)

            try:
                elemento_select = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div/div[2]/div/div[1]/div/div[2]/form/table/tbody/tr/td/select'))
                )
                select = Select(elemento_select)
                select.select_by_index(1)
            except Exception as e:
                print("")

            produto_sem_estoque = driver.find_element(By.CSS_SELECTOR, '.stock').text
            print('produto_sem_estoque', produto_sem_estoque)
            if 'fora' in produto_sem_estoque.lower():
                driver.back()
                continue

            # Coleta os detalhes do produto na página de detalhes
            nome_real = driver.find_element(By.XPATH, '/html/body/div[2]/main/div/div[2]/div/div[1]/div/div[2]/h1').text

            descricao = driver.find_element(By.XPATH, '/html/body/div[2]/main/div/div[2]/div/div[2]/div/div[1]/div/div[1]')
            # Extrai o HTML interno do elemento de descrição
            descricao = descricao.get_attribute('innerHTML')
            # Encontre a lista pelo seu ID (ou outro seletor adequado)
            try:
                lista = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.flickity-slider')))
                divs_dentro_da_lista = lista.find_elements(By.CSS_SELECTOR, 'div > a > img')
                print('divs_dentro_da_lista', divs_dentro_da_lista)
                imagens = [img.get_attribute('src') for img in divs_dentro_da_lista]
            except Exception as e:
                print('ERRO AO COLETAR IMAGEM:', e)

            # Encontre todas as divs dentro dos itens da lista

            try:
                dados_info_adicional = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div/div[2]/div/div[2]/div/div[1]/div/div[2]')))
                dados_info_adicional = dados_info_adicional.get_attribute('innerHTML')
            except Exception as e:
                print(e)

            try:
                nome = send_message(f'me traga somente o titulo com até 60 caracteres que seja facil dos usuarios acharem para anunciar este produto no mercado livre: nome do produto: {nome_real}, descrição do produto:{descricao}')
            except Exception as e:
                nome = nome_real
                print('Erro ao editar nome na ia', e)

            obj = {
                'id': id_produto,
                'nome': nome,
                'nome_real': nome_real,
                'descricao': descricao,
                'informacao_adicional': dados_info_adicional,
                'images': ", ".join(imagens),
                'preco': preco,
                'utilizou': False
            }
            produtos.append(obj)

            print('produtos', obj)

            id_produto += 1  # Incrementa o ID para o próximo produto

            # Retorna para a lista de produtos
            driver.back()

            # Recarregar os elementos da página para evitar StaleElementReferenceException
            driver.find_elements(By.XPATH, '/html/body/div[2]/main/div/div/div/div[2]')

            if (limite_produtos == pagina_atual):
                break
            qtd_produtos_add = produtos[-1]['id']

            if(limite_produtos == qtd_produtos_add):
                    driver.quit()
                    print('ENTROU 1')
                    # Salve a lista de produtos em um arquivo JSON
                    with open('produtos.json', 'w', encoding='utf-8') as f:
                        json.dump(produtos, f, ensure_ascii=False, indent=4)

                    print("Arquivo 'produtos.json' salvo com sucesso.")
                    break

        if (limite_produtos == qtd_produtos_add):
            break

        pagina_atual += 1
        ultimo_item = driver.find_elements(By.CSS_SELECTOR, "ul.page-numbers li a.page-number")[-1]
        ultimo_item.click()

pegar_produto_dinka()