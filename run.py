from flask import Flask
import os
from flask import render_template, request, redirect, url_for
import codecs
import json
import csv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import markdown
from random import *
import time


UPLOAD_FOLDER = "csv"
ALLOWED_EXTENSIONS = {'csv'}

def ouvrirQuestionnaire(user): #Ouvre le fichier {user}.json contenant le questionnaire d'un utilisateur & renvoie (dict) le questionnaire sous le format dict
    fichier=None
    nom_questionnaire = user + ".json"
    fichier = codecs.open(f'user/{nom_questionnaire}', "r", "utf8") #Cherche dans le dossier user
    questionnaire = json.load(fichier)
    if fichier:
        fichier.close()
    return questionnaire

def ecraserQuestionnaire(user, questionnaire): #Remplace l'ancien questionnaire par celui entrer en paramètre
    fichier=None
    nom_questionnaire = user + ".json"
    fichier = codecs.open(f'user/{nom_questionnaire}', "w", "utf8")
    json.dump(questionnaire, fichier)
    if fichier:
        fichier.close()

def tailleQuestionnaire(questionnaire): #Renvoie (int) la taille du dictionnaire
    return int(len(questionnaire))

def nomQuestion(numQuestion): #Renvoie (str) le nom d'une question en fonction d'un chiffre
    return str("Question " + str(numQuestion))

def numQuestion(nomQuestion): #Renvoie (int) le numero d'une question
    return int(nomQuestion[-1])

def supprimer(questionnaire, num_a_suppr, username): #Renvoie (dict) le questionnaire sans la question dont le numéro est en paramètre
    questionnaire = ouvrirQuestionnaire(username)
    with open("questions.json", "r") as file:
            nom_question = json.load(file)

    if (num_a_suppr != "") : #vérifie que la question à supprimer n'est pas la question 0
        for i in range(len(questionnaire)):
            if (num_a_suppr == questionnaire[i]['id']): #vérifie que la question à supprimer est dans le dictionnaire
                del questionnaire[i]
                for j in range (len(nom_question)):
                    if (num_a_suppr == nom_question[j]):
                        del nom_question[j]
                        break
                with open("questions.json", "w") as file:
                    json.dump(nom_question, file)
                break
    return questionnaire

def verifQuestion(questionnaire, nom_question_a_cree): #Renvoie (dict) la nouvelle question sans '' et sans None // vérifier que la question n'est pas corrompu et la corriger si jamais
    while "" in questionnaire[nom_question_a_cree][1]:
        questionnaire[nom_question_a_cree][1].remove("")
    while None in questionnaire[nom_question_a_cree][1]:
        questionnaire[nom_question_a_cree][1].remove(None)
    return questionnaire[nom_question_a_cree]

def listeEtiquette (questionnaire):
    liste_etiquette = []
    for i in range(len(questionnaire)):
            for j in range(len(questionnaire[i]["etiquette"])) :
                if (questionnaire[i]["etiquette"][j] not in liste_etiquette) :
                    liste_etiquette.append(questionnaire[i]["etiquette"][j])
    return liste_etiquette

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def listID(liste_eleve ):
  li = []
  for eleve in liste_eleve:
    li.append(eleve[0])
  return li

def verifListeNewEleve(liste_eleve):
    list_id = listID(liste_eleve)
    liste_a_suppr = []
    for i in range(len(list_id)):
        if list_id[i] in list_id[int(i+1):]:
            liste_a_suppr.append(i)
    liste_a_suppr.reverse()
    for i in liste_a_suppr:
        del liste_eleve[i]
    liste_a_suppr = []
    list_id = listID(liste_eleve)
    with open("users.json", "r") as file:
        users = json.load(file)

        for user in users :
            for i in range(len(list_id)) :
                if list_id[i] == user["username"]:
                    liste_a_suppr.append(i)
    liste_a_suppr.reverse()
    for i in liste_a_suppr:
        del liste_eleve[i]

    return liste_eleve

def marquListeDoublons(liste_eleve):
    list_id = listID(liste_eleve)
    liste_a_marque=[]
    for i in range(len(list_id)):
        if list_id[i] in list_id[int(i+1):]:
            liste_a_marque.append(list_id[i])
    return liste_a_marque

