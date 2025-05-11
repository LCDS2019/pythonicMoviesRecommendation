import datetime
start = datetime.datetime.now()

import os
os.system('clear')

################################################################################

from owlready2 import *

################################################################################

onto = get_ontology("http://each.br/amazing_videos.owl")

with onto:
    # Classe base
    class Pessoa(Thing): pass

    # Subclasses
    class Ator(Pessoa): pass
    class Diretor(Pessoa): pass
    class Usuario(Pessoa): pass

    # Demais classes
    class Filme(Thing): pass
    class Avaliacao(Thing): pass
    class Preferencia(Thing): pass

    # DataProperties de Pessoa
    class nome(DataProperty, FunctionalProperty): domain = [Pessoa]; range = [str]
    class anoNascimento(DataProperty, FunctionalProperty): domain = [Pessoa]; range = [int]
    class anoMorte(DataProperty, FunctionalProperty): domain = [Pessoa]; range = [int]

    # DataProperties de Filme
    class titulo(DataProperty, FunctionalProperty): domain = [Filme]; range = [str]
    class ano(DataProperty, FunctionalProperty): domain = [Filme]; range = [int]
    class categoria(DataProperty, FunctionalProperty): domain = [Filme]; range = [str]
    class nota(DataProperty, FunctionalProperty): domain = [Filme, Avaliacao]; range = [float]
    class quantidadeVotos(DataProperty, FunctionalProperty): domain = [Filme]; range = [int]

    # DataProperties de Usuario e Avaliação
    class nomeUsuario(DataProperty, FunctionalProperty): domain = [Usuario]; range = [str]
    class generoPreferido(DataProperty, FunctionalProperty): domain = [Preferencia]; range = [str]
    class comentario(DataProperty, FunctionalProperty): domain = [Avaliacao]; range = [str]

    # ObjectProperties
    class temDiretor(ObjectProperty): domain = [Filme]; range = [Diretor]
    class atuaEm(ObjectProperty): domain = [Ator]; range = [Filme]

    class temPreferencia(ObjectProperty): domain = [Usuario]; range = [Preferencia]
    class realizouAvaliacao(ObjectProperty): domain = [Usuario]; range = [Avaliacao]
    class avaliou(ObjectProperty): domain = [Avaliacao]; range = [Filme]

################################################################################

onto.save(file="./ontology/amazing_videos_v2.rdf", format="rdfxml")
onto.save(file="./ontology/amazing_videos_v2.ttl", format="turtle")

print("Ontologia criada e salva com sucesso.")

################################################################################

end = datetime.datetime.now()
time = end - start

hour = str(time.seconds // 3600).zfill(2)
min = str((time.seconds % 3600) // 60).zfill(2)
sec = str(time.seconds % 60).zfill(2)

msg_time = f' Time:{hour}:{min}:{sec} '
print(msg_time.center(80,'#'))

################################################################################