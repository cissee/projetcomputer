
"""Le code initialise une base de données SQLite nommée 
`security.db` avec deux tables : `users` (pour stocker les informations des utilisateurs, 
y compris leur encodage facial) et `access_logs` (pour enregistrer les tentatives d'accès). 
La fonction `init_db` crée ces tables si elles n'existent pas déjà, tandis que `get_connection` 
permet d'obtenir une connexion à la base de données. La base est initialisée au lancement du script."""

import sqlite3

def init_db():
    conn = sqlite3.connect("security.db")
    cursor = conn.cursor()
    
    # Création des tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        role TEXT,
                        encoding BLOB)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS access_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        status TEXT,
                        timestamp TEXT)''')

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("security.db")

# Initialiser la base au lancement
init_db()
