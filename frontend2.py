import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from owlready2 import get_ontology

# Carregar a ontologia
file_path = "ontology/amazing_videos_populated_v3.rdf"  # Altere o caminho para o arquivo correto
onto = get_ontology(file_path).load()

# Acessar instâncias da classe Filme
filmes = list(onto.Filme.instances())

# Imprimir informações de cada filme
for filme in filmes:
    titulo = filme.titulo_principal[0] if hasattr(filme, 'titulo_principal') else 'Sem título'
    ano = filme.ano_inicio[0] if hasattr(filme, 'ano_inicio') else 'Desconhecido'
    generos = filme.lista_generos[0] if hasattr(filme, 'lista_generos') else 'Desconhecido'
    duracao = filme.duracao_minutos[0] if hasattr(filme, 'duracao_minutos') else 'Desconhecida'
    print(f"Título: {titulo} | Ano: {ano} | Gêneros: {generos} | Duração: {duracao} min")

# Simulação de dados da ontologia
filmes = [
    {"id": "tt0111161", "titulo": "Um Sonho de Liberdade", "ano": 1994, "genero": "Drama", "duracao": 142},
    {"id": "tt0068646", "titulo": "O Poderoso Chefão", "ano": 1972, "genero": "Crime, Drama", "duracao": 175},
    {"id": "tt0468569", "titulo": "Batman: O Cavaleiro das Trevas", "ano": 2008, "genero": "Ação, Crime", "duracao": 152},
]

avaliacoes = []  # Armazena avaliações simuladamente

class AvaliadorFilmesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Avaliação de Filmes - Estilo IMDb")
        self.root.geometry("700x500")

        self.create_widgets()

    def create_widgets(self):
        # --- Campo de busca
        tk.Label(self.root, text="Buscar Filme:").pack(anchor='nw', padx=10, pady=5)
        self.search_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.search_var, width=40).pack(anchor='nw', padx=10)

        tk.Button(self.root, text="Buscar", command=self.buscar_filmes).pack(anchor='nw', padx=10, pady=5)

        # --- Lista de resultados
        self.resultado_lista = tk.Listbox(self.root, width=90, height=10)
        self.resultado_lista.pack(padx=10, pady=5)
        self.resultado_lista.bind('<<ListboxSelect>>', self.selecionar_filme)

        # --- Avaliação
        self.frame_avaliacao = tk.LabelFrame(self.root, text="Avaliar Filme Selecionado")
        self.frame_avaliacao.pack(fill="x", padx=10, pady=10)

        tk.Label(self.frame_avaliacao, text="Nota (1 a 10):").pack(anchor='w')
        self.nota = ttk.Combobox(self.frame_avaliacao, values=[str(i) for i in range(1, 11)], width=5)
        self.nota.pack(anchor='w')

        tk.Label(self.frame_avaliacao, text="Descrição da Avaliação:").pack(anchor='w')
        self.descricao_texto = tk.Text(self.frame_avaliacao, height=4, width=80)
        self.descricao_texto.pack()

        tk.Button(self.frame_avaliacao, text="Salvar Avaliação", command=self.salvar_avaliacao).pack(pady=5)

    def buscar_filmes(self):
        termo = self.search_var.get().lower()
        self.resultado_lista.delete(0, tk.END)
        for filme in filmes:
            if termo in filme["titulo"].lower():
                texto = f'{filme["titulo"]} ({filme["ano"]}) - {filme["genero"]} - {filme["duracao"]} min'
                self.resultado_lista.insert(tk.END, texto)

    def selecionar_filme(self, event):
        try:
            index = self.resultado_lista.curselection()[0]
            self.filme_selecionado = [f for f in filmes if f["titulo"] in self.resultado_lista.get(index)][0]
        except IndexError:
            self.filme_selecionado = None

    def salvar_avaliacao(self):
        if not hasattr(self, 'filme_selecionado') or not self.filme_selecionado:
            messagebox.showerror("Erro", "Selecione um filme primeiro.")
            return

        nota = self.nota.get()
        descricao = self.descricao_texto.get("1.0", tk.END).strip()

        if not nota:
            messagebox.showerror("Erro", "Insira uma nota entre 1 e 10.")
            return

        avaliacao = {
            "filme": self.filme_selecionado["titulo"],
            "nota": int(nota),
            "descricao": descricao
        }

        avaliacoes.append(avaliacao)
        messagebox.showinfo("Sucesso", f"Avaliação salva para o filme '{avaliacao['filme']}'.")

        self.descricao_texto.delete("1.0", tk.END)
        self.nota.set("")

# Execução do app
if __name__ == "__main__":
    root = tk.Tk()
    app = AvaliadorFilmesApp(root)
    root.mainloop()
