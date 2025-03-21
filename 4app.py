import sys
import os
import cv2
import face_recognition
import pickle
import sqlite3
import hashlib
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QInputDialog, QFileDialog, QTextEdit
)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import QTimer, QDateTime, Qt
from smtplib import SMTP

"""La classe `FaceAuthenticationApp` est une application PyQt6 qui implémente un système 
d'authentification sécurisé basé sur la reconnaissance faciale et un code PIN. Elle gère
une base de données SQLite pour les utilisateurs, une interface graphique intuitive, 
et une caméra pour la reconnaissance faciale en temps réel."""

class FaceAuthenticationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système d'Authentification Sécurisé")
        self.setGeometry(100, 100, 800, 700)  # Taille de la fenêtre augmentée

        # Base de données des utilisateurs
        self.users_db = "users.db"
        self.create_users_db()

        # Chargement des utilisateurs autorisés
        self.known_encodings = self.load_known_faces()

        # Variables d'authentification
        self.current_user = None
        self.role = None
        self.pincode = None

        # Interface utilisateur
        self.init_ui()

        # Configurations de la caméra
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        
    """La méthode `init_ui` initialise l'interface utilisateur de l'application, 
    comprenant un titre, une zone d'affichage pour la caméra, des champs de saisie
    pour l'identifiant et le code PIN, ainsi que des boutons pour démarrer/arrêter 
    la caméra, se connecter, se déconnecter, s'inscrire, accéder au mode administrateur,
    utiliser la messagerie et télécharger une image. Les éléments sont stylisés avec des 
    couleurs et des polices spécifiques pour une meilleure expérience utilisateur."""

    def init_ui(self):
        """Initialisation de l'interface utilisateur"""
        # Titre
        title_label = QLabel("Système d'Authentification Faciale", self)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50; padding: 10px;")

        # Caméra
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(640, 480)  # Taille de la caméra augmentée
        self.image_label.setStyleSheet("border: 2px solid #34495E; border-radius: 10px; background-color: black;")

        # Statut
        self.result_label = QLabel("Statut : En attente...", self)
        self.result_label.setFont(QFont("Arial", 12))
        self.result_label.setStyleSheet("padding: 10px; background-color: #34495E; color: white; border-radius: 5px;")

        # Champs de saisie
        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText("Entrer l'identifiant")
        self.id_input.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #34495E;")

        self.pincode_input = QLineEdit(self)
        self.pincode_input.setPlaceholderText("Entrer le code PIN")
        self.pincode_input.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #34495E;")
        self.pincode_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Boutons
        self.btn_start = QPushButton("Démarrer Caméra", self)
        self.btn_start.setStyleSheet("background-color: #27AE60; padding: 10px; border-radius: 5px; color: white;")
        self.btn_start.clicked.connect(self.start_camera)

        self.btn_stop = QPushButton("Arrêter Caméra", self)
        self.btn_stop.setStyleSheet("background-color: #E74C3C; padding: 10px; border-radius: 5px; color: white;")
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_stop.setEnabled(False)

        self.login_button = QPushButton("Se connecter", self)
        self.login_button.setStyleSheet("background-color: #2980B9; padding: 10px; border-radius: 5px; color: white;")
        self.login_button.clicked.connect(self.validate_access)

        self.logout_button = QPushButton("Se déconnecter", self)
        self.logout_button.setStyleSheet("background-color: #E67E22; padding: 10px; border-radius: 5px; color: white;")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setEnabled(False)

        self.register_button = QPushButton("S'inscrire", self)
        self.register_button.setStyleSheet("background-color: #8E44AD; padding: 10px; border-radius: 5px; color: white;")
        self.register_button.clicked.connect(self.show_registration_form)

        self.admin_button = QPushButton("Admin", self)
        self.admin_button.setStyleSheet("background-color: #2C3E50; padding: 10px; border-radius: 5px; color: white;")
        self.admin_button.clicked.connect(self.show_admin_login)

        self.messaging_button = QPushButton("Messagerie", self)
        self.messaging_button.setStyleSheet("background-color: #3498DB; padding: 10px; border-radius: 5px; color: white;")
        self.messaging_button.clicked.connect(self.show_messaging_window)
        self.messaging_button.setEnabled(False)

        self.upload_button = QPushButton("Télécharger une image", self)
        self.upload_button.setStyleSheet("background-color: #16A085; padding: 10px; border-radius: 5px; color: white;")
        self.upload_button.clicked.connect(self.upload_image)

        # Layout
        main_layout = QVBoxLayout()

        # Titre
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Caméra
        main_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Statut
        main_layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Champs de saisie
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.id_input)
        input_layout.addWidget(self.pincode_input)
        main_layout.addLayout(input_layout)

        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.logout_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.admin_button)
        button_layout.addWidget(self.messaging_button)
        button_layout.addWidget(self.upload_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

"""La méthode `create_users_db` crée une base de données SQLite
avec trois tables principales : `users` (stocke les informations des utilisateurs, 
y compris les encodages faciaux et les rôles), `access_log` (enregistre les tentatives
d'accès avec leur succès ou échec), et `messages` (gère les messages échangés entre utilisateurs). 
Chaque table est conçue avec des champs spécifiques pour stocker des données structurées,
et des clés étrangères assurent l'intégrité des relations entre les tables.
La méthode garantit que les tables sont créées uniquement si elles n'existent pas déjà."""

def create_users_db(self):
        """Création de la base de données des utilisateurs"""
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    birthdate TEXT NOT NULL,
                    status TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    encoding BLOB NOT NULL,
                    role TEXT NOT NULL,
                    pincode TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    success INTEGER NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (sender_id) REFERENCES users (id),
                    FOREIGN KEY (receiver_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
            
"""La méthode `load_known_faces` charge les encodages faciaux des utilisateurs 
depuis la base de données SQLite et les stocke dans un dictionnaire (`encodings`). 
Elle récupère les données de la table `users`, désérialise les encodages (stockés sous forme binaire) 
à l'aide de `pickle`, et les associe à l'ID de l'utilisateur.
Ces encodages sont ensuite utilisés pour la reconnaissance faciale."""

def load_known_faces(self):
        """Charge les visages enregistrés depuis la base de données"""
        encodings = {}
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, encoding FROM users")
            rows = cursor.fetchall()

            for row in rows:
                user_id, encoding = row
                encodings[user_id] = pickle.loads(encoding)
                print(f"Encodage chargé pour l'utilisateur ID {user_id}")  # Log de débogage
        return encodings

def start_camera(self):
        """Démarre la caméra et la reconnaissance faciale"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Erreur", "Impossible d'ouvrir la caméra.")
            return
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.timer.start(30)

def stop_camera(self):
        """Arrête la caméra proprement"""
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.image_label.clear()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
"""La méthode `process_frame` capture une image depuis la caméra, 
la redimensionne et la convertit en RGB pour la reconnaissance faciale.
Elle détecte les visages dans l'image, génère leurs encodages, 
et les compare avec les encodages préenregistrés pour identifier les utilisateurs. 
Si une correspondance est trouvée (avec un seuil de similarité de 0.5), 
elle affiche le nom de l'utilisateur et dessine un rectangle autour du visage. 
Enfin, l'image traitée est affichée dans l'interface utilisateur."""

def process_frame(self):
        """Capture et traite les images pour la reconnaissance faciale"""
        ret, frame = self.cap.read()
        if not ret:
            return

        # Redimensionner l'image pour une meilleure précision
        frame = cv2.resize(frame, (640, 480))

        # Convertir en RGB pour la reconnaissance faciale
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Détecter les visages
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        print(f"Visages détectés : {len(face_locations)}")  # Log de débogage
        print(f"Encodages générés : {len(face_encodings)}")  # Log de débogage

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Comparer avec les encodages connus
            matches = face_recognition.compare_faces(list(self.known_encodings.values()), face_encoding, tolerance=0.5)
            name = "Inconnu"

            # Calculer les distances pour vérifier la similarité
            face_distances = face_recognition.face_distance(list(self.known_encodings.values()), face_encoding)
            print(f"Distances : {face_distances}")  # Affiche les distances pour chaque utilisateur enregistré

            if True in matches:
                # Trouver l'utilisateur avec la distance la plus faible
                best_match_index = face_distances.argmin()
                if face_distances[best_match_index] < 0.5:  # Seuil de similarité
                    user_id = list(self.known_encodings.keys())[best_match_index]
                    name = self.get_user_name(user_id)  # Récupérer le nom de l'utilisateur
                    print(f"Utilisateur reconnu : {name}")  # Log de débogage

            # Dessiner un rectangle autour du visage et afficher le nom
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, str(name), (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)  # Convertir name en str

        self.display_image(frame)
        
"""La méthode `display_image` convertit l'image capturée (au format BGR) en RGB, 
puis la transforme en un objet `QImage` pour l'affichage dans un `QLabel`.
L'image est ensuite affichée dans l'interface utilisateur à l'aide de `QPixmap`."""

def display_image(self, frame):
        """Affiche l'image capturée dans le QLabel"""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))
        
