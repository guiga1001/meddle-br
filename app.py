import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Meddle BR", page_icon="🩺", layout="centered")

# LINKS DAS PLANILHAS
# 1. Link da aba principal (Calendário de jogos)
URL_JOGOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaYRZ8o_poW_YRuUke9vFxlmoezEp1S98ih7SCOeYgwzxlHMiJn9NcNrmXuLrkNC8ngnCb6Vth27PG/pub?output=csv"

# 2. Link da nova aba (Lista Geral de Doenças)
URL_LISTA_GERAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaYRZ8o_poW_YRuUke9vFxlmoezEp1S98ih7SCOeYgwzxlHMiJn9NcNrmXuLrkNC8ngnCb6Vth27PG/pub?gid=16863228&single=true&output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    # O comando 'sep=None' faz o Python descobrir sozinho se é vírgula ou ponto e vírgula
    df = pd.read_csv(url, sep=None, engine='python', encoding='utf-8')
    # Limpa espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip()
    return df

# Interface Visual
st.title("Meddle BR 🩺")
st.write("Analise as dicas e escolha a hipótese diagnóstica correta.")

try:
    # Carrega as duas tabelas
    df_jogos = load_data(URL_JOGOS)
    df_opcoes = load_data(URL_LISTA_GERAL)
    
    # Prepara a lista de sugestões (vem da aba 'lista_geral')
    # Assume que a coluna na sua nova aba também se chama 'doenca'
    lista_doencas_completa = sorted(df_opcoes['doenca'].unique().tolist())

    # Lógica da data de hoje
    hoje = datetime.now().strftime("%d/%m/%Y")
    df_jogos['data'] = df_jogos['data'].astype(str).str.strip()
    
    # Filtra o jogo de hoje
    jogo_hoje = df_jogos[df_jogos['data'] == hoje]

    if jogo_hoje.empty:
        st.warning(f"Nenhum caso clínico agendado para hoje ({hoje}).")
        st.info("Dica para o desenvolvedor: Verifique se a data na planilha está no formato DD/MM/AAAA e se o ano é 2026.")
    else:
        dados = jogo_hoje.iloc[0]
        solucao = dados['doenca'].strip()
        dicas = [dados['dica1'], dados['dica2'], dados['dica3'], dados['dica4'], dados['dica5'], dados['dica6']]

        # Controle de estado (sessão)
        if 'tentativas' not in st.session_state:
            st.session_state.tentativas = 0
        if 'terminou' not in st.session_state:
            st.session_state.terminou = False
        if 'venceu' not in st.session_state:
            st.session_state.venceu = False

        # Exibição das dicas liberadas
        st.divider()
        for i in range(st.session_state.tentativas + 1):
            if i < 6:
                st.info(f"**Dica {i+1}:** {dicas[i]}")

        # Interface de palpite
        if not st.session_state.terminou:
            # O selectbox agora usa a lista completa da nova aba
            palpite = st.selectbox("Selecione seu diagnóstico:", [""] + lista_doencas_completa, index=0)
            
            if st.button("Confirmar Hipótese"):
                if palpite == "":
                    st.warning("Selecione uma doença na lista!")
                elif palpite.strip() == solucao:
                    st.session_state.terminou = True
                    st.session_state.venceu = True
                    st.rerun()
                else:
                    st.session_state.tentativas += 1
                    if st.session_state.tentativas >= 6:
                        st.session_state.terminou = True
                        st.session_state.venceu = False
                    else:
                        st.error("Hipótese incorreta. Uma nova dica foi liberada!")
                    st.rerun()

        # Resultado Final
        if st.session_state.terminou:
            st.divider()
            if st.session_state.venceu:
                st.balloons()
                st.success(f"🔥 Sensacional! Você acertou: **{solucao}**")
                st.write(f"Você utilizou {st.session_state.tentativas + 1} dicas.")
            else:
                st.error(f"Esgotaram as tentativas! O diagnóstico era: **{solucao}**")
            
            st.write("Volte amanhã para um novo desafio clínico!")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
