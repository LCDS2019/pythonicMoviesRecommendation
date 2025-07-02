import streamlit as st
from owlready2 import get_ontology, destroy_entity
import os
from collections import defaultdict

st.set_page_config(page_title="Amazing Videos", page_icon="🎥", layout="centered")

# Carrega a ontologia
onto = get_ontology("./ontology/amazing_videos_populated_v4.rdf").load()

# Escolha da tela
st.sidebar.title("🎥 Amazing Videos")
st.sidebar.subheader("Navegação")
opcao = st.sidebar.radio("Ir para:", ["Cadastro de Usuário", "Filmes Recomendados", "Filmes Avaliados"])

# Lista de usuários
usuarios_existentes = {u.nome: u for u in onto.Usuario.instances() if hasattr(u, 'nome') and u.nome.strip() != ""}

if opcao == "Cadastro de Usuário":
    st.title("👤 Cadastro de Usuário")
    nome = st.text_input("Nome completo do usuário", max_chars=100)

    atores_opcoes = sorted({a.nome for a in onto.Ator.instances() if hasattr(a, 'nome')})
    diretores_opcoes = sorted({d.nome for d in onto.Diretor.instances() if hasattr(d, 'nome')})
    generos_opcoes = sorted({g.nome_genero for g in onto.Genero.instances() if hasattr(g, 'nome_genero')})

    ator_pref = st.selectbox("Ator preferido", [""] + atores_opcoes)
    diretor_pref = st.selectbox("Diretor preferido", [""] + diretores_opcoes)
    generos_pref = st.multiselect("Gêneros preferidos", options=generos_opcoes)

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

elif opcao == "Filmes Recomendados":
    st.title("🎬 Recomendados - Amazing Videos")
    if not usuarios_existentes:
        st.warning("⚠️ Nenhum usuário cadastrado no sistema.")
        st.stop()
    nome_usuario = st.selectbox("Selecione o usuário", list(usuarios_existentes.keys()))
    usuario = usuarios_existentes[nome_usuario]

    if st.button("🔄 Atualizar Lista"):
        st.rerun()

    generos_usuario = [p.genero_preferido for p in usuario.tem_preferencia]
    ator_usuario = usuario.prefere_ator[0] if usuario.prefere_ator else None
    diretor_usuario = usuario.prefere_diretor[0] if usuario.prefere_diretor else None

    filmes_recomendados = []
    for f in onto.Titulo.instances():
        if not hasattr(f, 'titulo') or not hasattr(f, 'ano'):
            continue

        match_genero = any(g.nome_genero in generos_usuario for g in f.tem_genero)
        match_ator = ator_usuario in f.tem_ator
        match_diretor = diretor_usuario in f.tem_diretor

        if match_genero or match_ator or match_diretor:
            filmes_recomendados.append(f)

    def nota_para_ordenacao(filme):
        for a in filme.tem_avaliacao:
            if a.avaliador == usuario:
                return a.nota_usuario
        return getattr(filme, 'nota_media', 0) or 0.0

    filmes_recomendados.sort(key=nota_para_ordenacao, reverse=True)
    filmes_recomendados = filmes_recomendados[:100]

    for filme in filmes_recomendados:
        genero_str = ", ".join(g.nome_genero for g in filme.tem_genero) if hasattr(filme, 'tem_genero') else ""

        nota_usuario = next((a.nota_usuario for a in filme.tem_avaliacao if a.avaliador == usuario), None)
        if nota_usuario is not None:
            nota_str = f"Nota: {nota_usuario} / IMDb: {getattr(filme, 'nota_media', 'N/A')}"
        else:
            nota_str = f"IMDb: {getattr(filme, 'nota_media', 'N/A')}"

        with st.expander(f"{filme.titulo} - {filme.ano} - {nota_str}"):
            ator_nome = filme.ator_principal.nome if hasattr(filme, 'ator_principal') and filme.ator_principal else ""
            diretor_nome = filme.tem_diretor[0].nome if hasattr(filme, 'tem_diretor') and len(filme.tem_diretor) > 0 and hasattr(filme.tem_diretor[0], 'nome') else ""
            st.caption(f"🎭 Ator Principal: {ator_nome}  |  🎬 Diretor: {diretor_nome}  |  🏷️ Gênero(s): {genero_str}")

            nota_atual = nota_usuario if nota_usuario is not None else ""
            nova_nota = st.number_input("Sua nota (0 a 10)", 0.0, 10.0, float(nota_atual) if nota_atual else 5.0, step=0.5, key=filme.name)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Salvar nota", key=f"save_{filme.name}"):
                    with onto:
                        avaliacao = next((a for a in filme.tem_avaliacao if a.avaliador == usuario), None)
                        if not avaliacao:
                            avaliacao = onto.Avaliacao(f"avaliacao_{usuario.name}_{filme.name}")
                            avaliacao.avaliador = usuario
                            avaliacao.filme_avaliado = filme
                            filme.tem_avaliacao.append(avaliacao)
                        avaliacao.nota_usuario = nova_nota
                        st.success("Nota salva com sucesso!")
                        onto.save(file="./ontology/amazing_videos_populated_v4.rdf", format="rdfxml")
            with col2:
                if st.button("Excluir avaliação", key=f"delete_{filme.name}"):
                    with onto:
                        avaliacao = next((a for a in filme.tem_avaliacao if a.avaliador == usuario), None)
                        if avaliacao:
                            destroy_entity(avaliacao)
                            st.success("Avaliação excluída com sucesso!")
                            onto.save(file="./ontology/amazing_videos_populated_v4.rdf", format="rdfxml")

elif opcao == "Filmes Avaliados":
    st.title("📊 Avaliações - Amazing Videos")
    if not usuarios_existentes:
        st.warning("⚠️ Nenhum usuário cadastrado no sistema.")
        st.stop()
    nome_usuario = st.selectbox("Selecione o usuário", list(usuarios_existentes.keys()), key="avaliados")
    usuario = usuarios_existentes[nome_usuario]

    if st.button("🔄 Atualizar Lista", key="refresh_avaliados"):
        st.rerun()

    avaliacoes_usuario = [a for a in onto.Avaliacao.instances() if a.avaliador == usuario]
    avaliacoes_usuario.sort(key=lambda a: a.nota_usuario if a.nota_usuario is not None else 0, reverse=True)

    if not avaliacoes_usuario:
        st.info("Este usuário ainda não avaliou nenhum filme.")
    else:
        for a in avaliacoes_usuario:
            filme = a.filme_avaliado
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**🎬 {filme.titulo} - {filme.ano} - Nota: {a.nota_usuario} / IMDb: {getattr(filme, 'nota_media', 'N/A')}**")
            with col2:
                if st.button("🗑️", key=f"remove_{a.name}"):
                    with onto:
                        destroy_entity(a)
                        st.success(f"Avaliação de '{filme.titulo}' removida com sucesso.")
                        onto.save(file="./ontology/amazing_videos_populated_v4.rdf", format="rdfxml")
                        st.rerun()
