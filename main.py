from onthology_populator import OntologiaIMDbPopulador
from onthology import onto
from tqdm import tqdm
  
  
def main():
    print("Iniciando a população da ontologia IMDb...")
    populador = OntologiaIMDbPopulador(onto, limit=100)

    # Popular ontologia por partes com barra de progressosourceece
    print(" - Carregando títulos básicos...")
    populador.carregar_basics()
    for _ in tqdm(range(1), desc="Títulos básicos"):
        populador.popular_basics()

    print(" - Carregando avaliações...")
    populador.carregar_ratings()
    for _ in tqdm(range(1), desc="Avaliações"):
        populador.popular_ratings()

    print(" - Carregando diretores e roteiristas...")
    populador.carregar_crew()
    for _ in tqdm(range(1), desc="Crew"):
        populador.popular_crew()

    print(" - Carregando títulos alternativos...")
    populador.carregar_akas()
    for _ in tqdm(range(1), desc="Títulos alternativos"):
        populador.popular_akas()

    print(" - Carregando pessoas e papéis principais...")
    populador.carregar_principals()
    populador.carregar_people()
    for _ in tqdm(range(1), desc="Pessoas e papéis"):
        populador.popular_principals()

    # Exportação final
    onto.save(file="ontologia_filmes_completa.owl", format="rdfxml")
    onto.save(file="ontologia_filmes_completa.ttl", format="turtle")
    print("Ontologia salva com sucesso nos formatos OWL e Turtle.")


if __name__ == "__main__":
    main()
