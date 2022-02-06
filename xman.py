
from time import strftime
import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import datetime
from datetime import date, datetime, timedelta
import calendar
import hashlib

from db_function import *


def reg_xman(username):
    # constante converter formato de datas gravadas na  bd sqlite para python
    formato_dia = '%Y-%m-%d'
    st.subheader("Registo de Manutenções : ")

    lista_clientes = [x[1] for x in read_clients()]
    escolher_cliente = st.selectbox(
        "Cliente - Localidade", lista_clientes)
    resultado_escolhido = ler_cliente(escolher_cliente)

    if resultado_escolhido:

        n_assoc = resultado_escolhido[0][0]

        with st.expander('Histórico de Manutenções Realizadas:'):

            historico_xman = read_hist_manut(n_assoc)
            hist_xman_rs = pd.DataFrame(historico_xman, columns=[
                'ID', 'Assoc', 'Modelo', 'Data Prevista',
                'Data Realizada', 'Tec.Atrib',
                'Tec.Realizou'])

            st.dataframe(hist_xman_rs)

        with st.expander('Regularizar Manutenção Atual'):
            ultima_xman = read_manut(n_assoc)
            data_hoje = date.today()
            if ultima_xman:
                ult_man_rs = pd.DataFrame(ultima_xman, columns=[
                    'ID', 'Assoc', 'Modelo', 'Data Prevista',
                    'Data Realizada', 'Tec.Atrib',
                    'Tec.Realizou'])
                st.write('Manutenção Atual :')
                st.dataframe(ult_man_rs)
                id_man = ult_man_rs.values[0][0]
                modelo = ult_man_rs.values[0][2]
                d_prev_bd = ult_man_rs.values[0][3]
                dia_previsto = datetime.strptime(
                    d_prev_bd, formato_dia).date()  # apenas dia
                tec_atrib = ult_man_rs.values[0][5]

                coluna1, coluna2 = st.columns(2)

                with coluna1:
                    pick_day = st.date_input(
                        'Data em que foi Realizada:', data_hoje)  # passa a data lida no picker

                    if pick_day:
                        mes_picked = pick_day.replace(day=calendar.monthrange(
                            pick_day.year, pick_day.month)[1])  # ultimo dia do mês escolhido!

                    if dia_previsto == mes_picked:

                        next_xman = dia_previsto + \
                            timedelta(days=120)
                        xman = next_xman.replace(day=calendar.monthrange(
                            next_xman.year, next_xman.month)[1])
                        msg = 'Dentro do prazo! Próxima : ' + \
                            str(xman)
                        st.info(msg)

                    elif mes_picked < dia_previsto:
                        next_xman = mes_picked + \
                            timedelta(days=120)
                        xman = next_xman.replace(day=calendar.monthrange(
                            next_xman.year, next_xman.month)[1])
                        msg = 'Foi antecipada . Prever manutenção até : ' + \
                            str(xman)
                        st.warning(msg)
                    elif mes_picked > dia_previsto:
                        offset_xman = mes_picked - dia_previsto
                        next_xman = mes_picked + \
                            timedelta(days=120)
                        next_xman = next_xman - \
                            timedelta(days=offset_xman.days)
                        xman = next_xman.replace(day=calendar.monthrange(
                            next_xman.year, next_xman.month)[1])
                        msg = 'MANUTENÇÃO EM ATRASO!!!! \n Programar Manutenção para acerto de calendário em : ' + str(
                            next_xman)
                        msg = msg + "\n diferença atual :" + \
                            str(offset_xman.days)
                        st.error(msg)
                with coluna2:
                    tec_escolhido = read_tec()
                    df_tecnicos = pd.DataFrame(tec_escolhido, columns=[
                        'Nome', 'Sigla'])
                    nomes = df_tecnicos['Nome'].tolist()
                    siglas = df_tecnicos['Sigla'].tolist()
                    dic = dict(zip(siglas, nomes))

                    tec_efec = st.selectbox(
                        'Realizada Por : ', siglas, format_func=lambda x: dic[x])
                    # st.write(tec_efec)
                    if tec_efec == 'AD' and username != 'admin':
                        st.error('O seu user não é administrador!')

                st.write('id', id_man, 'Data Real', pick_day,
                         'Próxima:', xman, 'Tec_Real:', tec_efec)
                regularizar = st.button('Regularizar')
                if regularizar:
                    upd_xman(pick_day, tec_efec, id_man)
                    st.write(
                        'Regularizada!\n Vai ser gerada novo registo de manutenção')
                    add_xman(n_assoc, modelo,
                             next_xman, tec_atrib)
                    st.write(
                        'Foi criado registo da próxima manutenção')
                    st.experimental_rerun()

        with st.expander('Lista Tarefas Pendentes neste Cliente'):
            menu_pendentes = ["Visualizar / Editar", "Criar"]
            opcao_pendentes = st.selectbox(
                "Escolher opção", menu_pendentes)
            if opcao_pendentes == 'Criar':
                colun1, colun2, colun3 = st.columns(3)

                cat_pendente = read_cat_pendente()
                df_cat_pendente = pd.DataFrame(cat_pendente, columns=[
                    'id', 'Categoria'])
                categoria = df_cat_pendente['Categoria'].tolist()
                id_cat = df_cat_pendente['id'].tolist()
                dic_cat = dict(zip(id_cat, categoria))

                estado_pendente = read_estado_pendente()
                df_est_pendente = pd.DataFrame(estado_pendente, columns=[
                    'id', 'Estado'])
                estado = df_est_pendente['Estado'].tolist()
                id_est = df_est_pendente['id'].tolist()
                dic_est = dict(zip(id_est, estado))

                with colun1:

                    cat_select = st.selectbox(
                        'Categoria : ', id_cat, format_func=lambda x: dic_cat[x])
                    estado_select = st.selectbox(
                        'Estado : ', id_est, format_func=lambda x: dic_est[x])

                with colun2:
                    data_p_criado = st.date_input('Dia Criado :', date.today())
                    if estado_select == 2:
                        data_pend_concluido = st.date_input(
                            'Dia Concluído :', date.today())
                    else:
                        data_pend_concluido = ''

                with colun3:
                    memo = st.text_area('Memória descritiva', max_chars=80)
                    adicionar_pendente = st.button(
                        'Adicionar pendente aos registos ')
                if adicionar_pendente:
                    st.write('Criado!')
                    if data_pend_concluido == "":
                        data_pend_concluido = ''
                    # (assoc, id_xman, data_criado, categoria, estado, memo, data_resolvido)

                    # n_assoc, id_man, data_p_criado, cat_select, estado_select, memo, data_pend_concluido
                    add_pendente(n_assoc, id_man, data_p_criado, cat_select,
                                 estado_select, memo, data_pend_concluido)
                    st.write("Adicionado Registo \n ", "Assoc : ", n_assoc, "ID_XMAN : ",
                             id_man, "Data Criado : ", data_p_criado, "Categoria : ", cat_select, "Estado : ",
                             estado_select, "Memo : ", memo, "Concluído em : ", data_pend_concluido, "/")
                    st.experimental_rerun()

            elif opcao_pendentes == 'Visualizar / Editar':
                sql_query = st.radio('Listar :', ['Por Fechar', 'Concluídos'])
                if sql_query == 'Por Fechar':
                    hist_pendentes = read_pendentes(n_assoc)
                    hist_pendentes_rs = pd.DataFrame(hist_pendentes, columns=[
                        'ID', 'Assoc', 'ID_XMan', 'Data Criado', 'Categoria',
                        'Estado', 'Memo', 'Gravidade',
                        'Resolvido Em:'])
                    st.dataframe(hist_pendentes_rs)
                    lista_tarefa = [i[0] for i in read_pendentes(n_assoc)]
                    tarefa_escolhida = st.selectbox(
                        "Id Pendente :", lista_tarefa)
                    resultado_tarefa = get_tarefa(tarefa_escolhida)

                elif sql_query == 'Concluídos':
                    hist_pendentes = read_pendentes_fechados(n_assoc)
                    hist_pendentes_rs = pd.DataFrame(hist_pendentes, columns=[
                        'ID', 'Assoc', 'ID_XMan', 'Data Criado', 'Categoria',
                        'Estado', 'Memo', 'Gravidade',
                        'Resolvido Em:'])
                    st.dataframe(hist_pendentes_rs)
                    lista_tarefa = [i[0]
                                    for i in read_pendentes_fechados(n_assoc)]
                    tarefa_escolhida = st.selectbox(
                        "Id Pendente :", lista_tarefa)
                    resultado_tarefa = get_tarefa(tarefa_escolhida)
                if resultado_tarefa:
                    task_data_criado = resultado_tarefa[0][3]  # Data Criado
                    task_categoria = resultado_tarefa[0][4]  # Categoria
                    int_categoria = resultado_tarefa[0][4]
                    index_val_cat = int_categoria - 1
                    task_estado = resultado_tarefa[0][5]  # Estado
                    int_estado = resultado_tarefa[0][5]
                    index_val_estado = int_estado - 1
                    task_memo = resultado_tarefa[0][6]  # Memo
                    # Converter datas
                    task_data_resolvido = resultado_tarefa[0][7]

                    dia_tarefa_criada = datetime.strptime(
                        task_data_criado, formato_dia).date()
                    if task_data_resolvido == "":
                        dia_tarefa_resolvida = date.today()
                        # st.write(dia_tarefa_resolvida)
                    else:
                        dia_tarefa_resolvida = datetime.strptime(
                            task_data_resolvido, formato_dia).date()

                    cat_pendente = read_cat_pendente()
                    df_cat_pendente = pd.DataFrame(cat_pendente, columns=[
                        'id', 'Categoria'])
                    categoria = df_cat_pendente['Categoria'].tolist()
                    id_cat = df_cat_pendente['id'].tolist()
                    dic_cat = dict(zip(id_cat, categoria))

                    estado_pendente = read_estado_pendente()
                    df_est_pendente = pd.DataFrame(estado_pendente, columns=[
                        'id', 'Estado'])
                    estado = df_est_pendente['Estado'].tolist()
                    id_est = df_est_pendente['id'].tolist()
                    dic_est = dict(zip(id_est, estado))

                    colu1, colu2, colu3 = st.columns(3)

                    with colu1:
                        task_criada = st.date_input(
                            "Criado : ", dia_tarefa_criada)
                        task_resolvido = st.date_input(
                            "Resolvido : ", dia_tarefa_resolvida)

                    with colu2:
                        cat_select = st.selectbox(
                            'Categoria : ', id_cat, format_func=lambda x: dic_cat[x], index=index_val_cat)
                        estado_select = st.selectbox(
                            'Estado : ', id_est, format_func=lambda x: dic_est[x], index=index_val_estado)

                    with colu3:
                        task_memo = st.text_area(
                            "Memo", task_memo,  max_chars=80)
                        grava_pendente = st.button('Gravar Alterações')
                        if grava_pendente:
                            if estado_select != 2:
                                task_resolvido = ''

                            st.write(task_criada, cat_select, estado_select,
                                     task_memo, task_resolvido, tarefa_escolhida)
                            upd_pendente(task_criada, cat_select, estado_select,
                                         task_memo, task_resolvido, tarefa_escolhida)
                            st.experimental_rerun()
    else:
        st.write(
            'Não foi encontrada a data da última manutenção !')
        st.write(
            'Informe o SYS.ADMIN afim de criar o registo!')
