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

if nome_usuario:
    uploaded_file = st.file_uploader("Escolha o arquivo CSV ou JSON", type=['csv', 'json'])

    if validar_arquivo(uploaded_file):
        log_acao(f"Arquivo carregado: {uploaded_file.name}")
        df = carregar_dados(uploaded_file)
        df.replace("None", pd.NA, inplace=True)

        df_limpo = df.copy()

        if 'data_cleaned' not in st.session_state:
            st.session_state.data_cleaned = False

        tab1, tab2, tab3, tab4 = st.tabs([
            "Dados Básicos",
            "Limpeza de Dados",
            "Análise Estatística",
            "Gráficos"
        ])

        # Tab 1: Dados Básicos
        with tab1:
            st.header("1. Informações Básicas")
            st.write(f"Quantidade de dados carregados: {len(df)}")
            total_mulheres = df[df['Gender'] == "Female"].shape[0]
            total_homens = df[df['Gender'] == "Male"].shape[0]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Mulheres", total_mulheres)
            with col2:
                st.metric("Total de Homens", total_homens)

            registros_nulos_educacao = df['Parent_Education_Level'].isnull().sum()
            st.write(
                "Registros sem informação sobre nível de escolaridade dos pais: "
                f"{registros_nulos_educacao}"
            )

        # Tab 2: Limpeza de Dados
        with tab2:
            st.header("2. Limpeza de Dados")

            if st.button("Limpar Dados"):
                df_limpo = df.copy()
                df_limpo = df_limpo.dropna(subset=['Parent_Education_Level'])

                mediana_attendance = df['Attendance (%)'].median()
                df_limpo['Attendance (%)'] = df_limpo['Attendance (%)'].fillna(mediana_attendance)

                st.write("Dados limpos:")
                st.dataframe(df_limpo)

                soma_attendance = df_limpo['Attendance (%)'].sum()
                st.metric("Soma total de presença", f"{soma_attendance:.2f}%")

                st.session_state.data_cleaned = True
                log_acao("Dados limpos")

        # Tab 3: Análise Estatística
        if st.session_state.data_cleaned:
            with tab3:
                st.header("3. Análise Estatística")
                colunas_numericas = df_limpo.select_dtypes(include=['int64', 'float64']).columns
                coluna = st.selectbox("Escolha uma coluna para análise:", colunas_numericas)

                if coluna and validar_coluna_numerica(df_limpo, coluna):
                    media = df_limpo[coluna].mean()
                    mediana = df_limpo[coluna].median()
                    moda = df_limpo[coluna].mode()[0]
                    desvio_padrao = df_limpo[coluna].std()

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Média", f"{media:.2f}")
                    with col2:
                        st.metric("Mediana", f"{mediana:.2f}")
                    with col3:
                        st.metric("Moda", f"{moda:.2f}")
                    with col4:
                        st.metric("Desvio Padrão", f"{desvio_padrao:.2f}")
                    log_acao(f"Análise estatística realizada na coluna: {coluna}")
        else:
            with tab3:
                st.warning("Por favor, execute a limpeza de dados primeiro.")

        # Tab 4: Gráficos
        if st.session_state.data_cleaned:
            with tab4:
                st.header("4. Gráficos")

                if 'show_detailed' not in st.session_state:
                    st.session_state.show_detailed = False

                if st.button("Alternar Gráfico"):
                    st.session_state.show_detailed = not st.session_state.show_detailed

                if st.session_state.show_detailed:
                    st.subheader("Horas de Sono x Nota Final")
                    fig1, ax1 = plt.subplots()
                    ax1.scatter(df_limpo['Sleep_Hours_per_Night'], df_limpo['Final_Score'])
                    ax1.set_title('Relação entre Horas de Sono X Nota Final')
                    ax1.set_xlabel('Horas de Sono por Noite')
                    ax1.set_ylabel('Nota Final')
                    ax1.set_xlim(0, max(df_limpo['Sleep_Hours_per_Night']) + 2)
                    ax1.set_ylim(0, max(df_limpo['Final_Score']) + 20)
                    st.pyplot(fig1)
                else:
                    st.subheader("Horas de Sono x Nota Final (Detalhado)")
                    plt.figure(figsize=(8, 5))
                    sns.scatterplot(data=df_limpo, x='Sleep_Hours_per_Night', y='Final_Score')
                    plt.title('Relação entre Horas de Sono X Nota Final')
                    plt.xlabel('Horas de Sono por Noite')
                    plt.ylabel('Nota Final')
                    st.pyplot(plt)

                st.subheader("Gráfico de Barras: Idade x Notas Intermediárias")
                fig2, ax2 = plt.subplots()
                ax2.bar(df_limpo['Age'], df_limpo['Midterm_Score'])
                ax2.set_title('Idade x Notas Intermediárias')
                ax2.set_xlabel('Idade')
                ax2.set_ylabel('Notas Intermediárias')
                st.pyplot(fig2)

                st.subheader("Gráfico de Pizza: Distribuição por Faixa Etária")
                faixas_etarias = [0, 17, 21, 24, 100]
                labels = ['Até 17 anos', '18 a 21 anos', '22 a 24 anos', '25 anos ou mais']
                df_limpo['Faixa_Etaria'] = pd.cut(df_limpo['Age'], bins=faixas_etarias, labels=labels)
                contagem = df_limpo['Faixa_Etaria'].value_counts()
                contagem = contagem[contagem > 0]

                fig3, ax3 = plt.subplots()
                ax3.pie(
                    contagem.values,
                    labels=contagem.index,
                    autopct='%1.1f%%',
                    startangle=90
                )
                ax3.set_title('Distribuição por Faixa Etária')
                ax3.axis('equal')

                faixas_ausentes = [label for label in labels if label not in contagem.index]
                if faixas_ausentes:
                    texto = (
                        'Não há registros para: '
                        + ', '.join(f'"{f}"' for f in faixas_ausentes)
                        + '.'
                    )
                    fig3.text(0.5, 0, texto, ha='center', fontsize=10, color='black')

                st.pyplot(fig3)
                log_acao("Gráficos gerados")
        else:
            with tab4:
                st.warning("Por favor, execute a limpeza de dados primeiro.")
else:
    st.info('Por favor, faça o upload de um arquivo CSV ou JSON para começar a análise.')  
