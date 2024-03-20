import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import time
import json
from PIL import Image
from urllib.parse import urlparse, parse_qs

from execel_process import adicionar_produto_planilha

def obter_imagens_e_produtos(diretorio):
    produtos_com_imagens = {}

    for produto_nome in os.listdir(diretorio):
        produto_diretorio = os.path.join(diretorio, produto_nome)

        if os.path.isdir(produto_diretorio):
            imagens_produto = []

            for imagem_nome in os.listdir(produto_diretorio):
                imagem_caminho = os.path.join(produto_diretorio, imagem_nome)

                if os.path.isfile(imagem_caminho):
                    try:
                        imagem = Image.open(imagem_caminho)
                        imagens_produto.append(imagem)
                    except Exception as e:
                        print(f"Erro ao abrir imagem {imagem_caminho}: {e}")

            produtos_com_imagens[produto_nome] = imagens_produto

    return produtos_com_imagens

def add_imagem_mercado_livre(produtos):
            diretorio_base = "imagens"
            produtos_com_imagens = obter_imagens_e_produtos(diretorio_base)

            print("Iniciando ações para publicar as fotos. Aguarde!")
            options = webdriver.ChromeOptions()
            options.add_argument(r"user-data-dir=C:\Users\thiag\AppData\Local\Google\Chrome\User Data\Profile 3")

            # Utilizando webdriver-manager para gerenciar o ChromeDriver
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            driver.get("https://www.mercadolivre.com.br/gestao_de_fotos?page=1")
            time.sleep(5)

            # Localizações dos elementos...
            MODAL_ELEMET = '/html/body/main/div[3]/div[2]'
            BOTAO_CRIAR_GRUPO_ELEMENT = '/html/body/main/div[1]/div/div[2]/div/button'

            CAMPO_TITULO_PRODUTO_ELEMENT = '/html/body/div[6]/div/div/div[2]/div[2]/div/form/div/div[1]/input'
            BOTAO_CRIAR_GRUPO_DE_FOTOS_ELEMENT = '/html/body/div[6]/div/div/div[2]/div[3]/button[1]'
            LISTA_DE_IMAGENS_DOS_PRODUTOS_ELEMENT = '/html/body/main/div[1]/div[2]'

            try:
                close_modal = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, MODAL_ELEMET))
                )
                close_modal.click()
            except:
                print("Modal não encontrado ou já está fechado.")

            pages = 1
            indice = 0
            for  produto in produtos:
                nome_produto = produto['nome']

                time.sleep(5)

                # clica no botão Criar grupos de fotos
                botao_criar_grupo = driver.find_element(By.XPATH, BOTAO_CRIAR_GRUPO_ELEMENT)
                botao_criar_grupo.click()
                print('1')
                #adiciona o nome do titulo do produto
                campo_titulo_produto = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[6]/div/div/div[2]/div[2]/div/form/div/div[1]/input'))
                )
                campo_titulo_produto.send_keys(nome_produto[:60])
                print('2')
                time.sleep(2)

                botao_criar_grupo_de_fotos = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[6]/div/div/div[2]/div[3]/button[1]'))
                )
                botao_criar_grupo_de_fotos.click()
                print('3')
                time.sleep(10)

                parsed_url = urlparse(driver.current_url)
                current_page = parse_qs(parsed_url.query)['page'][0]
                print('4')
                print('pages', pages, 'array pages: ', current_page)

                if int(current_page) > pages:
                    indice = 0
                    pages = pages + 1

                input_fotos = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'/html/body/main/div[1]/div/div[{3 + indice}]/div[2]/div/div/div/div/input'))
                )

                if input_fotos:
                    # Encontre o input para fotos dentro da div do produto encontrado
                    # Supondo que o input esteja diretamente dentro da div do produto com base na sua estrutura

                    nome_produto_limpo = "".join(x for x in nome_produto if x.isalnum() or x in " -_").rstrip()
                    imagens = produtos_com_imagens[nome_produto_limpo]
                    for imagem in imagens:
                        caminho_da_imagem = os.path.abspath(imagem.filename)  # Assegure-se que 'imagem' tem um atributo 'filename'

                        input_fotos.send_keys(caminho_da_imagem)

                        WebDriverWait(driver, 50).until(
                            EC.invisibility_of_element_located((By.XPATH,
                                                                f'/html/body/main/div[1]/div/div[3]/div[2]/div/div/div/div[2]/div/div[2]/ul/div[last()]/li/div/div[2]/div/div/div/svg'))
                        )

                else:
                    print("Div do produto não encontrada.")

                indice = indice + 1


            add_imagens_hospedadas_no_objeto(produtos,driver)
            #add_produto_mercado_livre(novo_produto,driver)

def add_imagens_hospedadas_no_objeto(produtos,driver):
    for indice, produto in enumerate(produtos):

        time.sleep(5)
        produtos[indice]['images']
        setinha_exibir_lista = driver.find_element(By.XPATH,
                                                   f'/html/body/main/div[1]/div[2]/div[{3 + indice}]/{"div" if indice == 0 else "div[1]"}/div[2]/a')
        print('setinha_exebir_lista', setinha_exibir_lista)
        print('setinha_exibir_lista.get_attribute', setinha_exibir_lista.get_attribute('class').split())
        # Verifica se o elemento possui a classe 'minha-classe'
        if 'list-picture-icon-chevron--down' in setinha_exibir_lista.get_attribute('class').split():
            setinha_exibir_lista.click()

        lista_de_imagens = driver.find_element(By.XPATH, f'/html/body/main/div[1]/div[2]/div[{3 + indice}]/div[2]/div/div/div/div[2]/div/div[2]/ul')

        # Encontre todas as tags <img> dentro do container
        imagens = lista_de_imagens.find_elements(By.TAG_NAME, "img")
        print('imagens', imagens)
        produtos_e_imagens = {}

        # Lista temporária para armazenar URLs de imagens do produto atual.
        urls_imagens_temp = [elemento.get_attribute('src') for elemento in imagens]
        produtos[indice]['images'] = ', '.join(urls_imagens_temp)

        print('produtos_e_imagens', produtos_e_imagens)
        print('produtos', produtos)

    # Salvar os dados modificados de volta para o arquivo JSON
    with open('produtos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)

def add_produto_mercado_livre(novo_produto,driver):
   driver.quit()
   adicionar_produto_planilha(novo_produto)