"""La méthode `validate_access` vérifie l'accès en comparant l'identifiant
et le code PIN saisis par l'utilisateur avec ceux stockés dans la base de données.
Si les informations correspondent, l'accès est accordé, et l'interface est mise à 
jour pour refléter l'authentification réussie. Sinon, un message d'erreur est affiché,
et la tentative d'accès est journalisée. En cas d'échec, une notification est envoyée 
pour signaler une tentative d'accès non autorisée."""

def validate_access(self):
        """Valide l'accès après reconnaissance faciale et code PIN"""
        entered_id = self.id_input.text().strip()
        entered_pincode = self.pincode_input.text().strip()

        if not entered_id or not entered_pincode:
            QMessageBox.critical(self, "Erreur", "Veuillez entrer un identifiant et un code PIN.")
            return

        # Hacher le code PIN entré pour le comparer avec celui stocké
        hashed_pincode = hashlib.sha256(entered_pincode.encode()).hexdigest()

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, role, pincode FROM users WHERE id = ?", (entered_id,))
            result = cursor.fetchone()

        if result:
            user_id, name, role, stored_pincode = result
            if hashed_pincode == stored_pincode:
                self.current_user = user_id
                self.role = role
                self.result_label.setText(f"✅ Accès accordé à {name} ({role})")
                self.log_access(True)
                self.login_button.setEnabled(False)
                self.logout_button.setEnabled(True)
                self.messaging_button.setEnabled(True)  # Activer la messagerie
            else:
                self.result_label.setText("❌ Code PIN incorrect")
                self.log_access(False)
                self.send_notification("Tentative d'accès échouée")
        else:
            self.result_label.setText("❌ Identifiant incorrect")
            self.current_user = None
            self.log_access(False)
            self.send_notification("Tentative d'accès échouée")

