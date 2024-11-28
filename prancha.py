import streamlit as st
import pandas as pd
import io

# Título da aplicação
st.title("Gestão de Solicitações de Caminhões Pranchas")

# Upload do arquivo pelo usuário
uploaded_file = st.sidebar.file_uploader("Faça o upload do arquivo Excel:", type=["xlsx"])

if uploaded_file:
    try:
        # Ler o arquivo Excel enviado
        data = pd.read_excel(uploaded_file)

        # Selecionar as colunas de interesse
        selected_columns = [
            "objectid", "menu", "data_", "colaborador_responsavel", 
            "equipamento", "qnt_equipamento", "cc_modulo", "quantidade", 
            "eixos", "solicitacao", "data_reserva", "hora_reserva", 
            "fazenda_origem", "fazenda_destino"
        ]

        # Verificar se as colunas existem no DataFrame
        missing_columns = [col for col in selected_columns if col not in data.columns]
        if missing_columns:
            st.error(f"As seguintes colunas estão ausentes no arquivo: {', '.join(missing_columns)}")
        else:
            # Trabalhar apenas com as colunas de interesse
            data = data[selected_columns]

            # Converter a coluna `objectid` para tipo `object`
            data["objectid"] = data["objectid"].astype(str)

            # Filtros dinâmicos na barra lateral
            st.sidebar.header("Filtros")

            # Filtro por data
            data["data_reserva"] = pd.to_datetime(data["data_reserva"])
            selected_date = st.sidebar.date_input("Filtrar por Data (data_reserva):", value=None)
            if selected_date:
                data = data[data["data_reserva"].dt.date == selected_date]

            # Filtro por colaborador
            selected_colaborador = st.sidebar.multiselect(
                "Filtrar por Colaborador (colaborador_responsavel):",
                options=data["colaborador_responsavel"].unique(),
            )
            if selected_colaborador:
                data = data[data["colaborador_responsavel"].isin(selected_colaborador)]

            # Filtro por equipamento
            selected_equipamento = st.sidebar.multiselect(
                "Filtrar por Equipamento (equipamento):",
                options=data["equipamento"].unique(),
            )
            if selected_equipamento:
                data = data[data["equipamento"].isin(selected_equipamento)]

            # Filtro por fazenda de origem
            selected_fazenda_origem = st.sidebar.multiselect(
                "Filtrar por ID (objectid):",
                options=data["objectid"].unique(),
            )
            if selected_fazenda_origem:
                data = data[data["objectid"].isin(selected_fazenda_origem)]

            # Filtro por fazenda de destino
            selected_fazenda_destino = st.sidebar.multiselect(
                "Filtrar por Setor(menu):",
                options=data["menu"].unique(),
            )
            if selected_fazenda_destino:
                data = data[data["menu"].isin(selected_fazenda_destino)]

            # Exibir os dados filtrados
            st.write("### Dados Filtrados")
            st.dataframe(data)

            # Botão para exportar os dados
            if st.sidebar.button("Exportar para Excel"):
                output = io.BytesIO()
                data.to_excel(output, index=False)

                # Botão de download
                st.download_button(
                    label="Baixar Excel",
                    data=output.getvalue(),
                    file_name="dados_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado no caminho: {file_path}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")
