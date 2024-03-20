import time
import ast
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import undetected_chromedriver as webdriver

import ia_generate
import utils



def consultar_produto(produtos, prompt):
    resultados = []
    try_count = 0
    max_tries = 3  # Número máximo de tentativas
    driver = None

    while try_count < max_tries:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(r'user-data-dir="C:\\Users\\thiag\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 3"')
            # Utilizando webdriver-manager para gerenciar o ChromeDriver
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            driver.get("https://cosmos.bluesoft.com.br/pesquisar?utf8=✓&q=teste")

            WebDriverWait(driver, 40).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/form/div/div/input'))
            )

            for produto in produtos:
                nome_produto = produto["nome"]
                print('produto["preco"]',produto["preco"],' tipo: ',type)

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

                #produto_data = utils.formatar_dados_para_prompt(produto)
                #ia_generate.send_message(produto_data)

                time.sleep(1)

                promptValue = prompt(nome_produto)

                # Esta chamada é simulada. Substitua-a pela chamada real à sua função send_message.
                response = ia_generate.send_message(promptValue)
                print("PRODUTO ID:", produto["id"])
                try:
                    # Tentativa de pré-processamento para remover espaços em branco iniciais
                    response_processed = response.strip().replace("```", "")
                    time.sleep(2)
                    # Tentando converter a string processada em um objeto Python
                    response_obj = ast.literal_eval(response_processed)

                except SyntaxError as e:
                    print(f"Erro de sintaxe ao analisar a resposta: {e}")
                except ValueError as e:
                    print(f"Erro de valor ao tentar converter a resposta: {e}")

                # Aqui, você processaria a resposta para extrair os dados necessários.
                # Para este exemplo, apenas simulamos a resposta como um dicionário de especificações.
                tipo_anuncio = ['Clássico', 'Premium']
                anuncio_selecionado = tipo_anuncio[1]
                preco_produto = float(produto["preco"])
                taxa_percentual = 13 if anuncio_selecionado == tipo_anuncio[0] else 18  # 18%
                custo_frete = 24.54  # R$ 24.54
                margem_lucro = 10  # 10%
                preco_venda = calcular_preco_venda(preco_produto, taxa_percentual, custo_frete, margem_lucro)

                especificacoes = {
                    "id": produto["id"],
                    "nome": response_obj['nome'],
                    "descricao": produto["descricao"],
                    "images": produto["images"],
                    "preco": preco_venda,
                    "codigo_universal": pegar_codigo_universal,
                    "tipo_anuncio": anuncio_selecionado
                }
                produto_completo = {**especificacoes, **response_obj}

                resultados.append(produto_completo)
            driver.quit()
            utils.baixar_e_redimensionar_imagens(resultados)
            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            try_count += 1
            driver.quit()
            print(f"Tentativa {try_count} de {max_tries}")
        finally:
            if 'driver' in locals() or 'driver' in globals() and driver is not None:
                driver.quit()



def calcular_preco_venda(preco_produto, taxa_percentual, custo_frete, margem_lucro):
    # Converter a porcentagem para decimal
    taxa_decimal = taxa_percentual / 100
    margem_decimal = margem_lucro / 100
    valor_frete_gratis = 79
    custo_por_unidade = 6

    # Calcular o custo total
    custo_total = preco_produto + custo_frete

    # Primeiro, calcular o preço de venda sem considerar o valor do frete grátis
    # Este será o preço base usado para comparar com o valor do frete grátis
    preco_base_com_taxa = custo_total / (1 - taxa_decimal)

    preco_venda_base = preco_base_com_taxa * (1 + margem_decimal)

    if preco_venda_base < valor_frete_gratis:
        custo_total_com_unidade = preco_produto + custo_por_unidade

        # Recalcular o preço de venda considerando o custo por unidade
        preco_final_com_taxa_unidade = custo_total_com_unidade / (1 - taxa_decimal)
        preco_venda_final_com_unidade = preco_final_com_taxa_unidade * (1 + margem_decimal)
        return preco_venda_final_com_unidade
    else:
        return preco_venda_base
