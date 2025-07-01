import datetime
start = datetime.datetime.now()

import os
os.system('clear')

################################################################################

import pandas as pd
from owlready2 import *

################################################################################

print(' Ontology load '.center(80, '#'))

onto = get_ontology('./ontology/amazing_videos_p04.rdf').load()

################################################################################

def read_first_n_rows_tsv(filename, n=1000):
    chunk_size = 500
    selected_rows = []

    for chunk in pd.read_csv(filename, sep='\t', dtype=str, na_values='\\N', chunksize=chunk_size):
        valid_chunk = chunk.dropna(how='all')  
        selected_rows.extend(valid_chunk.to_dict(orient='records'))

        if len(selected_rows) >= n:
            break

    return pd.DataFrame(selected_rows[:n])

def limpar_nome(texto):
    return texto.strip().lower().replace(" ", "_").replace(":", "").replace(".", "").replace(",", "").replace("'", "").replace('"', "")

################################################################################

# Carregando os dados necessários
df_titles = read_first_n_rows_tsv('dados/title.basics.tsv', n=500)
df_principals = read_first_n_rows_tsv('dados/title.principals.tsv', n=500)
df_crew = read_first_n_rows_tsv('dados/title.crew.tsv', n=500)
df_ratings = read_first_n_rows_tsv('dados/title.ratings.tsv', n=500)

# Conversões
df_ratings['averageRating'] = df_ratings['averageRating'].astype(float)

# Mapeamentos
principals_filtrados = df_principals[df_principals['category'].isin(['actor', 'actress'])]
atores_principais = principals_filtrados.sort_values('ordering').drop_duplicates('tconst', keep='first')
map_ator = dict(zip(atores_principais['tconst'], atores_principais['nconst']))

df_crew['directors'] = df_crew['directors'].fillna("")
map_diretor = df_crew.set_index('tconst')['directors'].to_dict()
map_rating = df_ratings.set_index('tconst')['averageRating'].to_dict()

################################################################################

# Coletar todos os nconsts usados
nconsts_usados = set(map_ator.values())
for diretores in map_diretor.values():
    if isinstance(diretores, str):
        nconsts_usados.update(diretores.split(','))

# Carregar apenas os nomes necessários
df_names_full = pd.read_csv('dados/name.basics.tsv', sep='\t', dtype=str, na_values='\\N')
df_names = df_names_full[df_names_full['nconst'].isin(nconsts_usados)].drop_duplicates('nconst')

map_nconst_to_name = df_names.set_index('nconst')['primaryName'].to_dict()
map_nconst_to_birth = df_names.set_index('nconst')['birthYear'].to_dict()
map_nconst_to_death = df_names.set_index('nconst')['deathYear'].to_dict()

# Verificação
print(f"\nAtores/Diretores esperados: {len(nconsts_usados)}")
print(f"Nomes encontrados: {len(df_names)}\n")

################################################################################

# Populando os dados na ontologia
for _, row in df_titles.iterrows():
    tconst = row['tconst']
    titulo = onto.Titulo(f"titulo_{tconst}")

    if pd.notna(row['primaryTitle']):
        titulo.titulo = row['primaryTitle']

    if pd.notna(row['startYear']) and row['startYear'].isdigit():
        titulo.ano = int(row['startYear'])

    # Gêneros
    if pd.notna(row['genres']):
        for g in row['genres'].split(','):
            nome_genero = g.strip().lower().replace(" ", "_")
            genero = onto.search_one(nome_genero=g.strip())
            if not genero:
                genero = onto.Genero(f"genero_{nome_genero}")
                genero.nome_genero = g.strip()
            titulo.tem_genero.append(genero)

    # Diretor(es)
    diretor_id = map_diretor.get(tconst)
    if diretor_id:
        for did in diretor_id.split(','):
            diretor = onto.search_one(iri="*diretor_" + did)
            if not diretor:
                diretor = onto.Diretor(f"diretor_{did}")
                nome_diretor = map_nconst_to_name.get(did)
                if nome_diretor:
                    diretor.nome = nome_diretor

                nasc = map_nconst_to_birth.get(did)
                if pd.notna(nasc):
                    try:
                        diretor.ano_nascimento = int(float(nasc))
                    except:
                        pass

                mort = map_nconst_to_death.get(did)
                if pd.notna(mort):
                    try:
                        diretor.ano_morte = int(float(mort))
                    except:
                        pass

            titulo.tem_diretor.append(diretor)

    # Ator principal
    ator_id = map_ator.get(tconst)
    if ator_id:
        ator = onto.search_one(iri="*ator_" + ator_id)
        if not ator:
            ator = onto.Ator(f"ator_{ator_id}")
            nome_ator = map_nconst_to_name.get(ator_id)
            if nome_ator:
                ator.nome = nome_ator

            nasc = map_nconst_to_birth.get(ator_id)
            if pd.notna(nasc):
                try:
                    ator.ano_nascimento = int(float(nasc))
                except:
                    pass

            mort = map_nconst_to_death.get(ator_id)
            if pd.notna(mort):
                try:
                    ator.ano_morte = int(float(mort))
                except:
                    pass

        titulo.ator_principal = ator
        titulo.tem_ator.append(ator)

    # Nota média IMDb
    if tconst in map_rating:
        titulo.nota_media = map_rating[tconst]
        titulo.nota = map_rating[tconst]

    # Renomear a instância
    if hasattr(titulo, "titulo") and titulo.titulo:
        nome_limpo = limpar_nome(titulo.titulo[0])
        novo_nome = f"{nome_limpo}_{tconst}"
        titulo.name = novo_nome

################################################################################

# Salvar a ontologia populada
onto.save(file="./ontology/amazing_videos_populated_v4.rdf", format="rdfxml")
onto.save(file="./ontology/amazing_videos_populated_v4.ttl", format="ntriples")

print('\nOntologia salva como "amazing_videos_populated_v4.rdf"\n')

################################################################################

end = datetime.datetime.now()
time = end - start

hour = str(time.seconds // 3600).zfill(2)
min = str((time.seconds % 3600) // 60).zfill(2)
sec = str(time.seconds % 60).zfill(2)

msg_time = f' Time:{hour}:{min}:{sec} '
print(msg_time.center(80, '#'))

################################################################################
