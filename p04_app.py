import streamlit as st
from owlready2 import get_ontology, destroy_entity
import os

st.set_page_config(page_title="Sistema de Filmes", layout="centered")

# Carrega a ontologia
onto = get_ontology("./ontology/amazing_videos_populated_v4.rdf").load()

st.title("🎬 Sistema de Recomendação de Filmes")
st.markdown("Cadastre suas preferências para recomendações personalizadas.")

# --- Cadastro do usuário ---
st.subheader("👤 Cadastro de Usuário")
nome = st.text_input("Nome completo do usuário", max_chars=100)

# Listas completas para sugestões
atores_opcoes = sorted({a.nome for a in onto.Ator.instances() if hasattr(a, 'nome')})
diretores_opcoes = sorted({d.nome for d in onto.Diretor.instances() if hasattr(d, 'nome')})
generos_opcoes = sorted({g.nome_genero for g in onto.Genero.instances() if hasattr(g, 'nome_genero')})

ator_pref = st.text_input("Ator preferido", value="")
diretor_pref = st.text_input("Diretor preferido", value="")
generos_pref = st.multiselect("Gêneros preferidos", options=generos_opcoes)

usuarios_existentes = {u.nome: u for u in onto.Usuario.instances() if hasattr(u, 'nome') and u.nome.strip() != ""}

usuario_existente = usuarios_existentes.get(nome)
if usuario_existente:
    st.info("Usuário já cadastrado. Você pode atualizar ou remover suas preferências abaixo.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Atualizar usuário"):
            with onto:
                if ator_pref:
                    ator_onto = onto.search_one(nome=ator_pref)
                    if ator_onto:
                        usuario_existente.prefere_ator.clear()
                        usuario_existente.prefere_ator.append(ator_onto)
                if diretor_pref:
                    dir_onto = onto.search_one(nome=diretor_pref)
                    if dir_onto:
                        usuario_existente.prefere_diretor.clear()
                        usuario_existente.prefere_diretor.append(dir_onto)

                for pref in list(usuario_existente.tem_preferencia):
                    usuario_existente.tem_preferencia.remove(pref)

                for genero_pref in generos_pref:
                    gen_onto = onto.search_one(nome_genero=genero_pref)
                    if gen_onto:
                        pref = onto.Preferencia(f"pref_{usuario_existente.name}_{genero_pref}")
                        pref.genero_preferido = genero_pref
                        usuario_existente.tem_preferencia.append(pref)

                st.success("Usuário atualizado com sucesso!")
                onto.save(file="./ontology/amazing_videos_populated_v4.rdf", format="rdfxml")
    with col2:
        if st.button("Remover usuário"):
            with onto:
                destroy_entity(usuario_existente)
                st.success(f"Usuário '{nome}' removido com sucesso.")
                onto.save(file="./ontology/amazing_videos_populated_v4.rdf", format="rdfxml")
                st.stop()
else:
    if not nome.strip():
        st.warning("⚠️ Por favor, preencha o nome do usuário para habilitar o cadastro.")
    else:
        if st.button("Salvar usuário"):
            with onto:
                novo_id = "usuario_" + nome.strip().lower().replace(" ", "_")
                novo = onto.Usuario(novo_id)
                novo.nome = nome
                novo.nome_usuario = novo_id

                if ator_pref:
                    ator_onto = onto.search_one(nome=ator_pref)
                    if ator_onto:
                        novo.prefere_ator.append(ator_onto)

                if diretor_pref:
                    dir_onto = onto.search_one(nome=diretor_pref)
                    if dir_onto:
                        novo.prefere_diretor.append(dir_onto)

                for genero_pref in generos_pref:
                    gen_onto = onto.search_one(nome_genero=genero_pref)
                    if gen_onto:
                        pref = onto.Preferencia(f"pref_{novo_id}_{genero_pref}")
                        pref.genero_preferido = genero_pref
                        novo.tem_preferencia.append(pref)

                st.success("Usuário cadastrado com sucesso!")
                onto.save(file="./ontology/amazing_videos_populated_v4.rdf", format="rdfxml")

# --- Lista de recomendações ---
st.subheader("🎥 Filmes Recomendados")
usuarios = {u.name: u.nome for u in onto.Usuario.instances() if hasattr(u, 'nome') and u.nome.strip() != ""}
usuario_sel_nome = st.selectbox("Selecione o usuário para ver recomendações", options=list(usuarios.values()))
usuario_sel = next((k for k, v in usuarios.items() if v == usuario_sel_nome), None)

if usuario_sel is None:
    st.warning("Usuário não encontrado. Por favor, selecione um nome válido.")
    st.stop()

usuario_obj = onto.search_one(iri=f"*{usuario_sel}")

if st.button("🔍 Buscar filmes recomendados"):
    filmes_disponiveis = [f for f in onto.Titulo.instances() if not onto.search_one(avaliador=usuario_obj, filme_avaliado=f)]
    usuario_generos = {p.genero_preferido for p in usuario_obj.tem_preferencia if hasattr(p, 'genero_preferido')}
    usuario_ator = next(iter(usuario_obj.prefere_ator), None) if hasattr(usuario_obj, 'prefere_ator') else None
    usuario_diretor = next(iter(usuario_obj.prefere_diretor), None) if hasattr(usuario_obj, 'prefere_diretor') else None

    filmes_filtrados = []
    for f in filmes_disponiveis:
        match_genero = not usuario_generos or any(
            isinstance(g.nome_genero, str) and g.nome_genero in usuario_generos
            for g in f.tem_genero if hasattr(g, 'nome_genero')
        )
        match_ator = not usuario_ator or (hasattr(f, 'ator_principal') and f.ator_principal == usuario_ator)
        match_diretor = not usuario_diretor or any(d == usuario_diretor for d in f.tem_diretor)

        if match_genero and match_ator and match_diretor and hasattr(f, 'nota_media') and f.nota_media is not None:
            filmes_filtrados.append(f)

    filmes_filtrados.sort(key=lambda x: x.nota_media, reverse=True)
    filmes_filtrados = filmes_filtrados[:100]

    st.markdown(f"{len(filmes_filtrados)} filmes recomendados:")

    for f in filmes_filtrados:
        titulo_filme = f.titulo if isinstance(f.titulo, str) else f.titulo[0] if hasattr(f, 'titulo') else f.name
        ator_principal = f.ator_principal.nome if hasattr(f, 'ator_principal') and hasattr(f.ator_principal, 'nome') else 'N/A'
        diretores = ", ".join(getattr(d, 'nome', 'Desconhecido') for d in f.tem_diretor)
        generos = ", ".join(g.nome_genero for g in f.tem_genero if hasattr(g, 'nome_genero'))
        ano = f.ano if hasattr(f, 'ano') else 'N/A'
        nota = f.nota_media if hasattr(f, 'nota_media') else 'N/A'

        with st.container():
            st.markdown(f"""
                <div style='border: 1px solid #ccc; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                    <strong>{titulo_filme} - {ano} - Nota IMDb: {nota}</strong><br/>
                    <em>Diretor(es): {diretores} | Ator principal: {ator_principal}</em><br/>
                    Gêneros: {generos}
                </div>
            """, unsafe_allow_html=True)
