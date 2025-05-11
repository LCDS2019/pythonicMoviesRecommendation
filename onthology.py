from owlready2 import *
import os

DATASET_DIRECTORY_PATH = "/media/orlando/another/imdb/"

class OntologiaFilmes:
    def __init__(self, iri="http://each.usp.br/ontologia/filmes.owl"):
        self.onto = get_ontology(iri)

    def definir_classes_e_propriedades(self):
        with self.onto:
            # Classes
            class Filme(Thing): pass
            class Genero(Thing): pass
            class Pessoa(Thing): pass
            class Avaliacao(Thing): pass
            class PapelPrincipal(Thing): pass
            class TituloAlternativo(Thing): pass

            # Propriedades de Dados — title.basics
            class id_titulo(Filme >> str, DataProperty): pass
            class tipo_titulo(Filme >> str, DataProperty): pass
            class titulo_principal(Filme >> str, DataProperty): pass
            class titulo_original(Filme >> str, DataProperty): pass
            class eh_adulto(Filme >> bool, DataProperty): pass
            class ano_inicio(Filme >> int, DataProperty): pass
            class ano_fim(Filme >> int, DataProperty): pass
            class duracao_minutos(Filme >> int, DataProperty): pass
            class lista_generos(Filme >> str, DataProperty): pass

            # Propriedades de Dados — title.akas
            class id_titulo_alternativo(TituloAlternativo >> str, DataProperty): pass
            class ordem(TituloAlternativo >> int, DataProperty): pass
            class nome_titulo(TituloAlternativo >> str, DataProperty): pass
            class regiao(TituloAlternativo >> str, DataProperty): pass
            class idioma(TituloAlternativo >> str, DataProperty): pass
            class tipos(TituloAlternativo >> str, DataProperty): pass
            class atributos(TituloAlternativo >> str, DataProperty): pass
            class eh_titulo_original(TituloAlternativo >> bool, DataProperty): pass

            # Propriedades de Dados — title.ratings
            class id_titulo_avaliado(Avaliacao >> str, DataProperty): pass
            class nota_media(Avaliacao >> float, DataProperty): pass
            class total_votos(Avaliacao >> int, DataProperty): pass

            # Propriedades de Dados — title.principals
            class id_titulo_papel(PapelPrincipal >> str, DataProperty): pass
            class ordem_credito(PapelPrincipal >> int, DataProperty): pass
            class id_pessoa(PapelPrincipal >> str, DataProperty): pass
            class categoria(PapelPrincipal >> str, DataProperty): pass
            class trabalho(PapelPrincipal >> str, DataProperty): pass
            class personagens(PapelPrincipal >> str, DataProperty): pass

            # Propriedades de Dados — title.crew
            class id_titulo_crew(Filme >> str, DataProperty): pass
            class lista_diretores(Filme >> str, DataProperty): pass
            class lista_roteiristas(Filme >> str, DataProperty): pass

            # Propriedades de Dados — name.basics
            class ano_nascimento(Pessoa >> int, DataProperty): pass
            class ano_falecimento(Pessoa >> int, DataProperty): pass
            class profissoes_principais(Pessoa >> str, DataProperty): pass
            class titulos_conhecidos(Pessoa >> str, DataProperty): pass

            # Propriedades Objetais
            class tem_genero(Filme >> Genero): pass
            class tem_avaliacao(Filme >> Avaliacao): pass
            class tem_titulo_alternativo(Filme >> TituloAlternativo): pass
            class tem_papel_principal(Filme >> PapelPrincipal): pass
            class representado_por(PapelPrincipal >> Pessoa): pass

    def adicionar_axiomas(self):
        with self.onto:
            # Domínio e Alcance
            tem_genero.domain = [Filme]; tem_genero.range = [Genero]
            tem_avaliacao.domain = [Filme]; tem_avaliacao.range = [Avaliacao]
            tem_titulo_alternativo.domain = [Filme]; tem_titulo_alternativo.range = [TituloAlternativo]
            tem_papel_principal.domain = [Filme]; tem_papel_principal.range = [PapelPrincipal]
            representado_por.domain = [PapelPrincipal]; representado_por.range = [Pessoa]

            # Disjunções
            AllDisjoint([Filme, Pessoa, Genero, Avaliacao, PapelPrincipal, TituloAlternativo])

            # Propriedades funcionais
            id_titulo.characteristic = [FunctionalProperty]
            titulo_principal.characteristic = [FunctionalProperty]
            titulo_original.characteristic = [FunctionalProperty]
            nota_media.characteristic = [FunctionalProperty]
            total_votos.characteristic = [FunctionalProperty]

            # Cardinalidades mínimas
            class Filme(Filme):
                equivalent_to.append(Filme & (tem_genero.min(1, Genero)))
                equivalent_to.append(Filme & (tem_avaliacao.min(1, Avaliacao)))

            class Avaliacao(Avaliacao):
                equivalent_to.append(Avaliacao & (nota_media.exactly(1, float)))

            class PapelPrincipal(PapelPrincipal):
                equivalent_to.append(PapelPrincipal & (representado_por.exactly(1, Pessoa)))

            # Definições equivalentes
            class Diretor(Pessoa):
                equivalent_to = [
                    Pessoa & inverse(representado_por).some(
                        PapelPrincipal & (trabalho.value("director"))
                    )
                ]

            class Ator(Pessoa):
                equivalent_to = [
                    Pessoa & inverse(representado_por).some(
                        PapelPrincipal & (categoria.value("actor"))
                    )
                ]

    def salvar(self, caminho="ontologia_filmes_completa.owl"):
        self.onto.save(file=caminho, format="rdfxml")
        self.onto.save(file=os.path.splitext(caminho)[0] + ".ttl", format="turtle")


if __name__ == "__main__":
    of = OntologiaFilmes()
    of.definir_classes_e_propriedades()
    of.adicionar_axiomas()
    of.salvar()
