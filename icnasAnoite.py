import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Noite Aberta ICNAS - Torneio de Remates", page_icon="⚽", layout="centered")

FILE_PATH = "classificacao_icnas.csv"

# Função para carregar os dados existentes
def carregar_dados():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    else:
        return pd.DataFrame(columns=["Nome", "Remate 1", "Remate 2", "Remate 3", "Pontuação Total"])

# Inicializar o estado da sessão para os dados
if "df_leaderboard" not in st.session_state:
    st.session_state.df_leaderboard = carregar_dados()

st.title("⚽ ICNAS À NOITE ⚽")
st.subheader("Torneio de Penaltys")

# --- SECÇÃO 1: REGISTO DE NOVO PARTICIPANTE ---
st.header("📝 Próximo Participante")

# Usamos inputs normais em vez de um formulário estrito para permitir reatividade em tempo real
nome = st.text_input("Nome do Participante:", placeholder="Insira o nome aqui...", key="input_nome")

col1, col2, col3 = st.columns(3)
opcoes_pontos = [200, 500, 1000, -100]

with col1:
    r1 = st.selectbox("Remate 1:", opcoes_pontos, key="r1")
with col2:
    r2 = st.selectbox("Remate 2:", opcoes_pontos, key="r2")
with col3:
    r3 = st.selectbox("Remate 3:", opcoes_pontos, key="r3")

total_atual = r1 + r2 + r3

# Efeito visual de interatividade ("Subir na classificação em tempo real")
if nome.strip() != "":
    st.metric(label=f"Pontuação atual de {nome}", value=f"{total_atual} pts")
    
    # Criar uma simulação de onde esta pessoa ficaria na tabela neste exato momento
    df_simulado = st.session_state.df_leaderboard.copy()
    nova_linha_simulada = pd.DataFrame([{"Nome": f"⭐ {nome.strip()} (A jogar...)", "Pontuação Total": total_atual}])
    df_simulado = pd.concat([df_simulado, nova_linha_simulada], ignore_index=True)
    df_simulado = df_simulado.sort_values(by="Pontuação Total", ascending=False).reset_index(drop=True)
    df_simulado.index = df_simulado.index + 1
    
    posicao = df_simulado[df_simulado['Nome'].str.contains("A jogar...")].index[0]
    st.info(f"Projeção: {nome} está temporariamente em **{posicao}º lugar** da classificação!")

# Botão para fechar e salvar permanentemente a pontuação desta pessoa
if st.button("💾 Finalizar e Gravar Participante", type="primary"):
    if nome.strip() == "":
        st.error("Por favor, introduza um nome antes de gravar.")
    else:
        # Criar nova linha definitiva
        nova_linha = pd.DataFrame([{
            "Nome": nome.strip(),
            "Remate 1": r1,
            "Remate 2": r2,
            "Remate 3": r3,
            "Pontuação Total": total_atual
        }])
        
        # Atualizar DataFrame e gravar no CSV
        st.session_state.df_leaderboard = pd.concat([st.session_state.df_leaderboard, nova_linha], ignore_index=True)
        st.session_state.df_leaderboard.to_csv(FILE_PATH, index=False)
        st.success(f"Finalizado! Pontuação de {nome} guardada permanentemente.")
        # Pequeno truque para limpar o campo do nome para o próximo participante
        st.rerun()


# --- SECÇÃO 2: TABELA DE CLASSIFICAÇÃO EM TEMPO REAL ---
st.header("🏆 Classificação Geral")

if not st.session_state.df_leaderboard.empty:
    # Ordenar por Pontuação Total
    df_ordenado = st.session_state.df_leaderboard.sort_values(by="Pontuação Total", ascending=False).reset_index(drop=True)
    df_ordenado.index = df_ordenado.index + 1
    
    # Mostrar os líderes em destaque visual
    st.dataframe(df_ordenado[["Nome", "Pontuação Total"]], use_container_width=True)
    
    with st.expander("📊 Ver histórico detalhado de remates"):
        st.write(df_ordenado)
else:
    st.info("Ainda não há pontuações definitivas gravadas. Que comece o jogo!")


# --- SECÇÃO 3: ZONA DE GESTÃO DA ORGANIZAÇÃO (APAGAR ERROS) ---
st.markdown("---")
with st.expander("⚙️ Painel de Controlo da Organização (Apagar Participantes)"):
    if not st.session_state.df_leaderboard.empty:
        lista_nomes = st.session_state.df_leaderboard["Nome"].unique()
        participante_para_apagar = st.selectbox("Selecione o participante a remover por erro:", lista_nomes)
        
        if st.button("❌ Apagar Participante permanentemente", type="secondary"):
            # Filtrar o DataFrame para remover a pessoa selecionada
            st.session_state.df_leaderboard = st.session_state.df_leaderboard[
                st.session_state.df_leaderboard["Nome"] != participante_para_apagar
            ]
            # Guardar as alterações de volta no ficheiro CSV
            st.session_state.df_leaderboard.to_csv(FILE_PATH, index=False)
            st.warning(f"O participante '{participante_para_apagar}' foi removido com sucesso.")
            st.rerun()
    else:
        st.text("Nenhum participante registado para gerir.")