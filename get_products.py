from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import re
import search_product_ml
import time


def pegar_produto_mirao():
    driver = None  # Inicializa o driver como None
    produtos = []
    id_produto = 1
    pagina_atual = 1
    limite_produtos = 5
    qtd_produtos_add = 0
    # CASO FOR MUDAR A CATEGORIA DO PRODUTO, MUDAR ESSAS VARIAVES E O PROMPT
    CATEGORIA = 'perifericos'
    SUB_CATEGORIA = 'fone-de-ouvido'

    def prompt(nome_produto):
        PROMPT = f"\n\nMe traga as especificações em forma de objeto deste produto: {nome_produto}:" \
                 f"nome: formate este título {nome_produto} com as melhores palavras chaves e com no maximo 60 caracteries" \
                 f"marca: busque a marca do nome do produto acima e coloque aqui" \
                 f"modelo: busque a marca do nome do produto acima e coloque aqui" \
                 f"sem_fio: Se achar a informação do nome do produto acima coloque: Sim, se não achar coloque: Não" \
                 f"com_bluetooth: Se achar a informação do nome do produto acima coloque: Sim, se não achar coloque: Não" \
                 f"com_microfone: Se achar a informação do nome do produto acima coloque: Sim, se não achar coloque: Não" \
                 f"monaural: Se achar a informação do nome do produto acima coloque: Sim, se não achar coloque: Não" \
                 f"e_gamer: Se achar a informação do nome do produto acima coloque: Sim, se não achar coloque: Não" \
                 f"infantil: Se achar a informação do nome do produto acima coloque: Sim, se não achar coloque: Não" \
                 f"com_luz_led: Se achar a informação do nome do produto acima coloque: Sim, se não achar coloque: Não"
        return PROMPT

    while True:
        browser_to_use = "Chrome"  # "Chrome" "Firefox" "Ie"

        if browser_to_use == "Chrome":
            driver = webdriver.Chrome()
        elif browser_to_use == "Firefox":
            driver = webdriver.Firefox()
        elif browser_to_use == "Ie":  # This sucks!
            driver = webdriver.Ie()
            time.sleep(5)
        elif browser_to_use == "Edge":
            driver = webdriver.Edge()

        driver.set_window_size(1920, 1080)
        driver.get(f"https://www.mirao.com.br/{CATEGORIA}/{SUB_CATEGORIA}.html?p={pagina_atual}")

        # Espera para garantir que os elementos da página estejam carregados
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.product-items')))

        # Encontre todos os elementos 'product-item'
        product_items = driver.find_elements(By.CSS_SELECTOR, "ol.products.list.items.product-items > li.item.product.product-item")

        print('PAGINA:', pagina_atual)
        for index, produto in enumerate(product_items):

            print('PRODUTO ATUAL:',id_produto)

            produto_nao_e_mirao = driver.find_elements(By.XPATH, f'/html/body/div[3]/main/div[3]/div[1]/div[5]/ol/li[{index + 1}]/div/div/div[1]/div[2]')
            produto_sem_estoque = driver.find_elements(By.XPATH, f'/html/body/div[3]/main/div[3]/div[1]/div[5]/ol/li[{index + 1}]/div/div/div[2]/div/div/div/span')

            preco_texto = driver.find_element(By.XPATH, f'/html/body/div[3]/main/div[3]/div[1]/div[5]/ol/li[{index + 1}]/div/div/div[1]/div/span[1]/span/span/span').text


            print('valor text', preco_texto)
            preco_texto = preco_texto.replace(',', '.')
            preco = re.sub(r"[^0-9.]", "", preco_texto)
            preco_menor_que_50 = float(preco) < 50

            print('valor', preco)
            if produto_sem_estoque:
                print('PRODUTO NÃO TEM ESTOQUE')
                continue

            if produto_nao_e_mirao:
                print('PRODUTO NÃO É MIRÃO')
                continue

            if produto_sem_estoque:
                print('PRODUTO NÃO TEM ESTOQUE')
                continue

            if preco_menor_que_50:
                print('PRODUTO MENOR QUE 50')
                continue


            element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, f'/html/body/div[3]/main/div[3]/div[1]/div[5]/ol/li[{index + 1}]/div/div/strong/a')))

            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            driver.execute_script("arguments[0].click();", element)


            # Coleta os detalhes do produto na página de detalhes
            nome = driver.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/section[1]/div[1]/div[1]/h1/span').text

            descricao = driver.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/section[2]/section/div[2]')
            # Extrai o HTML interno do elemento de descrição
            descricao_html = descricao.get_attribute('innerHTML')
            # Substitui tags html por quebras de linha
            descricao_formatada = re.sub('<br>|</strong>|<h2>|</h2>', '\n', descricao_html)
            descricao_formatada = re.sub('&nbsp;', '', descricao_formatada)
            # Remove todas as outras tags HTML (simples exemplo, pode precisar de ajustes)
            descricao_formatada = re.sub('<[^<]+?>', '', descricao_formatada)
            # Substitui múltiplos espaços por um único espaço (se necessário)
            descricao = re.sub(' +', ' ', descricao_formatada)

            # Encontre a lista pelo seu ID (ou outro seletor adequado)
            lista = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/main/div[2]/div/section[1]/div[2]/div[2]/div[2]/div[2]/div[1]/div[3]')))
            # Encontre todas as divs dentro dos itens da lista
            divs_dentro_da_lista = lista.find_elements(By.CSS_SELECTOR, 'div > img')
            imagens = [img.get_attribute('src') for img in divs_dentro_da_lista]

            verifica_se_tem_pecas_minimas = driver.find_elements(By.CLASS_NAME, "product-after-price-box-qty")

            if verifica_se_tem_pecas_minimas:
                elemento_texto = verifica_se_tem_pecas_minimas[0].text  # Pega o texto do primeiro elemento
                elemento_texto = elemento_texto.replace('.', '')
                elemento_texto = re.sub(r"[^0-9.]", "", elemento_texto)

                preco = float(preco) * int(elemento_texto)

            produtos.append({
                'id': id_produto,
                'nome': nome,
                'descricao': descricao,
                'images': ", ".join(imagens),
                'preco': preco
            })
            id_produto += 1  # Incrementa o ID para o próximo produto

            # Retorna para a lista de produtos
            driver.back()

            # Recarregar os elementos da página para evitar StaleElementReferenceException
            driver.find_elements(By.XPATH, '/html/body/div[3]/main/div[3]/div[1]/div[5]/ol')

            if (limite_produtos == pagina_atual):
                break
            qtd_produtos_add = produtos[-1]['id']

            if(limite_produtos == qtd_produtos_add):
                    driver.quit()
                    print('ENTROU 1')
                    search_product_ml.consultar_produto(produtos, prompt)
                    break

        if (limite_produtos == qtd_produtos_add):
            break
        driver.quit()
        pagina_atual += 1

