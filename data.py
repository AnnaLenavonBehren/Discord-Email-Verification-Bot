import sqlite3
from sqlite3 import Error
import discord
import secrets

def generate_token():
    return str(secrets.token_urlsafe(16))


# initially
def create_database(db):
    conn = sqlite3.connect(db)
    sql_anweisung = """
            CREATE TABLE IF NOT EXISTS personen (
                id INTEGER, 
                username VARCHAR(20), 
                email VARCHAR(30), 
                token VARCHAR(40), 
                verified VARCHAR(20), 
                PRIMARY KEY (id));"""
    cursor = conn.cursor()
    cursor.execute(sql_anweisung)
    conn.close()    

# on join
def create_entry(db, member):
    conn = sqlite3.connect(db)
    new_student = """INSERT OR IGNORE INTO personen (id) VALUES (?);"""
    personal_inf = """UPDATE personen SET username = ?, verified = ? WHERE id = ?;"""
    

    try:
        cursor = conn.cursor()
        cursor.execute(new_student, (member.id, ))
        conn.commit()
        cursor.execute(personal_inf, (member.name, "not verified", member.id))
        conn.commit()
        #print("record added successfully")

    except Error as e:
        print("error in query")
        conn.rollback()
        return

    conn.close()

def add_email(db, member, email):
    conn = sqlite3.connect(db)
    qry = """UPDATE personen SET email = ?, token = ?, verified = ? WHERE id = ?;"""
    token = generate_token()

    try:
        cursor = conn.cursor()
        cursor.execute(qry, (email, token, "not verified", member.id))
        conn.commit()
        #print("email updated successfully")

    except Error as e:
        print("error in query")
        conn.rollback()
        return

    conn.close()


def get_token(db, member):
    conn = sqlite3.connect(db)
    qry = """SELECT token from personen WHERE id = ?;"""

    try:
        cursor = conn.cursor()
        cursor.execute(qry, (member.id,))
        token = cursor.fetchall()
        token = token[0][0]
        conn.close()
        return token

    except Error as e:
        print("token not received")
        conn.rollback()
        conn.close()
        return None


def verify(db, member, role):
    conn = sqlite3.connect(db)
    qry = """UPDATE personen SET verified = ? WHERE id = ?;"""

    try:
        cursor = conn.cursor()
        cursor.execute(qry, (role, member.id))
        conn.commit()

    except Error as e:
        print("error in query")
        conn.rollback()
        return

    conn.close()

def update_roles(db, member):
    highest_prio_role = member.roles[-1].name
    if highest_prio_role == "@everyone":
        highest_prio_role = ""
    
    conn = sqlite3.connect(db)
    qry = """UPDATE personen SET verified = ? WHERE id = ?;"""

    try:
        cursor = conn.cursor()
        cursor.execute(qry, (highest_prio_role, member.id))
        conn.commit()

    except Error as e:
        print("error in query")
        conn.rollback()
        return

    conn.close()


def email_occupied(db, email):
    conn = sqlite3.connect(db)
    qry = """SELECT email from personen WHERE email = ?;"""

    try:
        cursor = conn.cursor()
        cursor.execute(qry, (email,))
        email = cursor.fetchall()
        
        conn.close()

        if email:
            return True
        else:
            return False

    except Error as e:
        print("error in query")
        conn.rollback()
        
        return None
    
    


def remove_entry(db, member):
    conn = sqlite3.connect(db)
    qry = """DELETE from personen WHERE id = ?;"""

    try:
        cursor = conn.cursor()
        cursor.execute(qry, (member.id,))
        conn.commit()

    except Error as e:
        print("error in query")
        conn.rollback()
        return

    conn.close()