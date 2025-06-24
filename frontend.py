import tkinter as tk
from tkinter import ttk, messagebox
from owlready2 import get_ontology, Thing, DataProperty, ObjectProperty

# Carrega a ontologia real
onto = get_ontology("ontology/amazing_videos_populated_v3.rdf").load()


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("IMDb Ontológico")
        self.master.geometry("950x700")

        self.titulos = list(onto.Titulo.instances())
        self.resultados = []

        for t in self.titulos:
            titulo = t.titulo if hasattr(t, 'titulo') and t.titulo else ''
            print(titulo)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Buscar Filme:").pack(pady=5)
        self.search_var = tk.StringVar()
        tk.Entry(self.master, textvariable=self.search_var, width=50).pack()

        tk.Button(self.master, text="Buscar", command=self.buscar_titulos).pack(pady=5)

        self.lista_titulos = tk.Listbox(self.master, width=120, height=10)
        self.lista_titulos.pack(pady=5)
        self.lista_titulos.bind("<<ListboxSelect>>", self.selecionar_titulo)

        self.frame_avaliacao = tk.LabelFrame(self.master, text="Avaliação do Filme")
        self.frame_avaliacao.pack(fill="both", expand=True, padx=10, pady=10)

        self.info_var = tk.StringVar()
        tk.Label(self.frame_avaliacao, textvariable=self.info_var, font=('Arial', 12, 'bold')).pack()

        self.avaliacoes_text = tk.Text(self.frame_avaliacao, height=10, width=115, bg="#f0f0f0")
        self.avaliacoes_text.pack(pady=5)
        self.avaliacoes_text.configure(state='disabled')

        # Formulário
        form = tk.Frame(self.frame_avaliacao)
        form.pack()

        tk.Label(form, text="Seu Nome:").grid(row=0, column=0, sticky='w')
        self.nome_usuario = tk.Entry(form, width=30)
        self.nome_usuario.grid(row=0, column=1)

        tk.Label(form, text="Nota (0 a 10):").grid(row=1, column=0, sticky='w')
        self.nota_usuario = ttk.Combobox(form, values=[i/2 for i in range(0, 21)], width=5)
        self.nota_usuario.grid(row=1, column=1)

        tk.Button(form, text="Enviar Avaliação", command=self.salvar_avaliacao).grid(row=2, column=1, pady=10)

    def buscar_titulos(self):
        termo = self.search_var.get().lower()
        self.lista_titulos.delete(0, tk.END)
        self.resultados = []

        for t in self.titulos:
            titulo = t.titulo if hasattr(t, 'titulo') and t.titulo else ''
            if termo in titulo.lower():
                self.lista_titulos.insert(tk.END, titulo)
                self.resultados.append(t)

    def selecionar_titulo(self, event):
        try:
            idx = self.lista_titulos.curselection()[0]
            self.titulo_selecionado = self.resultados[idx]
            self.exibir_detalhes()
        except:
            self.titulo_selecionado = None

    def exibir_detalhes(self):
        t = self.titulo_selecionado
        titulo = t.titulo if hasattr(t, 'titulo') else ''
        ano = t.ano if hasattr(t, 'ano') else ''
        media = t.nota_media if hasattr(t, 'nota_media') else 0
        votos = t.quantidade_votos if hasattr(t, 'quantidade_votos') else 0
        generos = ", ".join([g.nome_genero for g in t.tem_genero]) if hasattr(t, 'tem_genero') else ''

        self.info_var.set(f"{titulo} ({ano}) - {generos} | Média: {media:.2f} ★ | Votos: {votos}")

        # Mostrar avaliaões anteriores
        self.avaliacoes_text.configure(state='normal')
        self.avaliacoes_text.delete("1.0", tk.END)

        if hasattr(t, 'foi_avaliado_por'):
            for a in t.foi_avaliado_por:
                try:
                    nome = a.nome_avaliador[0]
                    nota = a.nota_usuario[0]
                    self.avaliacoes_text.insert(tk.END, f"{nome}: {nota} ★\n")
                except:
                    continue
        else:
            self.avaliacoes_text.insert(tk.END, "(Sem avaliações)\n")

        self.avaliacoes_text.configure(state='disabled')

    def salvar_avaliacao(self):
        if not hasattr(self, 'titulo_selecionado') or self.titulo_selecionado is None:
            messagebox.showerror("Erro", "Selecione um filme primeiro.")
            return

        nome = self.nome_usuario.get().strip()
        nota = self.nota_usuario.get()

        if not nome or not nota:
            messagebox.showerror("Erro", "Preencha nome e nota.")
            return

        nota = float(nota)

        # Criar ou encontrar usuário
        usuarios = list(onto.Usuario.instances())
        usuario = next((u for u in usuarios if u.nome_usuario[0] == nome), None)

        if not usuario:
            usuario = onto.Usuario()
            usuario.nome_usuario = [nome]

        # Criar avaliação
        nova_avaliacao = onto.Avaliacao()
        nova_avaliacao.nome_avaliador = [nome]
        nova_avaliacao.nota_usuario = [nota]
        nova_avaliacao.avaliador = usuario
        nova_avaliacao.filme_avaliado = self.titulo_selecionado

        # Atualizar nota média
        if not hasattr(self.titulo_selecionado, "nota_media"):
            self.titulo_selecionado.nota_media = [0.0]
        if not hasattr(self.titulo_selecionado, "quantidade_votos"):
            self.titulo_selecionado.quantidade_votos = [0]

        votos_atuais = self.titulo_selecionado.quantidade_votos[0]
        media_atual = self.titulo_selecionado.nota_media[0]

        nova_media = ((media_atual * votos_atuais) + nota) / (votos_atuais + 1)
        self.titulo_selecionado.nota_media = [nova_media]
        self.titulo_selecionado.quantidade_votos = [votos_atuais + 1]

        onto.save(file="ontology/amazing_videos_populated_v3.rdf", format="rdfxml")
        messagebox.showinfo("Sucesso", "Avaliação registrada!")
        self.nome_usuario.delete(0, tk.END)
        self.nota_usuario.set('')
        self.exibir_detalhes()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
