import json

# 1. Lire le fichier JSON
with open("open.json", "r") as fichier:
    donnees = json.load(fichier)

# 2. Récupérer les informations requises
reponses_correctes = donnees[0]['reponse']
reponses_eleves = donnees[0]['repEleve']

# 3. Comptez le nombre de repEleve et les initialiser le nombre de réponses correctes
nombre_repEleve = len(reponses_eleves)
nombre_reponses_correctes = 0

compteur_reponses = {}

for eleve, reponses in reponses_eleves.items():
    reponses_correctes_eleve = 0
    for reponse in reponses:
        intitule = reponse["name"]
        valeur = reponse["val"]
        choix_eleve = reponse["rep"]

        # Initialiser le compteur pour chaque réponse
        if intitule not in compteur_reponses:
            compteur_reponses[intitule] = 0

        # Compter les réponses des élèves où leur choix est 'true'
        if valeur:
            compteur_reponses[intitule] += 1

        # Vérifier si la réponse de l'élève est correcte (valeur == choix_eleve)
        if valeur == choix_eleve:
            reponses_correctes_eleve += 1

    # Si toutes les réponses de l'élève sont correctes, incrémenter le compteur
    if reponses_correctes_eleve == len(reponses):
        nombre_reponses_correctes += 1

# 4. Afficher les résultats
print(f"Nombre de repEleve: {nombre_repEleve}")
print(f"Nombre de réponses correctes: {nombre_reponses_correctes}")
for intitule, count in compteur_reponses.items():
    print(f"{intitule} : {count}")
print(compteur_reponses)