"""La méthode `logout` déconnecte l'utilisateur en réinitialisant les variables d'authentification,
en arrêtant la caméra, et en mettant à jour l'interface pour refléter l'état déconnecté. 
Les champs de saisie sont également vidés."""

def logout(self):
        """Déconnecte l'utilisateur"""
        self.stop_camera()  # Arrêter la caméra
        self.current_user = None
        self.role = None
        self.pincode = None  # Réinitialiser le code PIN
        self.result_label.setText("Statut : Déconnecté")
        self.login_button.setEnabled(True)
        self.logout_button.setEnabled(False)
        self.messaging_button.setEnabled(False)  # Désactiver la messagerie
        self.id_input.clear()  # Effacer le champ d'identifiant
        self.pincode_input.clear()  # Effacer le champ de code PIN

"""La méthode `log_access` enregistre une tentative d'accès (succès ou échec)
dans la base de données avec l'ID de l'utilisateur et un horodatage."""

def log_access(self, success):
        """Journalise la tentative d'accès"""
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            timestamp = QDateTime.currentDateTime().toString()
            cursor.execute("INSERT INTO access_log (user, timestamp, success) VALUES (?, ?, ?)",
                           (self.current_user, timestamp, success))
            conn.commit()
            
"""La méthode `send_notification` envoie une notification par email en utilisant
les informations SMTP configurées. Si les informations SMTP sont manquantes 
ou si l'envoi échoue, une erreur est affichée dans la console."""

