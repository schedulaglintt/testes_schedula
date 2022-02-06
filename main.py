# from asyncio.windows_events import NULL
# from faulthandler import cancel_dump_traceback_later
from os import read
from time import strftime

from unittest import TestCase
import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import datetime
from datetime import date, datetime, timedelta
import calendar
import hashlib

from db_function import *
from xman import *


# Define titulo da página
st.set_page_config(
    page_title="Schedula - Mundus in manibus tuis ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# constante converter formato de datas gravadas na  bd sqlite para python
formato_dia = '%Y-%m-%d'


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


def main():

    # retirar coluna do indice do st.dataframe
    hide_dataframe_row_index = """
    <style>
    .row_heading.level0 {display:none}
    .blank {display:none}
    </style>"""

    st.markdown(hide_dataframe_row_index,
                unsafe_allow_html=True)

    ###################################################################################

    # create_table()
    menu = ["DashBoard", "Login"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "DashBoard":
        st.subheader("DashBoard")
        # Colocar aqui dashboard
        ###################################################################################
    elif choice == "Login":

        username = st.sidebar.text_input("User")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            default = 'abc123'
            default_pass = make_hashes(default)

            hashed_pswd = make_hashes(password)
            result = login_user(username, check_hashes(password, hashed_pswd))
            if result:
                df_loged = pd.DataFrame(result, columns=['id', 'tec_completo',
                                                         'tec_sigla', 'base', 'job_grade',
                                                         'lon', 'lat', 'password', 'username', 'next_log_on'])
                force_pass = df_loged.values[0][9]
                if force_pass == 'True':
                    if hashed_pswd == default_pass:
                        st.write('Detetada password de defeito!')
                        nova_pass = st.text_input(
                            "Indique Nova PassWord : ", type='password')
                        if len(nova_pass) > 0:
                            repeat_pass = st.text_input(
                                "Repita a PassWord : ", type='password')
                            if nova_pass != repeat_pass:
                                st.warning('PassWord não coincide !!!')
                            else:
                                submit_pass = st.button('Atualizar Password')
                                if submit_pass:
                                    uptdated_pass = make_hashes(nova_pass)
                                    upt_pass(uptdated_pass, username)
                                    st.experimental_rerun()
                if force_pass == 'False':
                    #    st.success("Utilizador : {}".format(username))
                    tec = username
                    #    st.write(tec)
                    if username != 'admin':
                        main_menu = st.selectbox(
                            "Escolha uma opção :  ", ["Ver", "Regularizar XMAN", "Estatística"])
                    else:
                        st.warning('ESTÁ EM MODO DE ADMINISTRAÇÃO!!!! ')
                        main_menu = st.selectbox(
                            "Escolha uma opção : ", ["Ver", "Regularizar XMAN", "Estatística", "Editar Dados", "Criar Novo Utilizador", "Reset Password de um User"])

                    if main_menu == "Regularizar XMAN":
                        reg_xman(username)

                    elif main_menu == "Estatística":
                        st.subheader("Estatística")

                    elif main_menu == "Ver":
                        st.subheader("Lista de Manutenções Pendentes")
                        if tec == 'admin':
                            username = ''
                        man_result = read_man_quad(username)

                        clean_db = pd.DataFrame(man_result, columns=[
                            "Assoc", "Cliente", "Localidade",
                            "Modelo", "Data Final", "Tec.Atrib", "Quad"])
                        st.dataframe(clean_db)
                    elif main_menu == "Editar Dados":
                        st.write('EDITAR TABELAS DE DADOS!!!!!!!!!!!')

                    elif main_menu == "Reset Password de um User":
                        st.write('Reset de Password de um user')
                        SYS_ADMIN = st.text_input(
                            "Digite a Password de SYS.ADMIN", type='password')
                        if SYS_ADMIN == "SudoRootAdmin":
                            st.subheader("Reset Password de Utilizador")

                            tecs = get_tecs()
                            df_tecs = pd.DataFrame(
                                tecs, columns=['id', 'tec_completo',
                                               'tec_sigla', 'base', 'job_grade',
                                               'lon', 'lat', 'password', 'username', 'next_log_on'])

                            tec_nome_completo = df_tecs['tec_completo'].tolist(
                            )
                            id_tec = df_tecs['id'].tolist()
                            dic_tecs = dict(zip(id_tec, tec_nome_completo))

                            tec_select = st.selectbox(
                                'Utilizador : ', id_tec, format_func=lambda x: dic_tecs[x])
                            st.write(tec_select)
                            reset_p = st.button(
                                'Anular password deste utilizador')
                            if reset_p and tec_select != 8:
                                st.write('Password Anulada',
                                         'Utilize a PassWord de defeito')
                                default = 'abc123'
                                next_logon = 'True'
                                default_pass = make_hashes(default)
                                default_pass_user(
                                    default_pass, next_logon, tec_select)
                                st.experimental_rerun()
                            elif reset_p and tec_select == 8:
                                st.warning(
                                    'Não É Permitido Modificar, Alterar ou Apagar A Conta Admin!')
                        else:
                            st.write("Password Inválida!")

                    elif main_menu == "Criar Novo Utilizador":

                        SYS_ADMIN = st.text_input(
                            "Digite a Password de SYS.ADMIN", type='password')
                        if SYS_ADMIN == "SudoRootAdmin":
                            st.subheader("Criar Novo Utilizador")
                            new_username = st.text_input(
                                "Username (2 Char) :", max_chars=2)
                            new_tec_completo = st.text_input(
                                "Nome e Apelido (25 Char) :", max_chars=25)
                            new_tec_sigla = st.text_input(
                                "Username (2 Char em CAPS) :", max_chars=2)
                            new_base = st.text_input(
                                "Base (8 Char) :", max_chars=8)
                            new_job_grade = st.text_input(
                                "Job_Grade (5 Char) :", max_chars=5)
                            new_lon = st.text_input(
                                "Longitude : ", max_chars=7)
                            new_lat = st.text_input("Latitude : ", max_chars=7)
                            pass_next_logon = 'True'

                            default = 'abc123'
                            default_pass = make_hashes(default)
                            if st.button("Criar"):
                                st.write('Criar')
                                # create_usertable()
                                add_userdata(
                                    new_tec_completo, new_tec_sigla, new_base, new_job_grade, new_lon, new_lat, default_pass, new_username, pass_next_logon
                                )
                                st.write(new_tec_completo, new_tec_sigla, new_base, new_job_grade,
                                         new_lon, new_lat, default_pass, new_username, pass_next_logon)
                                st.success("Foi criado um novo Utilizador")
                                st.info("Escolha a Opção LogIn!!!!")
                        else:
                            st.write("Password Inválida!")
            else:
                st.warning("Acesso Negado! Verifique Username/Password")


if __name__ == '__main__':
    main()
