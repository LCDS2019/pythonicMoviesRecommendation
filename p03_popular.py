import datetime
start = datetime.datetime.now()

import os
os.system('clear')

################################################################################

import pandas as pd
import random
from owlready2 import *

################################################################################

print(' Ontology load '.center(80,'#'))

# Certifique-se de usar a versão corrigida da ontologia
onto = get_ontology('./ontology/amazing_videos_p03.rdf').load()

print("Classes existentes:")
for cls in onto.classes():
    print(f"- {cls.name}")

################################################################################

def read_first_n_rows_tsv(filename, n=50):
    chunk_size = 1000
    selected_rows = []

    for chunk in pd.read_csv(filename, sep='\t', dtype=str, na_values='\\N', chunksize=chunk_size):
        valid_chunk = chunk.dropna(how='all')  
        selected_rows.extend(valid_chunk.to_dict(orient='records'))

        if len(selected_rows) >= n:
            break

    return pd.DataFrame(selected_rows[:n])

def limpar_nome(titulo):
    return titulo.strip().lower().replace(" ", "_").replace(":", "").replace(".", "").replace(",", "").replace("'", "").replace('"', "")

################################################################################

# Lendo os dados
df_names = read_first_n_rows_tsv('dados/name.basics.tsv', n=1000)
df_titles = read_first_n_rows_tsv('dados/title.basics.tsv', n=1000)
df_ratings = read_first_n_rows_tsv('dados/title.ratings.tsv', n=1000)
df_principals = read_first_n_rows_tsv('dados/title.principals.tsv', n=1000)
df_crew = read_first_n_rows_tsv('dados/title.crew.tsv', n=1000)

# Convertendo tipos
df_ratings['averageRating'] = df_ratings['averageRating'].astype(float)
df_ratings['numVotes'] = df_ratings['numVotes'].astype(int)

# Extraindo listas de papéis
lista_atores = df_principals[df_principals['category'].isin(['actor', 'actress'])]['nconst'].unique()
lista_diretores = df_crew['directors'].dropna().str.split(',').explode().unique()

# Amostra de usuários
todos_ids = set(df_names['nconst'])
ids_utilizados = set(lista_atores).union(set(lista_diretores))
lista_usuarios = list(todos_ids - ids_utilizados)
amostra_usuarios = pd.Series(lista_usuarios).sample(frac=0.1, random_state=42).tolist()

# Lista de nomes comuns brasileiros
nomes_comuns = ["Ana", "Carlos", "Fernanda", "Bruno", "Juliana", "Lucas", "Mariana", "Felipe", "Camila", "Rodrigo"]

################################################################################

# Criar instâncias de Pessoa, Ator, Diretor ou Usuario
usuario_index = 0
for _, row in df_names.iterrows():
    nconst = row['nconst']

    if nconst in lista_atores:
        pessoa = onto.Ator(f"ator_{nconst}")
    elif nconst in lista_diretores:
        pessoa = onto.Diretor(f"diretor_{nconst}")
    elif nconst in amostra_usuarios:
        pessoa = onto.Usuario(f"usuario_{nconst}")
        pessoa.nome = nomes_comuns[usuario_index % len(nomes_comuns)]
        usuario_index += 1
    else:
        continue

    if pd.notna(row['primaryName']) and nconst not in amostra_usuarios:
        pessoa.nome = row['primaryName']
    if pd.notna(row['birthYear']) and row['birthYear'].isdigit():
        pessoa.ano_nascimento = int(row['birthYear'])
    if pd.notna(row['deathYear']) and row['deathYear'].isdigit():
        pessoa.ano_morte = int(row['deathYear'])

################################################################################

# Criar instâncias de Titulo e seus gêneros
for _, row in df_titles.iterrows():
    titulo = onto.Titulo(f"titulo_{row['tconst']}")

    if pd.notna(row['primaryTitle']):
        titulo.titulo = row['primaryTitle']
    if pd.notna(row['startYear']) and row['startYear'].isdigit():
        titulo.ano = int(row['startYear'])

    if pd.notna(row['genres']):
        for g in row['genres'].split(','):
            nome_genero = g.strip().lower().replace(" ", "_")
            genero = onto.search_one(nome_genero=g.strip())
            if not genero:
                genero = onto.Genero(f"genero_{nome_genero}")
                genero.nome_genero = g.strip()
            titulo.tem_genero.append(genero)

################################################################################

# Associar notas aos títulos
for _, row in df_ratings.iterrows():
    if pd.isna(row['tconst']):
        continue

    titulo = onto.search_one(iri="*titulo_" + row['tconst'])

    if titulo and pd.notna(row['averageRating']):
        titulo.nota = row['averageRating']
        titulo.nota_media = row['averageRating']

    if titulo and pd.notna(row['numVotes']):
        titulo.quantidade_votos = row['numVotes']
        titulo.total_votos = row['numVotes']

    if titulo and hasattr(titulo, "titulo"):
        nome_limpo = limpar_nome(titulo.titulo[0])
        novo_nome = f"{nome_limpo}_{row['tconst']}"
        titulo.name = novo_nome

################################################################################

# Criar avaliações simuladas de usuários
usuarios = list(onto.Usuario.instances())
titulos = list(onto.Titulo.instances())

for usuario in usuarios:
    filmes_assistidos = random.sample(titulos, k=3)

    for filme in filmes_assistidos:
        avaliacao = onto.Avaliacao(f"avaliacao_{usuario.name}_{filme.name}")
        avaliacao.avaliador = usuario
        avaliacao.filme_avaliado = filme
        nota = round(random.uniform(6.0, 10.0), 1)
        avaliacao.nota_usuario = nota

        usuario.realizou_avaliacao.append(avaliacao)
        filme.tem_avaliacao.append(avaliacao)

################################################################################

# Salvar a ontologia populada
onto.save(file="./ontology/amazing_videos_populated_v3.rdf", format="rdfxml")
onto.save(file="./ontology/amazing_videos_populated_v3.ttl", format="ntriples")
print('\nOntologia salva como "amazing_videos_populated_v3.rdf"\n')

################################################################################

end = datetime.datetime.now()
time = end - start

hour = str(time.seconds // 3600).zfill(2)
min = str((time.seconds % 3600) // 60).zfill(2)
sec = str(time.seconds % 60).zfill(2)

msg_time = f' Time:{hour}:{min}:{sec} '
print(msg_time.center(80, '#'))

################################################################################
