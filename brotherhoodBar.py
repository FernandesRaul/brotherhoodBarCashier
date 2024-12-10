import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from openpyxl import Workbook, load_workbook
import os

# Configuração dos arquivos
DADOS_FILE = "dados.xlsx"


# Inicializar os arquivos necessários
def inicializar_arquivos():
    if not os.path.exists(DADOS_FILE):
        wb = Workbook()
        estoque_ws = wb.create_sheet("estoque")
        vendas_ws = wb.create_sheet("vendas")

        # Configuração da aba "estoque"
        estoque_ws.append(["ID", "Produto", "Preço", "Quantidade"])

        # Configuração da aba "vendas"
        vendas_ws.append(["ID Venda", "Produto", "Quantidade", "Preço Total", "Forma de Pagamento", "Troco"])

        wb.save(DADOS_FILE)


# Função para limpar e exibir novos conteúdos
def exibir_conteudo(funcao):
    for widget in frame_conteudo.winfo_children():
        widget.destroy()
    funcao()


# Função Tela Inicial
def tela_inicial():
    background_label = tk.Label(frame_conteudo, image=background_image, bg="black")
    background_label.place(relwidth=1, relheight=1)
    tk.Label(frame_conteudo, text="- BROTHERHOOD MC -\n WE ARE DISEASE UPON THE WORLD!", font=("Arial", 24, "bold"),
             fg="white", bg="black").pack(pady=50)