def send_notification(self, message):
        """Envoie une notification par email ou SMS en cas d'accès non autorisé"""
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        smtp_to = os.getenv('SMTP_TO')

        if not smtp_user or not smtp_password or not smtp_to:
            print("Erreur: Les informations d'identification SMTP ne sont pas définies.")
            return

        try:
            server = SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, smtp_to, message)
            server.quit()
        except Exception as e:
            print("Erreur d'envoi de notification:", e)
            
"""La méthode `show_registration_form` crée une nouvelle 
fenêtre pour le formulaire d'inscription, comprenant des champs
de saisie pour les informations personnelles (nom, prénom, date de naissance, etc.)
et un code PIN. Elle inclut également un bouton pour capturer une image du visage 
de l'utilisateur et un bouton pour valider l'inscription. 
La fenêtre est organisée avec un layout vertical (`QVBoxLayout`) 
et affichée à l'utilisateur pour qu'il puisse saisir ses données."""

def show_registration_form(self):
        """Affiche le formulaire d'inscription"""
        self.registration_window = QWidget()
        self.registration_window.setWindowTitle("Formulaire d'inscription")
        self.registration_window.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.name_input = QLineEdit(self.registration_window)
        self.name_input.setPlaceholderText("Nom")
        layout.addWidget(self.name_input)

        self.surname_input = QLineEdit(self.registration_window)
        self.surname_input.setPlaceholderText("Prénom")
        layout.addWidget(self.surname_input)

        self.birthdate_input = QLineEdit(self.registration_window)
        self.birthdate_input.setPlaceholderText("Date de naissance (YYYY-MM-DD)")
        layout.addWidget(self.birthdate_input)

        self.status_input = QLineEdit(self.registration_window)
        self.status_input.setPlaceholderText("Statut")
        layout.addWidget(self.status_input)

        self.age_input = QLineEdit(self.registration_window)
        self.age_input.setPlaceholderText("Âge")
        layout.addWidget(self.age_input)

        self.gender_input = QLineEdit(self.registration_window)
        self.gender_input.setPlaceholderText("Sexe")
        layout.addWidget(self.gender_input)

        self.email_input = QLineEdit(self.registration_window)
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        self.phone_input = QLineEdit(self.registration_window)
        self.phone_input.setPlaceholderText("Numéro de téléphone")
        layout.addWidget(self.phone_input)

        self.pincode_input = QLineEdit(self.registration_window)
        self.pincode_input.setPlaceholderText("Code PIN")
        layout.addWidget(self.pincode_input)

        self.capture_button = QPushButton("Capturer Image", self.registration_window)
        self.capture_button.clicked.connect(self.capture_image)
        layout.addWidget(self.capture_button)

        self.register_button = QPushButton("S'inscrire", self.registration_window)
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)

        self.registration_window.setLayout(layout)
        self.registration_window.show()

"""La méthode `capture_image` capture une image depuis la caméra,
détecte un visage unique, et génère un encodage facial qui 
est ensuite sérialisé et stocké. Si la capture réussit,
un message de confirmation est affiché à l'utilisateur."""

def capture_image(self):
        """Capture l'image de l'utilisateur pour l'inscription"""
        if self.cap is None:
            self.start_camera()

        ret, frame = self.cap.read()
        if not ret:
            QMessageBox.critical(self, "Erreur", "Impossible de capturer l'image.")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if len(face_locations) != 1:
            QMessageBox.critical(self, "Erreur", "Veuillez vous assurer qu'un seul visage est visible.")
            return

        face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        self.captured_encoding = pickle.dumps(face_encoding)
        QMessageBox.information(self, "Succès", "Image capturée avec succès.")
        
