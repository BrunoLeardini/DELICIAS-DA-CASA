import io
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="DELÍCIAS DA CASA", page_icon="🥧", layout="centered")

# ================================
# CONFIGURAÇÕES INICIAIS
# ================================
# Agora temos produtos divididos em categorias
pizzas = {
    "P. Brócolis c/ Bacon": 45.00,
    "P. Calabresa": 45.00,
    "P. Frango Catupiry": 45.00,
    "P. Mussarela": 45.00,
    "P. Portuguesa": 45.00,
    "Combo Pizza": 80.00
}

tortas = {
    "Bombom Morango": 15.00,
    "Maracujá Trufado": 15.00,
    "Ninho com Uva": 15.00,
    "Limão": 15.00,
    "Choco Oreo": 15.00,
    "Torta inteira": 140.00
}

esfihas = {
    "E. Queijo": 5.00,
    "E. Carne": 5.00,
    "E. Frango Catupiry": 5.00,
    "E. Calabresa": 5.00,
    "E. Brócolis c/ Bacon": 5.00,
    "Combo Esfiha": 27.00
}

# Combina tudo para cálculo e gravação
sabores = {**pizzas, **tortas, **esfihas}

arquivo_excel = "pedidos_torteria.xlsx"

if not os.path.exists(arquivo_excel):
    df_init = pd.DataFrame(columns=[
        "Data", "Cliente", "Forma de Pagamento", "Sabor", "Quantidade", "Valor Unitário", "Valor Total"
    ])
    df_init.to_excel(arquivo_excel, index=False)

# ================================
# ESTADO DA SESSÃO
# ================================
if "pedido_atual" not in st.session_state:
    st.session_state.pedido_atual = {}
if "aba" not in st.session_state:
    st.session_state.aba = "Selecione"

# ================================
# SIDEBAR (PILLS)
# ================================
with st.sidebar:
    st.image("logo.jpeg")
    st.write("### Navegação")
    cols = st.columns(2)

    if cols[0].button("📋 Pedidos", use_container_width=True):
        st.session_state.aba = "Menu"
    if cols[1].button("📊 Relatório", use_container_width=True):
        st.session_state.aba = "Relatório"

# ================================
# AVISO QUANDO NENHUMA ABA ESCOLHIDA
# ================================
if st.session_state.aba == "Selecione":
    st.info("👈 Selecione uma opção na barra lateral para continuar.")
    st.stop()

# ================================
# ABA MENU
# ================================
if st.session_state.aba == "Menu":
    st.header("😋 Registre o pedido do Cliente")

    col1, col2 = st.columns(2)
    st.divider()

    # --- BLOCO DE SELEÇÃO DE PRODUTOS ---
    st.subheader("Selecione os produtos:")

    col_pizza, col_torta, col_esfiha = st.columns(3)

    with col_pizza:
        st.markdown("### 🍕 Pizzas")
        for sabor, preco in pizzas.items():
            if st.button(f"{sabor} - R$ {preco:.2f}", key=f"pizza_{sabor}"):
                st.session_state.pedido_atual[sabor] = st.session_state.pedido_atual.get(sabor, 0) + 1

    with col_torta:
        st.markdown("### 🥧 Tortas Doces")
        for sabor, preco in tortas.items():
            if st.button(f"{sabor} - R$ {preco:.2f}", key=f"torta_{sabor}"):
                st.session_state.pedido_atual[sabor] = st.session_state.pedido_atual.get(sabor, 0) + 1

    with col_esfiha:
        st.markdown("### 🥟 Esfihas")
        for sabor, preco in esfihas.items():
            if st.button(f"{sabor} - R$ {preco:.2f}", key=f"esfiha_{sabor}"):
                st.session_state.pedido_atual[sabor] = st.session_state.pedido_atual.get(sabor, 0) + 1

    # --- INGREDIENTES A RETIRAR / OBSERVAÇÕES ---
    if st.session_state.pedido_atual:
        st.subheader("⚙️ Observações do Pedido")

        # Campo para observações adicionais
        extra = st.text_input("Exemplo: 'Sem cebola', 'Sem Azeitona'")
        if extra:
            if "observacoes" not in st.session_state:
                st.session_state.observacoes = []
            if extra not in st.session_state.observacoes:
                st.session_state.observacoes.append(extra)

    # --- DADOS DO CLIENTE E PAGAMENTO ---
    with col1:
        cliente = st.text_input("👤 Nome do cliente:")

    with col2:
        forma_pagamento = st.selectbox(
            "💳 Forma de pagamento:",
            ["Selecione...", "Pix", "Dinheiro", "Cartão de crédito", "Cartão de débito"]
        )

    # --- RESUMO DO PEDIDO ---
