# Membres : Ousmane Cisse - Samba Coumba Ba - Aichatou Dia


Projet Computer Vision : Mise en place d’un système de pointage automatique par reconnaissance facial
############################################################################################################


Objectif du Projet
Le projet vise à concevoir, développer et mettre en œuvre un système de reconnaissance automatique basé sur la technologie de reconnaissance faciale. 
L'objectif principal est de créer un système capable d'identifier et de vérifier automatiquement l'identité d'une personne en analysant les caractéristiques
uniques de son visage. Cette solution a le potentiel d'être utilisée dans divers contextes tels que la sécurité, le contrôle d'accès, la gestion des effectifs, 
et d'autres applications nécessitant une authentification fiable et rapide.

Tâches à réaliser / Etapes / Livrables : Collecte de Données- Preprocessing - Entraînement et Validation - Déploiement.

#########################################################################################################################

1. Introduction
Le code fourni est une application Python qui implémente un système d'authentification sécurisé basé sur la reconnaissance faciale.
Il utilise plusieurs bibliothèques populaires telles que face_recognition pour la reconnaissance faciale, PyQt6 pour l'interface graphique,
 sqlite3 pour la gestion de la base de données, et smtplib pour l'envoi de notifications par email. L'application permet aux utilisateurs de
s'authentifier via leur visage et un code PIN, et offre des fonctionnalités supplémentaires comme l'inscription d'utilisateurs, la gestion des utilisateurs par un administrateur,
et une messagerie interne.

###################################################################################################################
2. Initialisation de l'Application
Base de données : Une base de données SQLite (users.db) est créée pour stocker les informations des utilisateurs, les logs d'accès, et les messages.

Interface Utilisateur : L'interface est composée de plusieurs éléments :

Une zone d'affichage de la caméra.
Des champs de saisie pour l'identifiant et le code PIN.
Des boutons pour démarrer/arrêter la caméra, se connecter, se déconnecter, s'inscrire, accéder au mode administrateur, et utiliser la messagerie.
Des labels pour afficher le statut de l'authentification

#############################################################################################################################

3. Fonctionnalités Principales

Reconnaissance Faciale :
La caméra capture des images en temps réel.
Les visages détectés sont comparés avec les encodages stockés dans la base de données.
Si un visage est reconnu, l'utilisateur est identifié et peut se connecter en entrant son code PIN.

Authentification :
L'authentification combine la reconnaissance faciale et la validation du code PIN (hashé avec SHA-256).
Les tentatives d'accès sont journalisées dans la base de données.

Inscription :
Les nouveaux utilisateurs peuvent s'inscrire en fournissant leurs informations personnelles et en capturant une image de leur visage.
Les encodages faciaux sont stockés dans la base de données.

Administration :
Un administrateur peut se connecter pour gérer les utilisateurs (ajouter, modifier, supprimer) et envoyer des messages.
Un tableau de bord permet de visualiser et de rechercher les utilisateurs.

Messagerie :
Les utilisateurs authentifiés peuvent envoyer et recevoir des messages via une interface dédiée.

Notifications : 
En cas de tentative d'accès non autorisée, une notification est envoyée par email.

###########################################################################################################################

4. Points Forts du Code
Modularité : Le code est bien structuré, avec des méthodes distinctes pour chaque fonctionnalité (ex : start_camera, validate_access, register_user, etc.).

Sécurité :

Les codes PIN sont hachés avant d'être stockés dans la base de données.

La reconnaissance faciale utilise un seuil de similarité pour éviter les faux positifs.

Interface Utilisateur : L'interface est intuitive et bien organisée, avec des boutons clairs et des messages d'erreur explicites.

Extensibilité : Le code est facilement extensible pour ajouter de nouvelles fonctionnalités (ex : intégration de SMS, gestion des rôles, etc.).

##################################################################################################################

5. Gestion des Utilisateurs

Chargement des Utilisateurs :

La méthode load_users récupère les informations des utilisateurs depuis la base de données et les affiche dans un tableau.
Les colonnes du tableau incluent l'ID, le nom, le prénom, la date de naissance, le statut, l'âge, le sexe, l'email, le téléphone, et le rôle de chaque utilisateur.

Mise à Jour des Informations :

La méthode update_user_info permet à l'administrateur de modifier les informations d'un utilisateur sélectionné.
Une boîte de dialogue est affichée pour chaque champ à modifier (nom, prénom, date de naissance, etc.).
Les modifications sont ensuite enregistrées dans la base de données.

Suppression d'Utilisateurs :

La méthode delete_user supprime un utilisateur sélectionné de la base de données.
Une confirmation visuelle est affichée dans l'interface utilisateur après la suppression

#############################################################################################################

6. Messagerie
   
Envoi de Messages :

La méthode send_message permet à l'administrateur d'envoyer un message à un utilisateur sélectionné.
Le message est envoyé par email à l'adresse de l'utilisateur.

Fenêtre de Messagerie :

La méthode show_messaging_window affiche une interface dédiée à la messagerie.
Les utilisateurs peuvent envoyer et recevoir des messages, qui sont stockés dans la base de données.
La méthode load_messages charge les messages de l'utilisateur actuel et les affiche dans un widget QTextEdit.
La méthode send_message_to_user permet à un utilisateur d'envoyer un message à un autre utilisateur ou à l'administrateur.

############################################################################################################

7. Recherche d'Utilisateurs

Recherche par Nom :

La méthode search_user permet de rechercher un utilisateur par son nom.
Les résultats de la recherche sont affichés dans le tableau des utilisateurs.
##########################################################################################################
8. Téléchargement d'Image

Comparaison d'Image :

La méthode upload_image permet à l'utilisateur de télécharger une image et de la comparer avec les visages enregistrés dans la base de données.
Si un visage est reconnu, le nom de l'utilisateur correspondant est affiché

9. Deploiement
    Nous avons un dossier de video contenant 3 videos qui illustrent le deploiement.
    
10. Conclusion 
Le code fourni est une application fonctionnelle et bien structurée qui combine reconnaissance faciale et authentification par code PIN.
Il offre une base solide pour un système d'authentification sécurisé, avec des fonctionnalités supplémentaires comme la gestion des utilisateurs et la messagerie.