"""La méthode `register_user` enregistre un nouvel utilisateur dans la base de données 
en insérant ses informations personnelles, son encodage facial et son code PIN haché. 
Après l'inscription, l'utilisateur est automatiquement connecté,
et un message de succès affiche son identifiant.
L'interface est mise à jour pour refléter l'authentification réussie."""

def register_user(self):
        """Enregistre un nouvel utilisateur dans la base de données"""
        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        birthdate = self.birthdate_input.text().strip()
        status = self.status_input.text().strip()
        age = int(self.age_input.text().strip())
        gender = self.gender_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        pincode = hashlib.sha256(self.pincode_input.text().strip().encode()).hexdigest()

        if not hasattr(self, 'captured_encoding'):
            QMessageBox.critical(self, "Erreur", "Veuillez capturer une image avant de vous inscrire.")
            return

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, surname, birthdate, status, age, gender, email, phone, encoding, role, pincode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, surname, birthdate, status, age, gender, email, phone, self.captured_encoding, "user", pincode))
            user_id = cursor.lastrowid  # Récupérer l'identifiant généré
            conn.commit()

        # Afficher l'identifiant à l'utilisateur
        QMessageBox.information(self, "Succès", f"Utilisateur enregistré avec succès. Votre identifiant est : {user_id}")
        self.registration_window.close()

        # Connecter l'utilisateur automatiquement après l'inscription
        self.current_user = user_id
        self.role = "user"
        self.pincode = pincode
        self.result_label.setText(f"✅ Accès accordé à {name} ({self.role})")
        self.log_access(True)
        self.login_button.setEnabled(False)
        self.logout_button.setEnabled(True)
        self.messaging_button.setEnabled(True)

def show_admin_login(self):
        """Affiche le formulaire de connexion administrateur"""
        self.admin_login_window = QWidget()
        self.admin_login_window.setWindowTitle("Connexion Administrateur")
        self.admin_login_window.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.admin_username_input = QLineEdit(self.admin_login_window)
        self.admin_username_input.setPlaceholderText("Identifiant")
        layout.addWidget(self.admin_username_input)

        self.admin_password_input = QLineEdit(self.admin_login_window)
        self.admin_password_input.setPlaceholderText("Mot de passe")
        self.admin_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.admin_password_input)

        self.admin_login_button = QPushButton("Se connecter", self.admin_login_window)
        self.admin_login_button.clicked.connect(self.admin_login)
        layout.addWidget(self.admin_login_button)

        self.admin_login_window.setLayout(layout)
        self.admin_login_window.show()

def admin_login(self):
        """Vérifie les informations d'identification administrateur et affiche le tableau de bord"""
        username = self.admin_username_input.text().strip()
        password = self.admin_password_input.text().strip()

        # Vérifiez les informations d'identification administrateur (remplacez par vos informations)
        if username == "admin" and password == "1224":
            self.admin_login_window.close()
            self.show_admin_dashboard()
        else:
            QMessageBox.critical(self, "Erreur", "Identifiant ou mot de passe incorrect.")
            
"""La méthode `show_admin_dashboard` crée et affiche une fenêtre dédiée au tableau de bord administrateur.
Cette fenêtre inclut un tableau pour afficher les utilisateurs, des boutons pour charger, ajouter,
mettre à jour, supprimer des utilisateurs, envoyer des messages, et une fonction de recherche par nom. 
L'interface est organisée avec un layout vertical (`QVBoxLayout`)."""

