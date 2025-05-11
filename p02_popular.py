import datetime
start = datetime.datetime.now()

import os
os.system('clear')

################################################################################

from owlready2 import *
import pandas as pd
import gc

################################################################################

def open_base(base,onto):

    print('')
    print(f' {base} '.center(40,'-'))

    if base == 'name.basics':
        with onto:
            chunk_iter = pd.read_csv(f'./original/{base}.tsv', sep="\t", low_memory=False, chunksize=1000)
            
            for chunk in chunk_iter:
                for _, row in chunk.iterrows():
                    try:
                        ind = onto.Pessoa(row['nconst'])

                        if pd.notna(row['primaryName']):
                            ind.nome = row['primaryName']

                        if pd.notna(row['birthYear']) and str(row['birthYear']).isdigit():
                            ind.anoNascimento = int(row['birthYear'])

                        if pd.notna(row['deathYear']) and str(row['deathYear']).isdigit():
                            ind.anoMorte = int(row['deathYear'])

                    except Exception as e:
                        print(f"[Erro] Indivíduo {row.get('nconst', '')}: {e}")
                
                del chunk
                gc.collect()
                
    elif base == 'title.basics':
        with onto:
            chunk_iter = pd.read_csv(f'./original/{base}.tsv', sep="\t", low_memory=False, chunksize=1000)

            for chunk in chunk_iter:
                for _, row in chunk.iterrows():
                    try:
                        ind = onto.Filme(row['tconst'])

                        if pd.notna(row['primaryTitle']):
                            ind.titulo = row['primaryTitle']
                            
                        if pd.notna(row['startYear']) and str(row['startYear']).isdigit():
                            ind.ano = int(row['startYear'])

                        if pd.notna(row['genres']):
                            ind.categoria = row['genres']

                    except Exception as e:
                        print(f"[Erro] Filme {row.get('tconst', '')}: {e}")

                del chunk
                gc.collect()

    elif base == 'title.crew':
        with onto:
            chunk_iter = pd.read_csv(f'./original/{base}.tsv', sep="\t", low_memory=False, chunksize=1000)

            for chunk in chunk_iter:
                for _, row in chunk.iterrows():
                    try:
                        filme = onto.search_one(iri="*" + row['tconst'])
                        if not filme:
                            filme = onto.Filme(row['tconst'])

                        if pd.notna(row['directors']):
                            for diretor_id in row['directors'].split(','):
                                diretor = onto.search_one(iri="*" + diretor_id)
                                if not diretor:
                                    diretor = onto.Diretor(diretor_id)

                                if hasattr(filme, 'temDiretor'):
                                    if diretor not in filme.temDiretor:
                                        filme.temDiretor.append(diretor)
                                else:
                                    print(f"[Aviso] 'temDiretor' não existe para Filme {filme.name}")

                    except Exception as e:
                        print(f"[Erro] na linha de 'title.crew': {e}")

                del chunk
                gc.collect()

                            
    elif base == 'title.principal':
        with onto:
            chunk_iter = pd.read_csv(f'./original/{base}.tsv', sep="\t", low_memory=False, chunksize=1000)

            count = 0
            for chunk in chunk_iter:
                for _, row in chunk.iterrows():
                    try:
                        filme_id = row['tconst']
                        pessoa_id = row['nconst']
                        categoria = row['category']

                        filme = onto.search_one(iri="*" + filme_id) or onto.Filme(filme_id)

                        if categoria in ['actor', 'actress']:
                            pessoa = onto.search_one(iri="*" + pessoa_id) or onto.Ator(pessoa_id)
                            if hasattr(pessoa, 'atuaEm') and filme not in pessoa.atuaEm:
                                pessoa.atuaEm.append(filme)

                        elif categoria == 'director':
                            pessoa = onto.search_one(iri="*" + pessoa_id) or onto.Diretor(pessoa_id)
                            if hasattr(filme, 'temDiretor') and pessoa not in filme.temDiretor:
                                filme.temDiretor.append(pessoa)

                        else:
                            pessoa = onto.search_one(iri="*" + pessoa_id) or onto.Pessoa(pessoa_id)

                    except Exception as e:
                        print(f"[Erro] title.principal - pessoa {row.get('nconst', '')}: {e}")

                del chunk
                gc.collect()

    elif base == 'title.ratings':
        with onto:
            chunk_iter = pd.read_csv(f'./original/{base}.tsv', sep="\t", low_memory=False, chunksize=1000)

            for chunk in chunk_iter:
                for _, row in chunk.iterrows():
                    try:
                        filme_id = row['tconst']
                        filme = onto.search_one(iri="*" + filme_id) or onto.Filme(filme_id)

                        if pd.notna(row['averageRating']) and hasattr(filme, 'nota'):
                            filme.nota = float(row['averageRating'])  # valor direto, não lista

                        if pd.notna(row['numVotes']) and hasattr(filme, 'quantidadeVotos'):
                            filme.quantidadeVotos = int(row['numVotes'])  # valor direto, não lista

                    except Exception as e:
                        print(f"[Erro] title.ratings - filme {row.get('tconst', '')}: {e}")

                del chunk
                gc.collect()

################################################################################

print(' Ontology load '.center(80,'#'))

onto = get_ontology('./ontology/amazing_videos_v2.rdf').load()

print("Classes existentes:")
for cls in onto.classes():
    print(f"- {cls.name}")

################################################################################

print(' Base load '.center(80,'#'))

base_list = ['name.basics','title.basics','title.crew','title.principals','title.ratings']  #'title.akas','title.episode'

for base in base_list:
    open_base(base, onto)

################################################################################

onto.save(file="./ontology/amazing_videos_populated.rdf", format="rdfxml")
onto.save(file='./ontology/amazing_videos_populated.ttl', format='ntriples')
print('\nOntologia salva como "amazing_videos_populated.rdf"\n')

################################################################################

end = datetime.datetime.now()
time = end - start

hour = str(time.seconds // 3600).zfill(2)
min = str((time.seconds % 3600) // 60).zfill(2)
sec = str(time.seconds % 60).zfill(2)

msg_time = f' Time:{hour}:{min}:{sec} '
print(msg_time.center(80,'#'))

################################################################################

