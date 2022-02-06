import sqlite3

conn = sqlite3.connect('mapa_visitas.db', check_same_thread=False)
c = conn.cursor()


def read_tec():
    query = "Select tec_completo,tec_sigla from t_tecs order by tec_completo Desc"
    c.execute(query)
    tec_escolhido = c.fetchall()
    return tec_escolhido


def get_tecs():
    query = "Select * from t_tecs order by tec_completo Desc"
    c.execute(query)
    get_tec = c.fetchall()
    return get_tec


def default_pass_user(default_pass, next_logon, tec_select):
    query = "UPDATE t_tecs set password = ?, pass_next_logon = ? where id = ? "
    c.execute(query, (default_pass, next_logon, tec_select))
    updt_to_default_pass_tec = c.fetchall
    conn.commit()
    return updt_to_default_pass_tec


def upt_pass(uptdated_pass, username):
    query = "UPDATE t_tecs set password = ?, pass_next_logon = 'False' where username = ? "
    c.execute(query, (uptdated_pass, username))
    updt_pass_tec = c.fetchall
    conn.commit()
    return updt_pass_tec


def read_clients():
    query = "SELECT * From q_clix where cat  like '%sim%' or cat like '%parcial%'"
    c.execute(query)
    dados_clix = c.fetchall()
    return dados_clix


def read_man(username):
    query = "SELECT assoc, cliente, localidade, modelo, dt_fecho_xman, tec_atrib \
        from q_xman_deltas \
        where data_real is null \
        and tec_atrib like '%" + username + "%'\
        order by dt_fecho_xman, localidade, cliente "
    c.execute(query)
    dados = c.fetchall()
    return dados


def read_man_quad(username):
    query = "SELECT assoc, cliente, localidade, modelo, dt_fecho_xman, tec_atrib, \
        case \
        when strftime('%m', date(dt_fecho_xman)) BETWEEN '01' and '04' then 'Q1 - '||strftime('%Y', date(dt_fecho_xman)) \
        when strftime('%m', date(dt_fecho_xman)) BETWEEN '04' and '08' then 'Q2 - '||strftime('%Y', date(dt_fecho_xman)) \
        when strftime('%m', date(dt_fecho_xman)) BETWEEN '09' and '12' then 'Q3 - '||strftime('%Y', date(dt_fecho_xman)) \
        end \
        as Quad \
        from q_xman_deltas \
        where data_real is null \
        and tec_atrib like '%" + username + "%' \
        order by dt_fecho_xman, localidade, cliente "
    c.execute(query)
    dados = c.fetchall()
    return dados


def ler_cliente(escolher_cliente):
    query = "SELECT distinct assoc FROM q_clix \
            where cliloc like '%" + escolher_cliente + "%'"
    c.execute(query)
    clix = c.fetchall()
    return clix


def read_manut(n_assoc):
    query = "SELECT id, assoc, modelo, \
        dt_fecho_xman, data_real, \
        tec_atrib, tec_real \
        FROM q_xman_deltas where assoc = '{}'\
        and data_real is null"

    c.execute(query.format(n_assoc))
    manut = c.fetchall()
    return manut


def read_hist_manut(n_assoc):
    query = "SELECT id, assoc, modelo, data_fecho, data_real, tec_atrib, tec_real \
                FROM t_manu \
                where assoc = '{}' \
                and data_real not  null "
    c.execute(query.format(n_assoc))
    hist_manut = c.fetchall()
    return hist_manut


def upd_xman(pick_day, tec_efec, id_man):
    query = "UPDATE t_manu set data_real = ?, tec_real = ? where id = ? "
    c.execute(query, (pick_day, tec_efec, id_man))
    upt_manut = c.fetchall
    conn.commit()
    return upt_manut


def add_xman(n_assoc, modelo, data_fecho, tec_atrib):
    c.execute('INSERT INTO t_manu(assoc,modelo,data_fecho,tec_atrib) VALUES (?,?,?,?)',
              (n_assoc, modelo, data_fecho, tec_atrib))
    conn.commit()


def add_userdata(tec_completo, tec_sigla, base, job_grade, lon, lat, password, username, pass_next_logon):
    query = "INSERT INTO t_tecs(\
        tec_completo, tec_sigla, base, \
        job_grade, lon, lat, \
        password, username, pass_next_logon) \
        VALUES (?,?,?,?,?,?,?,?,?)"
    # 'INSERT INTO t_tecs(username,password) VALUES (?,?)'
    c.execute(query,
              (tec_completo, tec_sigla, base, job_grade, lon, lat, password, username, pass_next_logon))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM t_tecs WHERE username =? AND password = ?',
              (username, password))
    data = c.fetchall()
    return data


def read_pendentes(n_assoc):
    query = "SELECT A.id, A.assoc, A.id_xman, \
            A.data_criado, B.categoria, C.estado, \
            A.memo, B.gravidade, A.data_resolvido \
            from t_pendentes A  \
            left join t_cat_pendentes B on A.categoria = B.id \
            left join t_est_pendentes C on A.estado = C.id \
            Where assoc = '{}' and C.estado not like '%Conclu%'  "

    c.execute(query.format(n_assoc))
    hist_pendentes = c.fetchall()
    return hist_pendentes


def read_pendentes_fechados(n_assoc):
    query = "SELECT A.id, A.assoc, A.id_xman, \
            A.data_criado, B.categoria, C.estado, \
            A.memo, B.gravidade, A.data_resolvido \
            from t_pendentes A  \
            left join t_cat_pendentes B on A.categoria = B.id \
            left join t_est_pendentes C on A.estado = C.id \
            Where assoc = '{}' and C.estado like '%Conclu%' "

    c.execute(query.format(n_assoc))
    hist_pendentes_fechados = c.fetchall()
    return hist_pendentes_fechados


def get_tarefa(id):
    c.execute('SELECT * FROM t_pendentes WHERE id="{}"'.format(id))
    tsk = c.fetchall()
    return tsk


def get_pendente():
    query = "SELECT DISTINCT id, memo FROM t_pendentes "  # where assoc = '{}'"
    c.execute(query)
    tasks_pendentes = c.fetchall
    return tasks_pendentes


def add_pendente(n_assoc, id_man, data_p_criado, cat_select, estado_select, memo, data_pend_concluido):
    query = "INSERT INTO \
        t_pendentes(assoc, id_xman, data_criado, categoria, estado, memo, data_resolvido) \
        VALUES (?,?,?,?,?,?,?)"
    c.execute(query,
              (n_assoc, format(id_man), data_p_criado, cat_select, estado_select, memo, data_pend_concluido))
    conn.commit()


def upd_pendente(task_criada, cat_select, estado_select, task_memo, task_resolvido, tarefa_escolhida):
    # select id, assoc, id_xman, data_criado, categoria, estado, memo, data_resolvido  from t_pendentes
    query = "UPDATE t_pendentes set data_criado = ?,  categoria = ?, estado = ?, memo = ?, data_resolvido = ?  where id = ? "
    c.execute(query, (task_criada, cat_select, estado_select,
              task_memo,  task_resolvido, tarefa_escolhida))
    updt_pendente = c.fetchall
    conn.commit()
    print(task_criada, task_resolvido, cat_select,
          estado_select, task_memo, tarefa_escolhida)
    return updt_pendente


def read_cat_pendente():
    query = "SELECT id, categoria FROM t_cat_pendentes order by id"
    c.execute(query)
    cat_pendente = c.fetchall()
    return cat_pendente


def read_estado_pendente():
    query = "SELECT id, estado FROM t_est_pendentes"
    c.execute(query)
    est_pendente = c.fetchall()
    return est_pendente