def show_admin_dashboard(self):
        """Affiche le tableau de bord administrateur"""
        self.admin_dashboard_window = QWidget()
        self.admin_dashboard_window.setWindowTitle("Tableau de Bord Administrateur")
        self.admin_dashboard_window.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.users_table = QTableWidget(self.admin_dashboard_window)
        self.users_table.setColumnCount(10)
        self.users_table.setHorizontalHeaderLabels(
            ["ID", "Nom", "Prénom", "Date de Naissance", "Statut", "Âge", "Sexe", "Email", "Téléphone", "Rôle"])
        layout.addWidget(self.users_table)

        self.load_users_button = QPushButton("Charger les utilisateurs", self.admin_dashboard_window)
        self.load_users_button.clicked.connect(self.load_users)
        layout.addWidget(self.load_users_button)

        self.add_user_button = QPushButton("Ajouter Utilisateur", self.admin_dashboard_window)
        self.add_user_button.clicked.connect(self.show_registration_form)
        layout.addWidget(self.add_user_button)

        self.update_user_button = QPushButton("Mettre à jour Utilisateur", self.admin_dashboard_window)
        self.update_user_button.clicked.connect(self.update_user_info)
        layout.addWidget(self.update_user_button)

        self.delete_user_button = QPushButton("Supprimer Utilisateur", self.admin_dashboard_window)
        self.delete_user_button.clicked.connect(self.delete_user)
        layout.addWidget(self.delete_user_button)

        self.message_button = QPushButton("Envoyer Message", self.admin_dashboard_window)
        self.message_button.clicked.connect(self.send_message)
        layout.addWidget(self.message_button)

        self.search_input = QLineEdit(self.admin_dashboard_window)
        self.search_input.setPlaceholderText("Rechercher utilisateur par nom")
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Rechercher", self.admin_dashboard_window)
        self.search_button.clicked.connect(self.search_user)
        layout.addWidget(self.search_button)

        self.admin_dashboard_window.setLayout(layout)
        self.admin_dashboard_window.show()
        
"""La méthode `load_users` récupère les informations des utilisateurs 
depuis la base de données et les affiche dans un tableau. 
Chaque ligne du tableau correspond à un utilisateur, 
et chaque colonne affiche une de ses informations (ID, nom, prénom, etc.)."""

def load_users(self):
        """Charge les utilisateurs depuis la base de données et les affiche dans le tableau"""
        
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, surname, birthdate, status, age, gender, email, phone, role FROM users")
            rows = cursor.fetchall()

        self.users_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, item in enumerate(row):
                self.users_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
                
"""La méthode `update_user_info` permet à l'administrateur de modifier les informations
d'un utilisateur sélectionné dans le tableau. Elle affiche des boîtes de dialogue pour 
saisir les nouvelles valeurs, puis met à jour la base de données avec ces informations.
Enfin, le tableau des utilisateurs est rechargé pour refléter les modifications."""

