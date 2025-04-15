import logging

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from pathlib import Path

# Título do aplicativo
st.title('Análise de Dados dos Estudantes')

# Configuração do log com timestamp
logging.basicConfig(
    filename='user_actions.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log_acao(acao):
    """
    Registra uma ação do usuário no log.

    Parameters:
    acao (str): A descrição da ação a ser registrada.
    """
    logging.info(f"{acao}")


def solicitar_nome_usuario():
    """
    Solicita o nome do usuário e valida.

    Returns:
    str: O nome do usuário se for válido, caso contrário, None.
    """
    nome = st.text_input("Digite seu nome:")
    if nome:
        if len(nome.replace(" ", "")) >= 3 and all(part.isalpha() for part in nome.split()):
            log_acao(f"Nome do usuário: {nome}")
            return nome
        else:
            st.error("Nome inválido. Deve conter pelo menos 3 caracteres alfabéticos.")
    return None


def validar_arquivo(uploaded_file):
    """
    Valida o tipo de arquivo.

    Parameters:
    uploaded_file (UploadedFile): O arquivo carregado pelo usuário.

    Returns:
    bool: True se o arquivo for válido, False caso contrário.
    """
    if uploaded_file is not None:
        ext = Path(uploaded_file.name).suffix
        if ext in ['.csv', '.json']:
            return True
        st.error("Formato de arquivo não suportado.")
    return False


def validar_coluna_numerica(df, coluna):
    """
    Verifica se a coluna é numérica.

    Parameters:
    df (DataFrame): O DataFrame contendo os dados.
    coluna (str): O nome da coluna a ser verificada.

    Returns:
    bool: True se a coluna for numérica, False caso contrário.
    """
    return pd.api.types.is_numeric_dtype(df[coluna])


def carregar_dados(uploaded_file):
    """
    Carrega dados de um arquivo CSV ou JSON.

    Parameters:
    uploaded_file (UploadedFile): O arquivo carregado pelo usuário.

    Returns:
    DataFrame: O DataFrame com os dados carregados.
    """
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.json'):
        return pd.read_json(uploaded_file)


nome_usuario = solicitar_nome_usuario()