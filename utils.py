import requests
from PIL import Image, ImageDraw
from io import BytesIO
from ml_webscrapping import add_imagem_mercado_livre  # Certifique-se de que esta função está implementada corretamente
import os

# Função para formatar os dados dos produtos para o prompt
def formatar_dados_para_prompt(produto):
    prompt = "Informações dos produtos:\n"
    prompt += f"ID: {produto['id']}, Nome: {produto['nome']}, Descrição: {produto['descricao']}, Preço: ${produto['preco']}\n"
    return prompt

def baixar_e_redimensionar_imagens(produtos, tamanho_desejado=(700, 700)):
    for produto in produtos:
        nome_produto = produto['nome']
        imagens_produto = []

        for url_imagem in produto['images'].split(', '):
            resposta = requests.get(url_imagem)
            if resposta.status_code == 200:
                imagem = Image.open(BytesIO(resposta.content))
                if imagem.size != tamanho_desejado:
                    imagem = redimensionar_imagem(imagem, tamanho_desejado)
                # Supondo que você deseja remover um logo/texto e bordas de todas as imagens
                imagens_produto.append(imagem)
            else:
                print(f"Erro ao baixar a imagem {url_imagem} do produto {nome_produto}. Código de status HTTP: {resposta.status_code}")

        if imagens_produto:
            processar_imagem_final(nome_produto, imagens_produto)

    add_imagem_mercado_livre(produtos)  # Certifique-se de que esta função está pronta para aceitar os parâmetros corretos

def redimensionar_imagem(imagem, tamanho_desejado):
    return imagem.resize(tamanho_desejado, Image.Resampling.LANCZOS)


def processar_imagem_final(nome_produto, imagens):
    base_dir = "imagens"
    nome_produto_limpo = "".join(x for x in nome_produto if x.isalnum() or x in " -_").rstrip()
    produto_dir = os.path.join(base_dir, nome_produto_limpo)
    os.makedirs(produto_dir, exist_ok=True)

    for indice, imagem in enumerate(imagens):
        caminho_arquivo = os.path.join(produto_dir, f'{nome_produto_limpo}_{indice}.png')
        imagem.save(caminho_arquivo)
        print(f"Imagem {indice} do produto '{nome_produto_limpo}' processada e salva: {caminho_arquivo}")
