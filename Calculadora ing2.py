import sqlite3
import streamlit as st


# 1. CHAMADA OBRIGATÓRIA NO TOPO:
def inicialzador_banco():
    conn = sqlite3.connect('calculadora.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingredientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco_total REAL NOT NULL,
    qtd_total REAL NOT NULL
    )''')
    conn.commit()
    conn.close()


inicialzador_banco()

# --- MEMÓRIA DA RECEITA (Corrigido para usar sempre underline) ---
if 'carrinho_receita' not in st.session_state:
    st.session_state.carrinho_receita = []


# --- FUNÇÃO PARA BUSCAR DADOS ---
def buscar_ingredientes():
    conn = sqlite3.connect('calculadora.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome, preco_total, qtd_total FROM ingredientes")
    dados = cursor.fetchall()
    conn.close()
    return dados


# --- FORMULÁRIO DE CADASTRO NA BARRA LATERAL ---
with st.sidebar:
    st.header("📦 Cadastrar Ingredientes")
    novo_nome = st.text_input("Nome do Ingrediente")
    novo_preco = st.number_input("Preço do Pacote (R$)", min_value=0.0, step=0.10)
    nova_qtd = st.number_input("Quantidade Total (g ou ml)", min_value=1.0, step=10.0)

    if st.button("Salvar no Banco"):
        if novo_nome:
            conn = sqlite3.connect('calculadora.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ingredientes (nome, preco_total, qtd_total) VALUES (?, ?, ?)",
                           (novo_nome.strip(), novo_preco, nova_qtd))
            conn.commit()
            conn.close()
            st.success(f"{novo_nome} salvo!")
            st.rerun()
        else:
            st.error("Digite um nome!")

# --- INTERFACE PRINCIPAL ---
st.header("🍎 Montar Nova Receita")

opcoes = buscar_ingredientes()
nomes_ingredientes = [item[0] for item in opcoes]

if not nomes_ingredientes:
    st.warning("Cadastre ingredientes na barra lateral primeiro!")
else:
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        selecionado = st.selectbox("Escolha o ingrediente", nomes_ingredientes)
    with col2:
        quantidade_usada = st.number_input("Qtd usada (g/ml)", min_value=0.0, step=1.0)
    with col3:
        st.write("")  # Espaçador
        if st.button("Adicionar"):
            dados_ing = next(item for item in opcoes if item[0] == selecionado)
            nome, preco_total, qtd_total = dados_ing
            # Linha de DEBUG
            print(f">>> DEBUG: {nome} | preço: {preco_total} | qtd Total: {qtd_total} | Usada: {quantidade_usada}")
            if qtd_total > 0:
                custo_proporcional = (preco_total / qtd_total) * quantidade_usada
            else:
                custo_proporcional = 0.0
                st.error(f"Erro: A quantidade total de {nome} no banco está como ZERO.")

            st.session_state.carrinho_receita.append({
                "nome": nome,
                "quantidade": quantidade_usada,
                "custo": custo_proporcional
            })

# --- LISTAGEM DE ITENS (Fora do bloco de cálculo) ---
st.subheader("Itens da Receita")
total_custo_ingredientes = 0

for item in st.session_state.carrinho_receita:
    st.write(f"✅ {item['nome']} - {item['quantidade']}g/ml : **R$ {item['custo']:.2f}**")
    total_custo_ingredientes += item['custo']

st.divider()

# --- FECHAMENTO DO PRODUTO (Agora fora do loop!) ---
if total_custo_ingredientes > 0:
    st.subheader("📊 Fechamento do Produto")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        rendimento = st.number_input("Rendimento da receita (unidades)", min_value=1, value=1)
    with col_r2:
        margem = st.number_input("Margem de Lucro (%)", min_value=0, value=100)

    custo_por_unidade = total_custo_ingredientes / rendimento
    preco_venda_unidade = custo_por_unidade * (1 + margem / 100)

    c1, c2, c3 = st.columns(3)
    c1.metric("Custo Total", f"R$ {total_custo_ingredientes:.2f}")
    c2.metric("Custo / Unidade", f"R$ {custo_por_unidade:.2f}")
    c3.metric("Sugestão de Venda", f"R$ {preco_venda_unidade:.2f}")

    if st.button("Limpar Receita"):
        st.session_state.carrinho_receita = []
        st.rerun()

st.divider() #Cria uma linha divisoria para separar do resto
if st.button("Resetar todos os Ingredientes"):
    conn = sqlite3.connect('calculadora.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingredientes")
    conn.commit()
    conn.close()
    st.success("Banco de dados limpo! Agora você pode cadastrar os valores corretos.")
    st.session_state.carrinho_receita = [] # Limpa a receita atual tambem
    st.rerun()