def marquListeDejaExistant(liste_eleve):
    liste_a_marque = []

    list_id = listID(liste_eleve)

    with open("users.json", "r") as file:
        users = json.load(file)

    for user in users :
        for i in range(len(list_id)) :
            if list_id[i] == user["username"]:
                liste_a_marque.append(list_id[i])
    return liste_a_marque


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')

def home(): #Page d'entrée dans l'app // Purement décoratif
    return render_template('home.html')

@app.route('/login') 
def login(): #Fixe la page login.html
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_log(): #Permet de saisir son id et son mdp et de se connecter
    username = request.form.get('username') #Récupère l'id
    password = request.form.get('password')
    with open("users.json", "r") as file:
        users = json.load(file)
    for user in users: #vérifie que le le mdp correspond à l'id
        if user["username"] == username and check_password_hash(user["password"], password):
            if user["role"] == "Professeur":
                return redirect(url_for('menu', username=username)) #Renvoie vers l'index
            else :
                return redirect(url_for('menuEleve', username=username)) #Renvoie vers l'index
    return redirect(url_for('login')) #Si mdp et id ne correspondent pas, renvoie vers login.html


@app.route('/logout') #Non utilisé
def logout():
    return redirect(url_for('home'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_reg(): #Créer un compte utilisateur en saisissant un username et un mdp
    username = request.form.get('username') #Récupère le username et password
    password = request.form.get('password')
    role = request.form.get('role')

    with open("users.json", "r") as file: #Récupère le user.json en r
        users = json.load(file)
    for user in users:
        if user["username"] == username: #Vérifie que qu'il n'y ai pas un compte avec le m username
            return redirect(url_for('register'))

    if role == "Professeur":
        classe = []
        new_user = {
        "id": len(users) + 1,
        "username": username,
        "password": generate_password_hash(password, method='sha256'),
        "role": role,
        "classe" : classe
        }
    else :
        classe=""
        professeur = []
        new_user = {
        "id": len(users) + 1,
        "username": username,
        "password": generate_password_hash(password, method='sha256'),
        "role": role,
        "classe" : classe,
        "professeur" : professeur
        }

    

    users.append(new_user) #Rajoute cette table dans notre nouvelle variable users

    with open("users.json", "w") as file: #Rajoute users dans users.json
        json.dump(users, file)

    with open(f"user/{username}.json", "w") as user_file: #Creation du fichier personnel json
        questionnaire = []
        json.dump(questionnaire, user_file)

    return redirect(url_for('login'))

@app.route('/menu/<username>') #Non utilisé
def menu(username):
    return render_template('menu.html', username = username)

@app.route('/index/<username>', methods = ['POST', 'GET']) #page principale
def index(username): 
    
    questionnaire = ouvrirQuestionnaire(username)
    liste_etiquette = listeEtiquette(questionnaire)
        
    actionSUP = request.args.get('doSUPP') #Récupère la valeur 2 si un boutton est supprier est pressé

    if actionSUP == "2" : #Permet de savoir si le boutton a été pressé sans utilisation JavaScript ou redirection vers une autre page
            num_a_suppr = request.args.get('numSUPP') #Récupère le numéro de la question a supprimé
            questionnaire=supprimer(questionnaire, num_a_suppr, username) #Supprime la question
            ecraserQuestionnaire(username, questionnaire)  
            return redirect(url_for('index', username = username))

    ecraserQuestionnaire(username, questionnaire)  

    return render_template('index.html', username = username, questionnaire = questionnaire, liste_etiquette = liste_etiquette)


@app.route('/ajouter/<username>',methods = ['POST', 'GET']) #page ajouter une question
def ajouter(username):
    
    

    questionnaire = ouvrirQuestionnaire(username)
    
    
    liste_etiquette = listeEtiquette(questionnaire)
    val_rep = []


    if request.method == 'POST':
        etiquette = request.form.getlist('etiquette')

        with open("questions.json", "r") as file:
            liste_ID = json.load(file)
            
        while True :
            ID_question_a_cree =""
            for i in range(8):
                val = 91
                while val in [58,59,60,61,62,63, 91,92,93,94,95,96]:
                    val = randint(48,122)
                ID_question_a_cree = ID_question_a_cree + chr(val)
            if ID_question_a_cree not in liste_ID : break
        
        liste_ID.append(ID_question_a_cree)
        with open("questions.json", "w") as file:
            json.dump(liste_ID, file)

        if (etiquette != None):
            etiquettes = etiquette
        


    


        enonce = request.form['enon']
        val_enonce = enonce
        if ('~~~mermaid' in enonce) or ('```mermaid' in enonce) : #Permet de séparer un enoncé écrit en mermaid d'un enoncé écrit en pyhton par exemple
            val_enonce = markdown.markdown(enonce, extensions=['fenced_code', 'md_mermaid'], output_format="html4")
        else:
            val_enonce = markdown.markdown(enonce, extensions=['fenced_code', 'codehilite'], output_format="html4")



        nb_quest = int(request.form['nb_quest'])

        rep_n = request.form['rep_n']
        if rep_n != "":
                val_rep.append([rep_n,True])
                type = "numerique"
        else :
            for i in range(nb_quest) : #Limite à l'insertion de 100 réponses
                
                
                nom_rep = "rep" + str(i+1)
                nom_rep = request.form[nom_rep]
                val_check =""
                MDContent = nom_rep
                nom_check = "checkbox" + str(i+1)
                type = "choixMultiple"
                try:
                    nom_check = request.form[nom_check]
                    val_check = True
                except:
                    val_check = False

                if ('~~~mermaid' in enonce) or ('```mermaid' in enonce):
                    MDContent = markdown.markdown(nom_rep, extensions=['fenced_code', 'md_mermaid'], output_format="html4")
                    val_rep.append([MDContent, val_check])

                else:
                    MDContent = markdown.markdown(nom_rep, extensions=['fenced_code', 'codehilite'], output_format="html4")
                    val_rep.append([MDContent, val_check])
                




    
    
        if (val_enonce != None) and (val_enonce != "") and (val_rep[0] != "") : #succession de if permettent de vérifier que la question n'est pas vide
            new_question = {
                "id" : ID_question_a_cree,
                "etiquette" : etiquettes,
                "type" : type,
                "enonce" : val_enonce,
                "reponse" : val_rep,
                "repEleve" : {}
            }
            questionnaire.append(new_question)



        
        ecraserQuestionnaire(username, questionnaire)

        return redirect(url_for('index', username = username))


    return render_template('ajouter.html', username = username, questionnaire = questionnaire, liste_etiquette = liste_etiquette) #permet d'afficher la variable du nom de la question de la variable dans l'html

         


@app.route('/modifier/<username>/<nom_question_a_modifier>',methods = ['POST', 'GET']) #page modifier une question
def modifier(username, nom_question_a_modifier):
    
    questionnaire = ouvrirQuestionnaire(username)
    for i in range(len(questionnaire)):
        if questionnaire[i]['id'] == nom_question_a_modifier :
            enonce_base = questionnaire[i]["enonce"]
            type_base = questionnaire[i]["type"]
            reponse_base = questionnaire[i]["reponse"]
            nb_reponse = len(questionnaire[i]["reponse"])
            repEleve_base = questionnaire[i]["repEleve"]

            etiquettes = questionnaire[i]["etiquette"]
    liste_etiquette = listeEtiquette(questionnaire)
    val_rep =[]


    if request.method == 'POST':
            etiquette = request.form.getlist('etiquette')

            if (etiquette != None):
                etiquettes = etiquette

            enonce = request.form['enon']
            val_enonce = enonce
            if ('~~~mermaid' in enonce) or ('```mermaid' in enonce) : #Permet de séparer un enoncé écrit en mermaid d'un enoncé écrit en pyhton par exemple
                val_enonce = markdown.markdown(enonce, extensions=['fenced_code', 'md_mermaid'], output_format="html4")
            else:
                val_enonce = markdown.markdown(enonce, extensions=['fenced_code', 'codehilite'], output_format="html4")



            nb_quest = int(request.form['nb_quest'])

            rep_n = request.form['rep_n']
            nom_rep = request.form['rep1']


            if (type_base == "numerique" and nom_rep =="") or (type_base == "choixMultiple" and rep_n !=""):
                val_rep.append([rep_n,True])
                type = "numerique"
            elif (type_base == "numerique" and nom_rep !="") or (type_base == "choixMultiple" and rep_n ==""):
                for i in range(nb_quest) : #Limite à l'insertion de 100 réponses
                    
                    
                    nom_rep = "rep" + str(i+1)
                    nom_rep = request.form[nom_rep]
                    val_check =""
                    MDContent = nom_rep
                    nom_check = "checkbox" + str(i+1)
                    type = "choixMultiple"
                    try:
                        nom_check = request.form[nom_check]
                        val_check = True
                    except:
                        val_check = False

                    if ('~~~mermaid' in enonce) or ('```mermaid' in enonce):
                        MDContent = markdown.markdown(nom_rep, extensions=['fenced_code', 'md_mermaid'], output_format="html4")
                        val_rep.append([MDContent, val_check])

                    else:
                        MDContent = markdown.markdown(nom_rep, extensions=['fenced_code', 'codehilite'], output_format="html4")
                        val_rep.append([MDContent, val_check])
                    




        
        
            if (val_enonce != None) and (val_enonce != "") and (val_rep[0] != "") : #succession de if permettent de vérifier que la question n'est pas vide
                for i in range (len(questionnaire)):
                    if questionnaire[i]["id"] == nom_question_a_modifier :
                        questionnaire[i]['etiquette']= etiquettes
                        questionnaire[i]['enonce']= val_enonce
                        questionnaire[i]['reponse']= val_rep
                        questionnaire[i]['type']= type
                        questionnaire[i]['repEleve'] = {}





            
            ecraserQuestionnaire(username, questionnaire)

            return redirect(url_for('index', username = username))


    return render_template('modifier.html', username = username, questionnaire = questionnaire, nom_question_a_modifier = nom_question_a_modifier, nb_reponse = nb_reponse, liste_etiquette = liste_etiquette, enonce_base = enonce_base, type_base = type_base, reponse_base =reponse_base, etiquettes = etiquettes) #permet d'afficher la variable du nom de la question de la variable dans l'html


@app.route('/sequence/<username>', methods = ['POST', 'GET']) #Non utilisé
def sequence(username):
    questionnaire = ouvrirQuestionnaire(username)
    liste_etiquette = listeEtiquette(questionnaire)
        
    if request.method == 'POST' :

        actionSUP = request.form['doSUPP'] #Récupère la valeur 2 si un boutton est supprier est pressé

        if actionSUP == "2" : #Permet de savoir si le boutton a été pressé sans utilisation JavaScript ou redirection vers une autre page
                num_a_suppr = request.form['numSUPP'] #Récupère le numéro de la question a supprimé
                print(num_a_suppr)
                questionnaire=supprimer(questionnaire, num_a_suppr, username) #Supprime la question
                ecraserQuestionnaire(username, questionnaire)  
                return redirect(url_for('sequence', username = username))

        ecraserQuestionnaire(username, questionnaire)  

    return render_template('sequence.html', username = username, questionnaire = questionnaire, liste_etiquette = liste_etiquette)

@app.route('/ajoutSequence/<username>', methods = ['POST', 'GET'])
def ajoutSequence(username):
    questionnaire = ouvrirQuestionnaire(username)
    liste_question = []
    for i in range(len(questionnaire)):
        if questionnaire[i]["type"] == "choixMultiple" or questionnaire[i]["type"] == "numerique" :
            liste_question.append(questionnaire[i]["id"])
    print(liste_question)
    if request.method == 'POST' :
        if request.form['sequence1'] != "":
            etiquette = request.form.getlist('etiquette')

            with open("questions.json", "r") as file:
                liste_ID = json.load(file)
            while True :
                ID_sequence_a_cree =""
                for i in range(8):
                    val = 91
                    while val in [58,59,60,61,62,63, 91,92,93,94,95,96]:
                        val = randint(48,122)
                    ID_sequence_a_cree = ID_sequence_a_cree + chr(val)
                if ID_sequence_a_cree not in liste_ID : break
        
            liste_ID.append(ID_sequence_a_cree)
            with open("questions.json", "w") as file:
                json.dump(liste_ID, file)


        nb_question_a_inserer = request.form['nb_quest_sequence']
        nom= request.form['nom']
        commentaire = request.form['com']
        liste_ID_quest =[]
        for i in range(int(nb_question_a_inserer)-1):
            ID_question = request.form['sequence'+str(i+1)]
            print(ID_question)
            if ID_question != "":
                liste_ID_quest.append(ID_question)
        new_sequence = {
            "id" :  ID_sequence_a_cree,
            "type" : "sequence",
            "nom" : nom,
            "commentaire" : commentaire,
            "etiquette" : etiquette,
            "question" : liste_ID_quest,
        }
        questionnaire.append(new_sequence)



        
        ecraserQuestionnaire(username, questionnaire)
        return redirect(url_for('sequence', username = username))
    return render_template('ajoutSequence.html', username = username, questionnaire = questionnaire, liste_question = liste_question, liste_etiquette = listeEtiquette(questionnaire))
 

@app.route('/modifierSequence/<username>/<nom_question_a_modifier>', methods = ['POST', 'GET'])
def modifierSequence(username, nom_question_a_modifier):
    questionnaire = ouvrirQuestionnaire(username)
    liste_question = []
    for i in range(len(questionnaire)):
        if questionnaire[i]["type"] == "choixMultiple" or questionnaire[i]["type"] == "numerique" :
            liste_question.append(questionnaire[i]["id"])
        if questionnaire[i]["id"] == nom_question_a_modifier :
            id_sequence  = questionnaire[i]["id"]
            etiquettes = questionnaire[i]["etiquette"]
            nb_question = len(questionnaire[i]["question"])
            val_question = questionnaire[i]["question"]
            val_nom = questionnaire[i]["nom"]
            val_com = questionnaire[i]["commentaire"]

    if request.method == 'POST' :
        if request.form['sequence1'] != "":
            etiquette = request.form.getlist('etiquette')



        nb_question_a_inserer = request.form['nb_quest_sequence']
        nom= request.form['nom']
        commentaire = request.form['com']
        liste_ID_quest =[]
        for i in range(int(nb_question_a_inserer)-1):
            ID_question = request.form['sequence'+str(i+1)]
            print(ID_question)
            if ID_question != "":
                liste_ID_quest.append(ID_question)
        
         
        for i in range(len(questionnaire)):
        
            if questionnaire[i]["id"] == nom_question_a_modifier :
                questionnaire[i]["nom"] = nom
                questionnaire[i]["commentaire"] = commentaire
                questionnaire[i]["etiquette"] = etiquette
                questionnaire[i]["question"] = liste_ID_quest


        
        ecraserQuestionnaire(username, questionnaire)
        return redirect(url_for('sequence', username = username))
    return render_template('modifierSequence.html', username = username, questionnaire = questionnaire, liste_question = liste_question, liste_etiquette = listeEtiquette(questionnaire), val_nom = val_nom, id_sequence  = id_sequence, etiquettes = etiquettes, nb_question = nb_question, val_question = val_question, val_com = val_com)
 

@app.route('/exporter/<username>',methods = ['POST', 'GET']) #page exporter une question
def exporter(username):

    questionnaire = ouvrirQuestionnaire(username)
    liste_etiquette = listeEtiquette(questionnaire)
    ecraserQuestionnaire(username,questionnaire)
    num = tailleQuestionnaire(questionnaire)
    liste_question_a_export=[]
    for i in range(num+1): #Explore toutes les questions saisies
        try:
            question_a_export = request.args.get(questionnaire[i]['id'], type=bool)#Permet de savoir si une question a été seléctionnée
            question_a_export = not(not(question_a_export))
        except:
            question_a_export = False

        if question_a_export : #Si la case a été coché, ajoute le nom de la question a une liste
            liste_question_a_export.append(questionnaire[i]['id'])
    
    print(liste_question_a_export)
    if liste_question_a_export == []:
        return render_template('exporter.html', username = username, questionnaire = questionnaire, liste_etiquette = liste_etiquette)
    else :
        return redirect(url_for('questionnaire', username = username, liste_question_a_export = liste_question_a_export))


@app.route('/questionnaire/<username>/<liste_question_a_export>')
def questionnaire(username, liste_question_a_export):
    #La page récupère en paramètre un str "['Question 1', 'Question 2',...]"" au lieu d'une liste list ['Question 1', 'Question 2'...]
    #Transforme ce str en cette list
    liste_question_a_export = list(liste_question_a_export.split("["))[1]
    liste_question_a_export = list(liste_question_a_export.split("]"))[0]
    liste_question_a_export = liste_question_a_export.replace("'","")
    liste_question_a_export = list(liste_question_a_export.split(", "))
    questionnaire = ouvrirQuestionnaire(username)
    ecraserQuestionnaire(username,questionnaire)


    #for i in range(len(liste_question_a_export)): #Créer un nouveau questionnaire avec les question séléctionnée avec la bonne numérotation
        #questionnaire["Question " + str(i+1)]=questionnaireOrigine[liste_question_a_export[i]]
    
    return render_template('questionnaire.html', username = username, questionnaire = questionnaire, liste_question_a_export = liste_question_a_export)


@app.route('/diffuser/<username>', methods=['GET', 'POST'])
def diffuser(username):
    questionnaire= ouvrirQuestionnaire(username)
    sequences = [seq for seq in questionnaire if seq['type'] == 'sequence']
    questions = [q for q in questionnaire if q['type'] == 'choixMultiple' or q['type'] == 'numérique']
    if request.method == 'POST':
        num_a_diff = request.form['num_a_diffuser']
        with open("questions.json", "r") as file:
            liste_ID = json.load(file)
        if num_a_diff in liste_ID :
            with open("open.json", "r") as file:
                liste_diffuse = json.load(file)
            for i in range(len(questionnaire)):
                if num_a_diff == questionnaire[i]['id']:
                    if questionnaire[i]['type'] != 'sequence' :
                        questionnaire[i]['etat'] = 'attente'
                        questionnaire[i]['repEleve'] = {}
                        questionnaire[i]['last'] = True
                        liste_diffuse.append(questionnaire[i])
                    else :
                        new_sequence = {
                            'id' : questionnaire[i]['id'],
                            'type' : 'sequence',
                            'commentaire' : questionnaire[i]['commentaire'],
                            'taille' : len(questionnaire[i]['question']),
                            'etat' : 'attente',
                            'enCours' : 0
                        }
                        cpt = 0
                        for j in range(len(questionnaire[i]['question'])):
                            nom = questionnaire[i]['question'][j]
                            for h in range(len(questionnaire)) :
                                if questionnaire[h]['id'] == nom :
                                    questionnaire[h]['repEleve'] = {}
                                    if cpt == len(questionnaire[i]['question']) - 1 :
                                        questionnaire[h]['last'] = True
                                    else :
                                        questionnaire[h]['last'] = False
                                    new_sequence[cpt] = questionnaire [h]
                                    cpt += 1
                        liste_diffuse.append(new_sequence)

            with open("open.json", "w") as file:
                json.dump(liste_diffuse, file)
            return redirect(url_for('diffuserAttente', username = username, num_a_diff = num_a_diff))
        else :
            render_template('diffuser.html', username = username)
        
    return render_template('diffuser.html', username = username, sequences = sequences, questions = questions, questionnaire = questionnaire)

@app.route('/diffuserAttente.html/<username>/<num_a_diff>', methods=['GET', 'POST'])
def diffuserAttente (username, num_a_diff) :
    if request.method == 'POST' :
        with open("open.json", "r") as file:
            liste_diffuse = json.load(file)
        for i in range(len(liste_diffuse)):
            if num_a_diff == liste_diffuse[i]['id']:
                liste_diffuse[i]['etat'] = 'enCours'
        with open("open.json", "w") as file:
                json.dump(liste_diffuse, file)
                
        return redirect(url_for('diffusionQuestion', username = username, num_a_diff = num_a_diff))
    return render_template('diffuserAttente.html', username = username, num_a_diff = num_a_diff)

@app.route('/diffusionQuestion/<username>/<num_a_diff>', methods=['GET', 'POST'])
def diffusionQuestion(username, num_a_diff):
    with open("open.json", "r") as file:
                liste_diffuse = json.load(file)
    for i in range(len(liste_diffuse)):
        if num_a_diff == liste_diffuse[i]['id']:
            liste_diffuse[i]['etat'] = 'enCours'
            if liste_diffuse[i]['type'] != 'sequence' : 
                questionnaire = liste_diffuse[i]
            else :
                enCours = str(liste_diffuse[i]['enCours'])
                questionnaire = liste_diffuse[i][enCours]
            with open("open.json", "w") as file:
                json.dump(liste_diffuse, file)

    return render_template('diffusionQuestion.html', username = username, questionnaire = questionnaire, num_a_diff =  num_a_diff)

@app.route("/resultatQuestion/<username>/<num_a_diff>")
def resultatQuestion(username, num_a_diff):
    
    
    with open("open.json", "r") as file:
        liste_diffuse = json.load(file)
    for i in range(len(liste_diffuse)):
        if num_a_diff == liste_diffuse[i]['id']:
            liste_diffuse[i]['etat'] = 'correction'
            if liste_diffuse[i]['type'] != 'sequence':
                questionnaire = liste_diffuse[i]

            else :

                enCours = str(liste_diffuse[i]['enCours'])
                questionnaire = liste_diffuse[i][enCours]
                liste_diffuse[i]['enCours'] +=1
    with open("open.json", "w") as file:
        json.dump(liste_diffuse, file)
    return render_template('resultatQuestion.html', username = username, num_a_diff = num_a_diff, questionnaire = questionnaire)

@app.route("/annulDiff/<username>/<num_a_diff>", methods = ['GET', 'POST'])
def annulDiff(username, num_a_diff) :
    with open("open.json", "r") as file:
        liste_diffuse = json.load(file)
    for i in range(len(liste_diffuse)):
        if num_a_diff == liste_diffuse[i]['id']:
            index = liste_diffuse.index(liste_diffuse[i])

    del liste_diffuse[index]
    with open("open.json", "w") as file:
        json.dump(liste_diffuse, file)
    return redirect(url_for('diffuser', username = username))



@app.route("/menuEleve/<username>", methods = ['GET', 'POST'])
def menuEleve(username):
    if request.method == 'POST' :
        num_a_rep = request.form['num_a_rep']
        with open("questions.json", "r") as file:
            liste_ID = json.load(file)
        if num_a_rep in liste_ID :
            with open("open.json", "r") as file:
                liste_diffuse = json.load(file)
            for i in range(len(liste_diffuse)):
                if liste_diffuse[i]['id'] == num_a_rep :
                    return redirect(url_for('repondre', username = username, num_a_rep = num_a_rep))
    return render_template ("menuEleve.html", username = username)


@app.route("/repondre/<username>/<num_a_rep>", methods = ['GET', 'POST'])
def repondre (username, num_a_rep):

    go = False
    cpt = 1
    while go == False :
        print(cpt)
        cpt +=1 
        with open("open.json", "r") as file:
            liste_diffuse = json.load(file)
        for i in range(len(liste_diffuse)):
            if liste_diffuse[i]['id'] == num_a_rep :
                if liste_diffuse[i]['etat'] == 'enCours' :
                    go = True
        time.sleep(0.5)

    with open("open.json", "r") as file:
        liste_diffuse = json.load(file)
    for i in range(len(liste_diffuse)):
        if liste_diffuse[i]['id'] == num_a_rep :
            if liste_diffuse[i]['type'] == 'sequence' :
                enCours = str(liste_diffuse[i]['enCours'])
                questionnaire = liste_diffuse[i][enCours] 
            else :
                questionnaire = liste_diffuse[i]
    if request.method == 'POST' :
        with open("open.json", "r") as file:
            liste_diffuse = json.load(file)
        for i in range(len(liste_diffuse)):
            if liste_diffuse[i]['id'] == num_a_rep :
                enCours = str(liste_diffuse[i]['enCours'])
                liste_repEleve = []
                if questionnaire['type'] == 'choixMultiple' :
                    for j in range(len(questionnaire['reponse'])):
                        try : 
                            val = request.form['check' + str(j)]
                            val = True
                        except :
                            val = False
                        new_rep = {'name' : questionnaire['reponse'][j][0], 'val' : liste_diffuse[i][enCours]['reponse'][j][1], 'rep' : val}
                        liste_repEleve.append(new_rep)
                    if liste_diffuse[i]['type'] == 'sequence':
                        liste_diffuse[i][enCours]['repEleve'][username] = liste_repEleve
                    else:
                        liste_diffuse[i]['repEleve'][username] = liste_repEleve
                else :
                    val = request.form['rep_num']
                    new_rep = {'val' : questionnaire['reponse'][0], 'rep' : val}
                    liste_repEleve.append(new_rep)
                    if liste_diffuse[i]['type'] == 'sequence':
                        liste_diffuse[i][enCours]['repEleve'][username] = liste_repEleve
                    else:
                        liste_diffuse[i]['repEleve'][username] = liste_repEleve
        with open("open.json", "w") as file:
            json.dump(liste_diffuse, file)
        return redirect(url_for('reponse', username = username, num_a_rep = num_a_rep))

    return render_template("repondre.html", username = username, questionnaire = questionnaire)

@app.route('/reponse/<username>/<num_a_rep>')
def reponse (username, num_a_rep) :
    go = False
    cpt = 1
    while go == False :
        print(cpt)
        cpt +=1 
        with open("open.json", "r") as file:
            liste_diffuse = json.load(file)
        for i in range(len(liste_diffuse)):
            if liste_diffuse[i]['id'] == num_a_rep :
                if liste_diffuse[i]['etat'] == 'correction' :
                    go = True
    time.sleep(0.5)

    
    with open("open.json", "r") as file:
        liste_diffuse = json.load(file)
    for i in range(len(liste_diffuse)):
        if liste_diffuse[i]['id'] == num_a_rep :
            if liste_diffuse[i]['type'] == 'sequence' :
                enCours = str(liste_diffuse[i]['enCours'] -1 )
                questionnaire = liste_diffuse[i][enCours]['repEleve'][username]
                _type=liste_diffuse[i][enCours]['type']
            else :
                questionnaire = liste_diffuse[i]
                _type=liste_diffuse[i]['type']
            if liste_diffuse[i][enCours]["last"] == True :
                last = True
    print(questionnaire)

    return render_template("reponse.html", username = username, num_a_rep = num_a_rep, questionnaire = questionnaire, _type = _type, last = last)
    

@app.route('/gestion/<username>', methods=['GET','POST']) #Non utilisé
def gestion(username):

    liste_classe = []
    liste_effectif = {}
    with open("users.json", "r") as file:
        users = json.load(file)
        for user in users :
            if user["username"] == username:
                liste_classe = user["classe"]
        for nom_classe in liste_classe:
            liste_eleve = []
            for user in users :
                if user["role"] == "Eleve" :
                    for classe in user["cours"]:
                        if nom_classe == classe[1] and username == classe[0] :
                            if user["nom"]!= "" or user["prenom"]!= "" :
                                liste_eleve.append([user["nom"], user["prenom"]])
                            else :
                                liste_eleve.append([user["username"]])


            liste_effectif[nom_classe] = liste_eleve
                            
        print(liste_effectif)


    

    if os.path.exists(f'csv/listeEleve_{username}.csv'):
        os.remove(f'csv/listeEleve_{username}.csv')

    if request.method=='POST':
        
        if 'file' not in request.files:
            return render_template('gestion.html', username = username, liste_effectif = liste_effectif)
        file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
        if file.filename == '':
            return render_template('gestion.html', username = username, liste_effectif = liste_effectif)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.rename(f'csv/{filename}', f'csv/listeEleve_{username}.csv')
            
            return redirect(url_for('creation', username = username))

    return render_template('gestion.html', username = username, liste_effectif = liste_effectif)


@app.route('/creation/<username>', methods=['GET','POST'])
def creation(username):
    liste_eleve = []
    professeur = username
    with open(f'csv/listeEleve_{username}.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

        for row in reader:
            eleve = (', '.join(row))
            li_eleve = eleve.split(';')
            liste_eleve.append(li_eleve)
    
    liste_doublon = marquListeDoublons(liste_eleve)
    liste_ID_deja_existant = marquListeDejaExistant(liste_eleve)

    
    if request.method=='POST' :
        classe = request.form['nom_classe']
        liste_eleve= verifListeNewEleve(liste_eleve)

        with open("users.json", "r") as file:
            users = json.load(file)
            for utilisateur in users:
                if utilisateur["username"]==username:
                    print(classe)
                    (utilisateur["classe"]).append(classe)
            
            for i in range(len(liste_eleve)):
                user = liste_eleve[i][0]
                password = liste_eleve[i][0]
                role = "Eleve"
                nom = liste_eleve[i][1]
                prenom = liste_eleve[i][2]
                
                
                new_user = {
                "id": len(users) + 1,
                "username": user,
                "password": generate_password_hash(password, method='sha256'),
                "role": role,
                "nom" : nom,
                "prenom" : prenom,
                "classe": classe,
                "cours":[(professeur,classe)]
                }
                
                users.append(new_user)

            if liste_ID_deja_existant != []:
                for idDejaExitant in liste_ID_deja_existant :
                    for util in users:
                        if (idDejaExitant == util["username"]) and ([professeur, classe] not in util["cours"]):
                            (util["cours"]).append((professeur,classe))
                    
            with open("users.json", "w") as file:
                json.dump(users, file)


        os.remove(f'csv/listeEleve_{username}.csv')
        return redirect(url_for('gestion', username = username))
    return render_template('creation.html', username = username, liste_eleve = liste_eleve, liste_doublon = liste_doublon, liste_ID_deja_existant = liste_ID_deja_existant)

@app.route('/compte/<username>') #Non utilisé
def compte(username):
    return render_template('compte.html', username = username)



if __name__ == '__main__':
   app.run(debug = True)