def update_user_info(self):
        """Met à jour les informations d'un utilisateur sélectionné"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.critical(self, "Erreur", "Veuillez sélectionner un utilisateur à mettre à jour.")
            return

        user_id = self.users_table.item(selected_row, 0).text()
        name = self.users_table.item(selected_row, 1).text()
        surname = self.users_table.item(selected_row, 2).text()
        birthdate = self.users_table.item(selected_row, 3).text()
        status = self.users_table.item(selected_row, 4).text()
        age = int(self.users_table.item(selected_row, 5).text())  # Convertir en entier
        gender = self.users_table.item(selected_row, 6).text()
        email = self.users_table.item(selected_row, 7).text()
        phone = self.users_table.item(selected_row, 8).text()
        role = self.users_table.item(selected_row, 9).text()

        # Afficher une boîte de dialogue pour modifier les informations
        new_name, ok = QInputDialog.getText(self, "Modifier le nom", "Nouveau nom :", text=name)
        if not ok:
            return
        new_surname, ok = QInputDialog.getText(self, "Modifier le prénom", "Nouveau prénom :", text=surname)
        if not ok:
            return
        new_birthdate, ok = QInputDialog.getText(self, "Modifier la date de naissance", "Nouvelle date de naissance (YYYY-MM-DD) :", text=birthdate)
        if not ok:
            return
        new_status, ok = QInputDialog.getText(self, "Modifier le statut", "Nouveau statut :", text=status)
        if not ok:
            return
        new_age, ok = QInputDialog.getInt(self, "Modifier l'âge", "Nouvel âge :", value=age)
        if not ok:
            return
        new_gender, ok = QInputDialog.getText(self, "Modifier le sexe", "Nouveau sexe :", text=gender)
        if not ok:
            return
        new_email, ok = QInputDialog.getText(self, "Modifier l'email", "Nouvel email :", text=email)
        if not ok:
            return
        new_phone, ok = QInputDialog.getText(self, "Modifier le téléphone", "Nouveau téléphone :", text=phone)
        if not ok:
            return
        new_role, ok = QInputDialog.getText(self, "Modifier le rôle", "Nouveau rôle :", text=role)
        if not ok:
            return

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET name = ?, surname = ?, birthdate = ?, status = ?, age = ?, gender = ?, email = ?, phone = ?, role = ?
                WHERE id = ?
            ''', (new_name, new_surname, new_birthdate, new_status, new_age, new_gender, new_email, new_phone, new_role, user_id))
            conn.commit()

        QMessageBox.information(self, "Succès", "Informations utilisateur mises à jour avec succès.")
        self.load_users()  # Recharger les utilisateurs dans le tableau
        
"""PERMET DE SUPPRIMER UN UTILISATEUR A LA BASE DE DONNEES"""

def delete_user(self):
        """Supprime un utilisateur de la base de données"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.critical(self, "Erreur", "Veuillez sélectionner un utilisateur à supprimer.")
            return

        user_id = self.users_table.item(selected_row, 0).text()

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

        self.users_table.removeRow(selected_row)
        QMessageBox.information(self, "Succès", "Utilisateur supprimé avec succès.")
        
"""La méthode `send_message` permet à l'administrateur d'envoyer un message par email 
à un utilisateur sélectionné dans le tableau. Elle utilise les informations SMTP 
pour envoyer le message via Gmail. En cas d'erreur (ex : informations SMTP manquantes ou échec d'envoi),
un message d'erreur est affiché."""

def send_message(self):
        """Envoie un message à un utilisateur par email ou SMS"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.critical(self, "Erreur", "Veuillez sélectionner un utilisateur à qui envoyer un message.")
            return

        email = self.users_table.item(selected_row, 7).text()
        phone = self.users_table.item(selected_row, 8).text()
        message, ok = QInputDialog.getText(self, "Envoyer Message", "Entrez votre message:")

        if ok and message:
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')

            if not smtp_user or not smtp_password:
                QMessageBox.critical(self, "Erreur", "Les informations d'identification SMTP ne sont pas définies.")
                return

            try:
                server = SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, email, message)
                server.quit()
                QMessageBox.information(self, "Succès", "Message envoyé avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur d'envoi de message: {e}")
                
"""La méthode `search_user` recherche des utilisateurs dans la base de données en fonction
d'un terme de recherche (nom) et affiche les résultats correspondants dans un tableau.
Si aucun terme n'est saisi, un message d'erreur est affiché."""
def search_user(self):
        """Recherche un utilisateur par nom"""
        search_term = self.search_input.text().strip()
        if not search_term:
            QMessageBox.critical(self, "Erreur", "Veuillez entrer un nom pour la recherche.")
            return

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, surname, birthdate, status, age, gender, email, phone, role FROM users WHERE name LIKE ?", ('%' + search_term + '%',))
            rows = cursor.fetchall()

        self.users_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, item in enumerate(row):
                self.users_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
                
"""La méthode `upload_image` permet à l'utilisateur de sélectionner une image, 
détecte les visages dans celle-ci, et compare les encodages faciaux avec 
ceux enregistrés dans la base de données. Si une correspondance est trouvée,
le nom de l'utilisateur est affiché ; sinon, un message indique qu'aucune correspondance n'a été trouvée."""