if st.session_state.pedido_atual:

    st.divider()

    st.write("### 🧾 Pedido atual:")

    # Produtos
    st.write("**Produtos:**")
    total = 0
    for sabor, qtd in st.session_state.pedido_atual.items():
        valor = sabores[sabor] * qtd
        total += valor
        st.write(f"{sabor}: {qtd} unidade(s) — R$ {valor:.2f}")

    # Observações
    if "observacoes" in st.session_state and st.session_state.observacoes:
        st.write("**Observações:**")
        for obs in st.session_state.observacoes:
            st.write(f"- {obs}")
    
    st.write(f"**Total parcial: R$ {total:.2f}**")

    st.divider()

        # --- FINALIZAR PEDIDO ---
    if st.button("✅ Finalizar Pedido"):
        if not cliente or forma_pagamento == "Selecione...":
            st.warning("⚠️ Preencha o nome do cliente e a forma de pagamento antes de finalizar o pedido.")
        elif st.session_state.pedido_atual:
            df = pd.read_excel(arquivo_excel)
            data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Adiciona os registros na planilha
            for sabor, qtd in st.session_state.pedido_atual.items():
                valor_unit = sabores[sabor]
                valor_total = valor_unit * qtd
                obs = ", ".join(st.session_state.observacoes) if "observacoes" in st.session_state else ""
                novo = pd.DataFrame(
                    [[data, cliente, forma_pagamento, sabor, qtd, valor_unit, valor_total, obs]],
                    columns=df.columns.tolist() + ["Observações"] if "Observações" not in df.columns else df.columns
                )
                df = pd.concat([df, novo], ignore_index=True)

            df.to_excel(arquivo_excel, index=False)

            # Mostra mensagem de sucesso
            st.success(f"✅ Pedido registrado com sucesso para {cliente}!")
            st.balloons()

            # Mostra um compilado do pedido finalizado
            st.divider()
            st.write("### 🧾 COMANDA FINAL")
            st.write(f"**🕒 Data:** {data}")
            st.write(f"**👤 Cliente:** {cliente}")
            st.write(f"**💳 Pagamento:** {forma_pagamento}")

            st.write("**Produtos:**")
            total = 0
            for sabor, qtd in st.session_state.pedido_atual.items():
                valor = sabores[sabor] * qtd
                total += valor
                st.write(f"- {sabor}: {qtd} unidade(s) — R$ {valor:.2f}")

            if "observacoes" in st.session_state and st.session_state.observacoes:
                st.write("**Observações:**")
                for obs in st.session_state.observacoes:
                    st.write(f"- {obs}")

            st.write(f"**💰 Total: R$ {total:.2f}**")

            # Limpa dados da sessão
            st.session_state.pedido_atual = {}
            st.session_state.observacoes = []

        else:
            st.warning("Adicione pelo menos um item antes de finalizar o pedido.")

# ================================
# ABA RELATÓRIO
# ================================
elif st.session_state.aba == "Relatório":
    st.header("📊 Relatório de Vendas")

    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)

        if not df.empty:
            st.write("### 📄 Pedidos Registrados")

            # Mostrar tabela com botão de exclusão ao lado
            for i, row in df.iterrows():
                with st.expander(f"🧾 Pedido de {row['Cliente']} — {row['Data']}"):
                    st.write(f"**Sabor:** {row['Sabor']}")
                    st.write(f"**Quantidade:** {row['Quantidade']}")
                    st.write(f"**Valor Unitário:** R$ {row['Valor Unitário']:.2f}")
                    st.write(f"**Valor Total:** R$ {row['Valor Total']:.2f}")
                    st.write(f"**Forma de Pagamento:** {row['Forma de Pagamento']}")
                    if 'Observações' in df.columns and not pd.isna(row['Observações']):
                        st.write(f"**Observações:** {row['Observações']}")

                    # Botão para excluir o pedido específico
                    if st.button(f"🗑️ Excluir pedido {i+1}", key=f"excluir_{i}"):
                        df = df.drop(i)
                        df.reset_index(drop=True, inplace=True)
                        df.to_excel(arquivo_excel, index=False)
                        st.success(f"✅ Pedido de {row['Cliente']} excluído com sucesso!")
                        st.rerun()

            st.divider()

            # Resumo por sabor
            st.write("### 📊 Resumo por Sabor")
            resumo = df.groupby("Sabor")[["Quantidade", "Valor Total"]].sum().reset_index()
            st.dataframe(resumo, use_container_width=True)

            total_vendas = df["Valor Total"].sum()
            st.write(f"**💰 Valor total adquirido: R$ {total_vendas:.2f}**")

            # Download
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            st.download_button(
                "📥 Baixar planilha completa (.xlsx)",
                data=buffer.getvalue(),
                file_name="relatorio_torteria.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.divider()

            # 🧹 Botão para resetar dados do dia
            if st.button("🧹 Resetar dados do dia", use_container_width=True):
                df_vazio = pd.DataFrame(columns=[
                    "Data", "Cliente", "Forma de Pagamento",
                    "Sabor", "Quantidade", "Valor Unitário",
                    "Valor Total", "Observações"
                ])
                df_vazio.to_excel(arquivo_excel, index=False)
                st.session_state.clear()
                st.success("✅ Dados do dia resetados com sucesso!")
                st.balloons()
                st.rerun()
        else:
            st.info("📭 Nenhum pedido registrado ainda.")
    else:
        st.info("📭 Nenhum pedido encontrado.")
