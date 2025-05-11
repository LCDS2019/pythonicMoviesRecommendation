from owlready2 import *
import pandas as pd

DATASET_DIRECTORY_PATH = "/media/orlando/another/imdb/"


class OntologiaIMDbPopulador:
    def __init__(self, onto, limit=100):
        self.onto = onto
        self.limit = limit
        self.basics = None
        self.akas = None
        self.ratings = None
        self.principals = None
        self.crew = None
        self.people = None

    def carregar_basics(self):
        self.basics = pd.read_csv(DATASET_DIRECTORY_PATH + "title.basics.tsv.gz", sep="\t", compression="gzip", na_values="\\N").head(self.limit)

    def carregar_akas(self):
        self.akas = pd.read_csv(DATASET_DIRECTORY_PATH + "title.akas.tsv.gz", sep="\t", compression="gzip", na_values="\\N")

    def carregar_ratings(self):
        self.ratings = pd.read_csv(DATASET_DIRECTORY_PATH + "title.ratings.tsv.gz", sep="\t", compression="gzip", na_values="\\N")

    def carregar_principals(self):
        self.principals = pd.read_csv(DATASET_DIRECTORY_PATH + "title.principals.tsv.gz", sep="\t", compression="gzip", na_values="\\N")

    def carregar_crew(self):
        self.crew = pd.read_csv(DATASET_DIRECTORY_PATH + "title.crew.tsv.gz", sep="\t", compression="gzip", na_values="\\N")

    def carregar_people(self):
        self.people = pd.read_csv(DATASET_DIRECTORY_PATH + "name.basics.tsv.gz", sep="\t", compression="gzip", na_values="\\N")

    def popular_basics(self):
        if self.basics is None:
            self.carregar_basics()
        for _, row in self.basics.iterrows():
            filme_ind = self.onto.Filme("filme_" + row["tconst"])
            filme_ind.id_titulo = row["tconst"]
            filme_ind.tipo_titulo = row["titleType"]
            filme_ind.titulo_principal = row["primaryTitle"]
            filme_ind.titulo_original = row["originalTitle"]
            filme_ind.eh_adulto = bool(row["isAdult"]) if pd.notna(row["isAdult"]) else False
            if pd.notna(row["startYear"]): filme_ind.ano_inicio = int(row["startYear"])
            if pd.notna(row["endYear"]): filme_ind.ano_fim = int(row["endYear"])
            if pd.notna(row["runtimeMinutes"]): filme_ind.duracao_minutos = int(row["runtimeMinutes"])
            filme_ind.lista_generos = row["genres"]

            if pd.notna(row["genres"]):
                for g in row["genres"].split(","):
                    genero_ind = self.onto.search_one(iri="*" + g.strip()) or self.onto.Genero(g.strip().replace(" ", "_"))
                    filme_ind.tem_genero.append(genero_ind)

    def popular_ratings(self):
        if self.ratings is None:
            self.carregar_ratings()
        for _, row in self.ratings.iterrows():
            filme = self.onto.search_one(id_titulo=row["tconst"])
            if filme:
                av = self.onto.Avaliacao("avaliacao_" + row["tconst"])
                av.id_titulo_avaliado = row["tconst"]
                av.nota_media = float(row["averageRating"])
                av.total_votos = int(row["numVotes"])
                filme.tem_avaliacao.append(av)

    def popular_crew(self):
        if self.crew is None:
            self.carregar_crew()
        for _, row in self.crew.iterrows():
            filme = self.onto.search_one(id_titulo=row["tconst"])
            if filme:
                filme.id_titulo_crew = row["tconst"]
                if pd.notna(row["directors"]): filme.lista_diretores = row["directors"]
                if pd.notna(row["writers"]): filme.lista_roteiristas = row["writers"]

    def popular_akas(self):
        if self.akas is None:
            self.carregar_akas()
        for _, row in self.akas.iterrows():
            filme = self.onto.search_one(id_titulo=row["titleId"])
            if filme:
                alt = self.onto.TituloAlternativo("aka_" + str(hash(row["title"])))
                alt.id_titulo_alternativo = row["titleId"]
                alt.ordem = int(row["ordering"])
                alt.nome_titulo = row["title"]
                if pd.notna(row["region"]): alt.regiao = row["region"]
                if pd.notna(row["language"]): alt.idioma = row["language"]
                if pd.notna(row["types"]): alt.tipos = row["types"]
                if pd.notna(row["attributes"]): alt.atributos = row["attributes"]
                alt.eh_titulo_original = bool(row["isOriginalTitle"])
                filme.tem_titulo_alternativo.append(alt)

    def popular_principals(self):
        if self.principals is None:
            self.carregar_principals()
        if self.people is None:
            self.carregar_people()
        for _, p in self.principals.iterrows():
            filme = self.onto.search_one(id_titulo=p["tconst"])
            if filme:
                papel = self.onto.PapelPrincipal("papel_" + p["nconst"] + "_" + p["tconst"])
                papel.id_titulo_papel = p["tconst"]
                papel.ordem_credito = int(p["ordering"])
                papel.id_pessoa = p["nconst"]
                if pd.notna(p["category"]): papel.categoria = p["category"]
                if pd.notna(p["job"]): papel.trabalho = p["job"]
                if pd.notna(p["characters"]): papel.personagens = p["characters"]
                pessoa_ind = self.onto.search_one(iri="*" + p["nconst"])
                if not pessoa_ind:
                    pessoa_ind = self.onto.Pessoa("pessoa_" + p["nconst"])
                    pessoa_data = self.people[self.people["nconst"] == p["nconst"]]
                    if not pessoa_data.empty:
                        pessoa_data = pessoa_data.iloc[0]
                        pessoa_ind.nome = pessoa_data["primaryName"]
                        if pd.notna(pessoa_data["birthYear"]): pessoa_ind.ano_nascimento = int(pessoa_data["birthYear"])
                        if pd.notna(pessoa_data["deathYear"]): pessoa_ind.ano_falecimento = int(pessoa_data["deathYear"])
                        if pd.notna(pessoa_data["primaryProfession"]): pessoa_ind.profissoes_principais = pessoa_data["primaryProfession"]
                        if pd.notna(pessoa_data["knownForTitles"]): pessoa_ind.titulos_conhecidos = pessoa_data["knownForTitles"]
                papel.representado_por = pessoa_ind
                filme.tem_papel_principal.append(papel)
