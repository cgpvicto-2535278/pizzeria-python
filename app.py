from flask import Flask, render_template, request
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)

load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_name = os.getenv('DB_NAME')

try:
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        database=db_name
    )
except:
    db = 0
@app.route('/')
def index():
    if db == 0:
        return render_template('echecConnexion.html')
    else:
        return render_template('index.html')

@app.route('/commander')
def formulaire_commande():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM croutes;")
    croutes = cursor.fetchall()
    cursor.execute("SELECT * FROM sauces;")
    sauces = cursor.fetchall()
    cursor.execute("SELECT * FROM garnitures;")
    garnitures = cursor.fetchall()
    cursor.close()
    return render_template('form_commande.html', croutes=croutes, sauces=sauces, garnitures=garnitures)

@app.route('/placer-commande', methods=['POST'])
def ajouter_commande():

    # Vérification d'intégrité des données textuelles

    if 0 > len(request.form['nom']) > 255:
        return render_template('mauvaise_valeur.html' + ' nom')
    if 0 > len(request.form['adresse']) > 255:
        return render_template('mauvaise_valeur.html' + ' add')
    if 0 > len(request.form['num_tel']) > 20:
        return render_template('mauvaise_valeur.html' + ' tel')

    # Verification id croute

    cursor = db.cursor()
    requete = "SELECT * FROM croutes WHERE id = %(id_croute)s;"
    parametres = {
        'id_croute' : request.form['type_croute']
    }
    cursor.execute(requete, parametres)
    cursor.fetchall()
    if cursor.rowcount != 1:
        cursor.close()
        return render_template('mauvaise_valeur.html')

    # Verification id sauce

    requete = "SELECT * FROM sauces WHERE id = %(id_sauce)s;"
    parametres = {
        'id_sauce' : request.form['sauce']
    }
    cursor.execute(requete, parametres)
    cursor.fetchall()
    if cursor.rowcount != 1:
        cursor.close()
        return render_template('mauvaise_valeur.html')

    # Verification garnitures

    listeGarnitures = []
    for i in range(1, 5):
        if int(request.form['garniture_' + str(i)]) > 0:
            listeGarnitures.append(int(request.form['garniture_' + str(i)]))

    for garniture in listeGarnitures:
        requete = "SELECT * FROM garnitures WHERE id = %(id_garniture)s;"
        parametres = {
            'id_garniture' : garniture
        }
        cursor.execute(requete, parametres)
        cursor.fetchall()
        if cursor.rowcount != 1:
            cursor.close()
            return render_template('mauvaise_valeur.html')

    # Insertion de pizza

    try:
        requete = "INSERT INTO pizzas (sauce_id, croute_id) VALUES(%(id_sauce)s, %(id_croute)s);"
        parametres = {
            'id_sauce' : request.form['sauce'],
            'id_croute' : request.form['type_croute']
        }
        cursor.execute(requete, parametres)

        # Insertion de garnitures pour la pizza

        id_pizza = cursor.lastrowid

        for garniture in listeGarnitures:
            requete = "INSERT INTO pizzas_garnitures (pizza_id, garniture_id) VALUES(%(id_pizza)s, %(id_garniture)s)"
            parametres = {
                'id_pizza' : id_pizza,
                'id_garniture' : garniture
            }
            cursor.execute(requete, parametres)

        # Insertion de la commande

        maintenant = datetime.now();
        requete = "INSERT INTO commandes (temps_commande, nom_client, telephone_client, adresse, pizza_id) VALUES(%(temps_commande)s, %(nom_client)s, %(telephone_client)s, %(adresse)s, %(pizza_id)s);"
        parametres = {
            'temps_commande' : maintenant,
            'nom_client' : request.form['nom'],
            'telephone_client' : request.form['num_tel'],
            'adresse' : request.form['adresse'],
            'pizza_id' : id_pizza
        }

        cursor.execute(requete, parametres)

        db.commit()
    except mysql.connector.Error as erreur:
        cursor.close()
        return render_template("erreurDB.html")

    cursor.close()
    return render_template("commande_reussite.html")

@app.route('/liste-commande')
def listeCommandes():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT c.id id, nom_client, temps_commande, cr.nom croute, s.nom sauce FROM commandes_en_attente ca INNER JOIN commandes c ON ca.commande_id = c.id INNER JOIN pizzas p ON p.id = c.pizza_id INNER JOIN croutes cr ON cr.id = p.croute_id INNER JOIN sauces s ON s.id = p.sauce_id ORDER BY c.temps_commande;")
    commandes_att = cursor.fetchall()
    cursor.close()
    return render_template("liste_commandes.html", commandes=commandes_att)

@app.route('/commande/<int:id>')
def detailsCommande(id):

    cursor = db.cursor(dictionary=True)

    requete = "SELECT c.id id, nom_client, telephone_client, adresse, temps_commande, cr.nom croute, s.nom sauce FROM commandes c INNER JOIN pizzas p ON p.id = c.pizza_id INNER JOIN croutes cr ON cr.id = p.croute_id INNER JOIN sauces s ON s.id = p.sauce_id WHERE c.id = %(id)s;"
    parametres = {
        "id" : id
    }
    cursor.execute(requete, parametres)
    commande = cursor.fetchone()

    if cursor.rowcount <= 0:
        cursor.close()
        return render_template("echec_requete_commande.html")

    requete = "SELECT g.nom nom FROM commandes c INNER JOIN pizzas p ON p.id = c.pizza_id INNER JOIN pizzas_garnitures pg ON p.id = pg.pizza_id INNER JOIN garnitures g ON g.id = pg.garniture_id WHERE c.id = %(id)s;"
    parametres = {
        "id" : id
    }
    cursor.execute(requete, parametres)
    garnitures = cursor.fetchall()

    cursor.close()

    return render_template("commande.html", commande=commande, garnitures=garnitures)

@app.route('/terminer/<int:id>')
def terminerCommande(id):
    cursor = db.cursor(dictionary=True)

    requete = "DELETE FROM commandes_en_attente WHERE commande_id = %(id)s"
    parametres = {
        "id" : id
    }
    try:
        cursor.execute(requete, parametres)
        db.commit()
    except mysql.connector.Error as erreur:
        cursor.close()
        return render_template("erreurDB.html")

    cursor.close()
    return render_template("terminer_reussi.html")


if __name__ == '__main__':
    app.run(debug=True)
