import sqlite3

conn = sqlite3.connect('mapa_visitas.db', check_same_thread=False)
c = conn.cursor()
a = 11
b = 23
linhas = 0
qr_drop = "drop table if exists t_manu"
c.execute(qr_drop)
conn.commit()
qr_create = 'CREATE TABLE IF NOT EXISTS t_manu("id" INTEGER NOT NULL,"assoc"	TEXT, "modelo" TEXT, "data_fecho" TEXT, "data_real"	TEXT, "tec_atrib" TEXT, "tec_real" TEXT, PRIMARY KEY("id" AUTOINCREMENT)) '
c.execute(qr_create)
conn.commit


def gen_query():
    dtprev = ("d" + str(quad) + "q" + str(year))
    dtreal = ("r" + str(quad) + "q" + str(year))
    tec = ("t" + str(quad) + "q" + str(year))
    query = ('select assoc, modelo, ' +
             'date(' +
             'substr(' + str(dtprev) + ', 7, 4)||"-"||' +
             'substr(' + str(dtprev) + ', 4, 2)||"-"||' +
             'substr(' + str(dtprev) + ', 1, 2)) as dt_prev, ' +
             'date(' +
             'substr(' + str(dtreal) + ',7,4)||"-"||' +
             'substr(' + str(dtreal) + ',4,2)||"-"||' +
             'substr(' + str(dtreal) + ',1,2)) as dt_real, ' + str(tec) + ' ' +
             'from t_clientes where ' + str(tec) + ' not NULL')
    c.execute(query)
    query_insert = (
        "INSERT INTO t_manu(assoc,modelo,data_fecho,data_real,tec_atrib) " +
        query
    )
    print(query_insert)
    c.execute(query_insert)
    return(str(query))


for year in range(a, b):
    if year == 11:
        quad = 3
        query = gen_query()
        year = year + 1
    elif year > 11 and year < 22:
        for quad in range(1, 4):
            query = gen_query()
    if year == 22:
        quad = 1
        query = gen_query()
        year = year + 1

conn.commit()
print('Adicionadas  :', str(linhas), 'Terminado')
