import streamlit as st

st.set_page_config(page_title="FIFA 2001 Player Editor Pro", page_icon="⚽", layout="centered")

st.title("⚽ FIFA 2001 Advanced Player Editor")
st.write("Busca e edição binária de jogadores no arquivo `FCDB_ENG.DBI`.")

# 1. Upload do arquivo binário
uploaded_file = st.file_uploader("Selecione o arquivo FCDB_ENG.DBI", type=["dbi"])

if uploaded_file is not None:
    # Mantém os dados na sessão para evitar perda de alterações entre cliques
    if 'file_data' not in st.session_state or st.session_state.get('last_uploaded') != uploaded_file.name:
        st.session_state.file_data = bytearray(uploaded_file.read())
        st.session_state.last_uploaded = uploaded_file.name

    data = st.session_state.file_data
    
    st.success(f"Arquivo carregado! Tamanho total: `{len(data):,}` bytes.")
    st.divider()

    # 2. Configuração de Busca
    termo_busca = st.text_input("Digite o nome ou trecho do jogador para buscar:")

    if termo_busca:
        # Codifica para latin-1 (padrão em arquivos antigos de jogos de futebol)
        bytes_busca = termo_busca.encode("latin-1")
        
        # Encontra TODAS as ocorrências do termo no arquivo binário
        offsets_encontrados = []
        inicio = 0
        while True:
            pos = data.find(bytes_busca, inicio)
            if pos == -1:
                break
            offsets_encontrados.append(pos)
            inicio = pos + 1  # Avança para buscar próximas ocorrências

        if offsets_encontrados:
            st.info(f"Foram encontradas **{len(offsets_encontrados)}** ocorrências para '{termo_busca}'.")
            
            # Cria um seletor caso haja mais de um resultado para o mesmo nome
            opcoes_formatadas = [f"Offset: 0x{offset:08X} (Decimal: {offset})" for offset in offsets_encontrados]
            escolha_offset_str = st.selectbox("Selecione qual ocorrência deseja editar:", opcoes_formatadas)
            
            # Extrai o offset numérico da escolha
            indice_selecionado = opcoes_formatadas.index(escolha_offset_str)
            offset_escolhido = offsets_encontrados[indice_selecionado]

            st.divider()
            st.markdown(f"**Editando o registro no Offset Hexadecimal:** `0x{offset_escolhido:08X}`")

            # 3. Campo para o Novo Nome
            novo_nome = st.text_input("Digite o novo nome do jogador:", value=termo_busca)

            if st.button("💾 Aplicar Modificação Binária"):
                bytes_novos = novo_nome.encode("latin-1")
                tamanho_original = len(bytes_busca)
                
                if len(bytes_novos) > tamanho_original:
                    st.warning(f"⚠️ O novo nome é maior que o espaço reservado ({len(bytes_novos)} > {tamanho_original} bytes). Ele será cortado para evitar corromper o arquivo.")
                    bytes_finais = bytes_novos[:tamanho_original]
                else:
                    # Preenche o restante do espaço com bytes nulos (0x00) mantendo o alinhamento do FIFA
                    bytes_finais = bytes_novos.ljust(tamanho_original, b'\x00')

                # Aplica a alteração diretamente no buffer de bytes da memória
                data[offset_escolhido:offset_escolhido + tamanho_original] = bytes_finais
                st.session_state.file_data = data

                st.success(f"Sucesso! O bloco no offset `0x{offset_escolhido:08X}` foi atualizado.")

        else:
            st.error(f"Nenhuma ocorrência encontrada para '{termo_busca}'. Verifique letras maiúsculas/minúsculas.")

    st.divider()

    # 4. Botão de Download do Arquivo Editado
    st.download_button(
        label="📥 Baixar Arquivo DBI Modificado",
        data=bytes(st.session_state.file_data),
        file_name=uploaded_file.name,
        mime="application/octet-stream"
    )
    
