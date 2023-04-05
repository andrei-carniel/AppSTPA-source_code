import sqlite3
from sqlite3 import Error

import Constant
from Objects.Responsibility import Responsibility, Responsibility_ssc


# make a connection


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(Constant.DB_FILE)
    except Error as e:
        print(e)

    return conn


# create all tables if not exists
def create_table_responsibility():
    return "CREATE TABLE IF NOT EXISTS responsibility (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT NOT NULL, id_project INTEGER NOT NULL, " \
                                        "id_screen INTEGER NOT NULL, id_controller INTEGER NOT NULL, " \
                                        "FOREIGN KEY(id_project) REFERENCES projects(id) " \
                                        "FOREIGN KEY(id_controller) REFERENCES components(id));"


# create all tables if not exists
def create_table_responsibility_ssc():
    return "CREATE TABLE IF NOT EXISTS responsibility_ssc (id INTEGER PRIMARY KEY AUTOINCREMENT, id_responsibility INTEGER NOT NULL, " \
                                          "id_constraint INTEGER NOT NULL, " \
                                          "FOREIGN KEY(id_responsibility) REFERENCES responsibility(id) " \
                                          "FOREIGN KEY(id_constraint) REFERENCES safety_constraints(id) );"


# insert one register to Table Safety Constraints
def insert_to_responsibility(resp):

    # create a database connection
    conn = create_connection()
    with conn:
        sql = "INSERT INTO responsibility(description, id_project, id_screen, id_controller) VALUES(?, ?, ?, ?)"
        cur = conn.cursor()
        task = (resp.description, resp.id_project, resp.id_screen, resp.id_controller)
        result = cur.execute(sql, task)
        id_resp = result.lastrowid
        conn.commit()

        for list_ssc in resp.list_of_ssc:
            list_ssc.id_responsibility = id_resp
            insert_to_responsibility_ssc(list_ssc)

        return cur.lastrowid


# insert one register to Table Hazards
def insert_to_responsibility_ssc(list_ssc):
    # create a database connection
    conn = create_connection()
    with conn:
        sql = "INSERT INTO responsibility_ssc(id_responsibility, id_constraint) VALUES(?, ?)"

        cur = conn.cursor()
        task = (list_ssc.id_responsibility, list_ssc.id_constraint)
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid


# update one register to Table Goals
def update_responsibility(resp):
    # create a database connection
    conn = create_connection()
    with conn:
        sql = "UPDATE responsibility SET description = ? WHERE id = ?"
        cur = conn.cursor()
        task = (resp.description, resp.id)
        cur.execute(sql, task)

        cur.execute("DELETE FROM responsibility_ssc WHERE id_responsibility = ?", (resp.id,))
        sql = "INSERT INTO responsibility_ssc(id_responsibility, id_constraint) VALUES(?, ?)"

        for ssc in resp.list_of_ssc:
            cur = conn.cursor()
            task = (resp.id, ssc.id_constraint)
            cur.execute(sql, task)

        conn.commit()
        return cur.lastrowid


def delete_responsibility(resp):
    # create a database connection
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM responsibility WHERE id = ?", (resp.id,))
        conn.commit()
        delete_responsibility_ssc(resp)
        update_responsibility_id(resp.id_project)
        return cur.lastrowid


def delete_responsibility_ssc(ssc):
    # create a database connection
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM responsibility_ssc WHERE id_responsibility = ?", (ssc.id,))
        conn.commit()
        return cur.lastrowid

# insert one register to Table Loss
def update_responsibility_id(id_project):
    # create a database connection
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM responsibility WHERE id_project = ?", (id_project,))
        rows = cur.fetchall()
        count = 1
        for row in rows:
            cur.execute("UPDATE responsibility SET id_screen = ? WHERE id = ?", (count, row[0],))
            count += 1
        conn.commit()

def delete_responsibility_by_controller(id_controller):
    # create a database connection
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM responsibility WHERE id_controller = ?", (id_controller,))
        rows = cur.fetchall()
        for row in rows:
            cur.execute("DELETE FROM responsibility_ssc WHERE id_responsibility = ?", (row[0],))
        cur.execute("DELETE FROM responsibility WHERE id_controller = ?", (id_controller,))
        conn.commit()

def select_all_responsibilities_by_controller(id_controller):
    result_list = []

    # create a database connection
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, description, id_project, id_screen, id_controller FROM responsibility WHERE id_controller = ?", (id_controller,))

        rows = cur.fetchall()

        for row in rows:
            resp = Responsibility(row[0], row[1], row[2], row[3], row[4], [])

            cur.execute("SELECT r.id, r.id_responsibility, r.id_constraint, sf.id_safety_constraint FROM responsibility_ssc AS r "
                        "JOIN safety_constraints AS sf ON sf.id = r.id_constraint "
                        "WHERE id_responsibility = ?", (row[0],))

            rows_ssc = cur.fetchall()
            result_ssc_list = []
            for row_ssc in rows_ssc:
                result_ssc_list.append(Responsibility_ssc(row_ssc[0], row_ssc[1], row_ssc[2], row_ssc[3]))

            resp.list_of_ssc = result_ssc_list
            result_list.append(resp)



    return result_list


# select all hazards by id_project and id_loss
def check_control_structure(id_project):
    """
    Query tasks by all rows
    :return: List of Goals
    """
    result_list = []

    # create a database connection
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT r.id, r.description, r.id_project, r.id_screen, r.id_controller, c.name FROM responsibility AS r "
                    "JOIN components AS c on c.id = r.id_controller "
                    "WHERE r.id_project = ?", (id_project,))

        rows = cur.fetchall()

        for row in rows:
            cur.execute("SELECT count(id) FROM responsibility_ssc WHERE id_responsibility = ?", (row[0],))
            row_c = cur.fetchone()
            if row_c != None:
                if row_c[0] == 0:
                    result_list.append("R-" + str(row[3]) + ": " + row[1] + " (" + row[5] + ")")

    return result_list