# Função de Caixa
def caixa():
    tk.Label(frame_conteudo, text="Caixa", font=("Arial", 20, "bold"), fg="white", bg="black").grid(row=0, column=0,
                                                                                                    pady=20,
                                                                                                    columnspan=2)

    wb = load_workbook(DADOS_FILE)
    estoque_ws = wb["estoque"]

    produtos = {}
    for row in estoque_ws.iter_rows(min_row=2, values_only=True):
        produto, preco, quantidade = row[1], row[2], row[3]
        produtos[produto] = {"preco": preco, "quantidade": quantidade}

    selected_produto = tk.StringVar()
    selected_quantidade = tk.IntVar(value=1)

    def atualizar_valor_a_ser_pago():
        produto_selecionado = selected_produto.get()
        quantidade_selecionada = selected_quantidade.get()

        preco_produto = produtos.get(produto_selecionado, {}).get("preco", 0)
        total = preco_produto * quantidade_selecionada

        valor_a_ser_pago_var.set(f"R${total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def confirmar_venda():
        produto_selecionado = selected_produto.get()
        quantidade_selecionada = selected_quantidade.get()
        preco_produto = produtos.get(produto_selecionado, {}).get("preco", 0)
        quantidade_produto = produtos.get(produto_selecionado, {}).get("quantidade", 0)

        if quantidade_produto >= quantidade_selecionada:
            produtos[produto_selecionado]["quantidade"] -= quantidade_selecionada
            wb.save(DADOS_FILE)  # Atualizar o estoque
            messagebox.showinfo("Venda Efetuada", "Venda efetuada com sucesso!", icon='info')
        else:
            messagebox.showwarning("Sem Estoque", f"O produto {produto_selecionado} está fora de estoque.")

    # Seleção de produtos para venda
    tk.Label(frame_conteudo, text="Selecione o Produto", fg="white", bg="black").grid(row=1, column=0, sticky="w",
                                                                                      padx=20)
    produto_dropdown = ttk.Combobox(frame_conteudo, textvariable=selected_produto, values=list(produtos.keys()))
    produto_dropdown.grid(row=1, column=1, padx=20, pady=5)

    # Quantidade
    tk.Label(frame_conteudo, text="Quantidade", fg="white", bg="black").grid(row=2, column=0, sticky="w", padx=20)
    quantidade_dropdown = ttk.Combobox(frame_conteudo, textvariable=selected_quantidade,
                                       values=[str(i) for i in range(1, 11)])
    quantidade_dropdown.grid(row=2, column=1, padx=20, pady=5)

    # Atualizar valor a ser pago automaticamente
    valor_a_ser_pago_var = tk.StringVar()
    valor_a_ser_pago_var.set("R$0,00")
    tk.Label(frame_conteudo, text="Valor a ser Pago", fg="white", bg="black").grid(row=3, column=0, sticky="w", padx=20)
    valor_a_ser_pago_entry = tk.Entry(frame_conteudo, textvariable=valor_a_ser_pago_var, font=("Arial", 14),
                                      state="readonly")
    valor_a_ser_pago_entry.grid(row=3, column=1, padx=20, pady=5)

    # Calcular valor ao selecionar o produto e quantidade
    selected_produto.trace("w", lambda *args: atualizar_valor_a_ser_pago())
    selected_quantidade.trace("w", lambda *args: atualizar_valor_a_ser_pago())

    # Forma de pagamento
    tk.Label(frame_conteudo, text="Forma de Pagamento", fg="white", bg="black").grid(row=4, column=0, sticky="w",
                                                                                     padx=20)
    pagamento_var = tk.StringVar(value="Dinheiro")
    pagamento_dropdown = ttk.Combobox(frame_conteudo, textvariable=pagamento_var,
                                      values=["Dinheiro", "Débito", "Crédito", "Pix"])
    pagamento_dropdown.grid(row=4, column=1, padx=20, pady=5)

    # Função para calcular troco
    def calcular_troco():
        try:
            produto_selecionado = selected_produto.get()
            quantidade_selecionada = selected_quantidade.get()

            preco_produto = produtos.get(produto_selecionado, {}).get("preco", 0)
            total_produto = preco_produto * quantidade_selecionada

            # Pop-up para valor recebido
            valor_recebido = simpledialog.askfloat("Valor Recebido", "Digite o valor recebido:", parent=root,
                                                   minvalue=0)
            if valor_recebido is not None:
                troco = valor_recebido - total_produto
                if troco >= 0:
                    messagebox.showinfo("Troco",
                                        f"Troco: R${troco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                else:
                    messagebox.showwarning("Pagamento Insuficiente", "O valor recebido é menor que o preço do produto.")
        except ValueError:
            pass

    # Exibir/ocultar o botão de calcular troco dependendo da forma de pagamento
    def atualizar_calculo_troco(*args):
        if pagamento_var.get() == "Dinheiro":
            calcular_troco_button.grid(row=5, column=0, pady=10, columnspan=2)
        else:
            calcular_troco_button.grid_forget()

    pagamento_var.trace("w", atualizar_calculo_troco)

    calcular_troco_button = tk.Button(frame_conteudo, text="Calcular Troco", command=calcular_troco, bg="#e60000",
                                      fg="white")
    calcular_troco_button.grid(row=5, column=0, pady=10, columnspan=2)

    # Confirmar venda
    tk.Button(frame_conteudo, text="Confirmar Venda", command=confirmar_venda, bg="#e60000", fg="white").grid(row=6,
                                                                                                              column=0,
                                                                                                              pady=10,
                                                                                                              columnspan=2)


# Função de Verificação do Estoque
def verificar_estoque():
    tk.Label(frame_conteudo, text="Verificação do Estoque", font=("Arial", 20, "bold"), fg="white", bg="black").pack(
        pady=20)

    tree = ttk.Treeview(frame_conteudo, columns=("Produto", "Preço", "Quantidade"), show="headings")
    tree.heading("Produto", text="Produto")
    tree.heading("Preço", text="Preço")
    tree.heading("Quantidade", text="Quantidade")

    # Ajuste do design da Treeview
    tree.tag_configure("evenrow", background="#444")
    tree.tag_configure("oddrow", background="#222")

    wb = load_workbook(DADOS_FILE)
    estoque_ws = wb["estoque"]

    for i, row in enumerate(estoque_ws.iter_rows(min_row=2, values_only=True)):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", tk.END, values=(row[1], f"R${row[2]:,.2f}", row[3]), tags=(tag,))

    tree.pack(expand=True, fill="both", padx=20, pady=10)


# Função de Inserir no Estoque
def inserir_estoque():
    tk.Label(frame_conteudo, text="Inserir no Estoque", font=("Arial", 20, "bold"), fg="white", bg="black").pack(
        pady=20)

    # Inputs
    tk.Label(frame_conteudo, text="Produto", fg="white", bg="black").pack(anchor="w", padx=20)
    produto_var = tk.StringVar()
    tk.Entry(frame_conteudo, textvariable=produto_var, font=("Arial", 14)).pack(fill="x", padx=20, pady=5)

    tk.Label(frame_conteudo, text="Preço (R$)", fg="white", bg="black").pack(anchor="w", padx=20)
    preco_var = tk.StringVar()
    tk.Entry(frame_conteudo, textvariable=preco_var, font=("Arial", 14)).pack(fill="x", padx=20, pady=5)

    tk.Label(frame_conteudo, text="Quantidade", fg="white", bg="black").pack(anchor="w", padx=20)
    quantidade_var = tk.StringVar()
    tk.Entry(frame_conteudo, textvariable=quantidade_var, font=("Arial", 14)).pack(fill="x", padx=20, pady=5)

    def adicionar_produto():
        produto = produto_var.get()
        preco = float(preco_var.get().replace("R$", "").replace(",", "."))
        quantidade = int(quantidade_var.get())

        wb = load_workbook(DADOS_FILE)
        estoque_ws = wb["estoque"]
        estoque_ws.append([estoque_ws.max_row, produto, preco, quantidade])
        wb.save(DADOS_FILE)

        messagebox.showinfo("Produto Adicionado", f"{produto} adicionado ao estoque!")

    tk.Button(frame_conteudo, text="Adicionar Produto", command=adicionar_produto, bg="#e60000", fg="white").pack(
        pady=20)


# Função de Auditoria (Exibição de Vendas e Relatório de Balanço)
def auditoria():
    tk.Label(frame_conteudo, text="Auditoria", font=("Arial", 20, "bold"), fg="white", bg="black").pack(pady=20)

    tree = ttk.Treeview(frame_conteudo, columns=("Produto", "Quantidade", "Preço Total", "Forma de Pagamento", "Troco"),
                        show="headings")
    tree.heading("Produto", text="Produto")
    tree.heading("Quantidade", text="Quantidade")
    tree.heading("Preço Total", text="Preço Total")
    tree.heading("Forma de Pagamento", text="Forma de Pagamento")
    tree.heading("Troco", text="Troco")

    wb = load_workbook(DADOS_FILE)
    vendas_ws = wb["vendas"]

    for row in vendas_ws.iter_rows(min_row=2, values_only=True):
        tree.insert("", tk.END, values=row[1:], tags=("oddrow",))

    tree.pack(expand=True, fill="both", padx=20, pady=10)


# Interface Principal
root = tk.Tk()
root.title("Gestão de Bar")
root.geometry("1200x800")
root.configure(bg="black")

# Estilo
style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview", background="#333", fieldbackground="#333", foreground="white")
style.configure("Treeview.Heading", background="#444", foreground="white", font=("Arial", 12, "bold"))

# Layout
frame_menu = tk.Frame(root, bg="#111", width=250)
frame_menu.pack(side="left", fill="y")

frame_conteudo = tk.Frame(root, bg="black")
frame_conteudo.pack(side="right", expand=True, fill="both")

# Imagem de Fundo
background_image = ImageTk.PhotoImage(Image.open("background.jpeg").resize((800, 800)))

# Botões do Menu
menu_botoes = [
    {"text": "Tela Inicial", "command": lambda: exibir_conteudo(tela_inicial)},
    {"text": "Caixa", "command": lambda: exibir_conteudo(caixa)},
    {"text": "Estoque", "command": lambda: exibir_conteudo(verificar_estoque)},
    {"text": "Adicionar Estoque", "command": lambda: exibir_conteudo(inserir_estoque)},
    {"text": "Auditoria", "command": lambda: exibir_conteudo(auditoria)},
]

for botao in menu_botoes:
    tk.Button(frame_menu, text=botao["text"], command=botao["command"], bg="#e60000", fg="white",
              font=("Arial", 12, "bold")).pack(fill="x", pady=10, padx=10)

# Inicializar arquivos e exibir tela inicial
inicializar_arquivos()
tela_inicial()

root.mainloop()