def upload_image(self):
        """Télécharge une image et la compare avec les visages enregistrés"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_path:
            return

        # Charger l'image sélectionnée
        image = face_recognition.load_image_file(file_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        if len(face_encodings) == 0:
            QMessageBox.critical(self, "Erreur", "Aucun visage détecté dans l'image.")
            return

        # Comparer avec les encodages connus
        matches = face_recognition.compare_faces(list(self.known_encodings.values()), face_encodings[0], tolerance=0.5)
        name = "Inconnu"

        if True in matches:
            user_id = list(self.known_encodings.keys())[matches.index(True)]
            name = self.get_user_name(user_id)
            QMessageBox.information(self, "Résultat", f"Visage reconnu : {name}")
        else:
            QMessageBox.information(self, "Résultat", "Aucune correspondance trouvée.")
            
"""La méthode `show_messaging_window` crée et affiche une fenêtre dédiée à la messagerie, 
comprenant une zone d'affichage des messages, un champ de saisie pour écrire un message,
et un bouton pour envoyer. Les messages existants sont chargés et affichés dès l'ouverture de la fenêtre."""

def show_messaging_window(self):
        """Affiche la fenêtre de messagerie"""
        self.messaging_window = QWidget()
        self.messaging_window.setWindowTitle("Messagerie")
        self.messaging_window.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.message_display = QTextEdit(self.messaging_window)
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)

        self.message_input = QLineEdit(self.messaging_window)
        self.message_input.setPlaceholderText("Entrez votre message")
        layout.addWidget(self.message_input)

        self.send_button = QPushButton("Envoyer", self.messaging_window)
        self.send_button.clicked.connect(self.send_message_to_user)
        layout.addWidget(self.send_button)

        self.messaging_window.setLayout(layout)
        self.messaging_window.show()

        self.load_messages()
        
"""La méthode `load_messages` récupère les messages envoyés ou reçus par l'utilisateur actuel
depuis la base de données et les affiche dans l'interface. Chaque message est formaté avec le nom de l'expéditeur, 
l'horodatage et le contenu du message."""

def load_messages(self):
        """Charge les messages de l'utilisateur actuel"""
        if not self.current_user:
            return

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender_id, message, timestamp FROM messages
                WHERE receiver_id = ? OR sender_id = ?
                ORDER BY timestamp
            ''', (self.current_user, self.current_user))
            messages = cursor.fetchall()

        self.message_display.clear()
        for sender_id, message, timestamp in messages:
            sender_name = self.get_user_name(sender_id)
            self.message_display.append(f"{sender_name} ({timestamp}): {message}")
            
"""La méthode `send_message_to_user` permet à un utilisateur connecté 
d'envoyer un message à un autre utilisateur en spécifiant son ID.
Le message est enregistré dans la base de données avec un horodatage,
puis l'interface est actualisée pour afficher les nouveaux messages."""

def send_message_to_user(self):
        """Envoie un message à un autre utilisateur ou à l'administrateur"""
        if not self.current_user:
            QMessageBox.critical(self, "Erreur", "Vous devez être connecté pour envoyer un message.")
            return

        message = self.message_input.text().strip()
        if not message:
            QMessageBox.critical(self, "Erreur", "Veuillez entrer un message.")
            return

        receiver_id, ok = QInputDialog.getInt(self, "Envoyer un message", "Entrez l'ID du destinataire:")
        if not ok:
            return

        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, message, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (self.current_user, receiver_id, message, QDateTime.currentDateTime().toString()))
            conn.commit()

        self.message_input.clear()
        self.load_messages()
        
"""La méthode `get_user_name` récupère le nom d'un utilisateur
à partir de son ID dans la base de données, 
ou retourne "Inconnu" si l'utilisateur n'est pas trouvé."""

def get_user_name(self, user_id):
        """Récupère le nom d'un utilisateur à partir de son ID"""
        with sqlite3.connect(self.users_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else "Inconnu"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceAuthenticationApp()
    window.show()
    sys.exit(app.exec())