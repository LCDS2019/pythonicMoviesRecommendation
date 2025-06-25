import datetime
start = datetime.datetime.now()

import os
os.system('clear')

################################################################################

from owlready2 import *

################################################################################

onto = get_ontology("http://each.br/amazing_videos.owl")

with onto:
    # Classes principais
    class Pessoa(Thing): pass
    class Ator(Pessoa): pass
    class Diretor(Pessoa): pass
    class Usuario(Pessoa): pass

    class Titulo(Thing): pass
    class Genero(Thing): pass   
    class Avaliacao(Thing): pass
    class Preferencia(Thing): pass
    class TituloAlternativo(Thing): pass
    class PapelPrincipal(Thing): pass

################################################################################

with onto:
    # Propriedades de dados relacionadas a Pessoa
    class nome(DataProperty, FunctionalProperty):
        domain = [Pessoa]
        range = [str]

    class ano_nascimento(DataProperty, FunctionalProperty):
        domain = [Pessoa]
        range = [int]

    class ano_morte(DataProperty, FunctionalProperty):
        domain = [Pessoa]
        range = [int]

################################################################################

with onto:
    # Propriedades de dados relacionadas a Titulo
    class titulo(DataProperty, FunctionalProperty):
        domain = [Titulo]
        range = [str]

    class ano(DataProperty, FunctionalProperty):
        domain = [Titulo]
        range = [int]

    class nota(DataProperty, FunctionalProperty):
        domain = [Titulo, Avaliacao]
        range = [float]

    class nota_media(DataProperty, FunctionalProperty):
        domain = [Titulo]
        range = [float]

    class quantidade_votos(DataProperty, FunctionalProperty):
        domain = [Titulo]
        range = [int]

    class total_votos(DataProperty, FunctionalProperty):
        domain = [Titulo]
        range = [int]

    class nome_genero(DataProperty, FunctionalProperty):
        domain = [Genero]
        range = [str]

################################################################################

with onto:
    # Propriedades de dados e objetos relacionadas a Usuario e Preferencia
    class nome_usuario(DataProperty, FunctionalProperty):
        domain = [Usuario]
        range = [str]

    class genero_preferido(DataProperty, FunctionalProperty):
        domain = [Preferencia]
        range = [str]

    class nota_usuario(DataProperty, FunctionalProperty):
        domain = [Avaliacao]
        range = [float]

    class nome_avaliador(DataProperty, FunctionalProperty):
        domain = [Avaliacao]
        range = [str]

    class tem_preferencia(ObjectProperty):
        domain = [Usuario]
        range = [Preferencia]

    Usuario.is_a.append(tem_preferencia.some(Preferencia))

################################################################################

with onto:
    # Avaliação: quem avaliou o quê (propriedades FUNCIONAIS)
    class avaliador(ObjectProperty, FunctionalProperty):
        domain = [Avaliacao]
        range = [Usuario]

    class realizou_avaliacao(ObjectProperty):
        domain = [Usuario]
        range = [Avaliacao]

    avaliador.inverse_property = realizou_avaliacao

    class filme_avaliado(ObjectProperty, FunctionalProperty):
        domain = [Avaliacao]
        range = [Titulo]

    class foi_avaliado_por(ObjectProperty):
        domain = [Titulo]
        range = [Avaliacao]

    filme_avaliado.inverse_property = foi_avaliado_por

    # Axioma: toda avaliação deve ter exatamente uma nota de usuário
    Avaliacao.is_a.append(nota_usuario.exactly(1, float))

################################################################################

with onto:
    # Relações título ↔ diretor / ator
    class tem_diretor(ObjectProperty):
        domain = [Titulo]
        range = [Diretor]

    class dirige(ObjectProperty):
        domain = [Diretor]
        range = [Titulo]

    tem_diretor.inverse_property = dirige

    class atua_em(ObjectProperty):
        domain = [Ator]
        range = [Titulo]

    class tem_ator(ObjectProperty):
        domain = [Titulo]
        range = [Ator]

    atua_em.inverse_property = tem_ator

    # Relação específica para ator principal
    class ator_principal(ObjectProperty, FunctionalProperty):
        domain = [Titulo]
        range = [Ator]

################################################################################

with onto:
    # Outras relações com Titulo
    class tem_genero(ObjectProperty):
        domain = [Titulo]
        range = [Genero]

    class tem_avaliacao(ObjectProperty):
        domain = [Titulo]
        range = [Avaliacao]

    class tem_titulo_alternativo(ObjectProperty):
        domain = [Titulo]
        range = [TituloAlternativo]

    # Axiomas de cardinalidade mínima
    Titulo.is_a.append(tem_genero.min(1, Genero))
    Titulo.is_a.append(tem_avaliacao.min(1, Avaliacao))

################################################################################

with onto:
    # Instâncias de exemplo

    # Criando um ator
    ator1 = Ator("ator_keanu")
    ator1.nome = "Keanu Reeves"

    # Criando um diretor
    diretor1 = Diretor("diretor_wachowski")
    diretor1.nome = "Lana Wachowski"

    # Criando um título
    t1 = Titulo("titulo_matrix")
    t1.titulo = "Matrix"
    t1.ano = 1999
    t1.ator_principal = ator1
    t1.tem_ator.append(ator1)
    t1.tem_diretor.append(diretor1)

    # Criando um gênero
    g1 = Genero("genero_scifi")
    g1.nome_genero = "Sci-Fi"
    t1.tem_genero.append(g1)

    # Criando um usuário e uma avaliação
    u1 = Usuario("usuario_joana")
    u1.nome = "Joana Silva"
    u1.nome_usuario = "joana_s"
    u1.ano_nascimento = 1992

    a1 = Avaliacao("avaliacao_joana_matrix")
    a1.avaliador = u1
    a1.filme_avaliado = t1
    a1.nota_usuario = 9.0
    a1.nome_avaliador = "Joana"
    t1.tem_avaliacao.append(a1)

with onto:
    class prefere_ator(ObjectProperty):
        domain = [Usuario]
        range = [Ator]

    class prefere_diretor(ObjectProperty):
        domain = [Usuario]
        range = [Diretor]


################################################################################

# Salvando a ontologia
onto.save(file="./ontology/amazing_videos_p04.rdf", format="rdfxml")
onto.save(file="./ontology/amazing_videos_p04.ttl", format="turtle")

print("Ontologia criada e salva com sucesso - p04.")

################################################################################

end = datetime.datetime.now()
time = end - start

hour = str(time.seconds // 3600).zfill(2)
min = str((time.seconds % 3600) // 60).zfill(2)
sec = str(time.seconds % 60).zfill(2)

msg_time = f' Time:{hour}:{min}:{sec} '
print(msg_time.center(80, '#'))

################################################################################
