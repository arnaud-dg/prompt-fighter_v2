"""Contenus centralisés (énoncés + conseils) pour l'application PromptFight.

Objectif:
- éviter de dupliquer les textes dans chaque page Streamlit
- faciliter la maintenance / l'évolution des exercices

Structure:
PROMPTFIGHT_CONTENT[page_key]["enonce"|"conseils"]
"""

from __future__ import annotations

PROMPTFIGHT_CONTENT = {
    "ex1": {
        "enonce": """
🎯 **Tâche :**  
Vous devez expliquer la notion de **Data Integrity** (intégrité des données) à des **nouveaux opérateurs** n'ayant
jamais entendu parler de ce sujet.
Formulez un **prompt** permettant de produire une note d'explication concrète et adaptée à des opérateurs de terrain.
""",
        "conseils": """
#### 1. Concepts clés

##### ✅ Qu'est-ce qu'un bon prompt ?  
Un bon prompt est :
- **Clair** : sans ambiguïté
- **Contextualisé** : il donne un cadre et une situation  
- **Spécifique** : il précise ce qu'on attend (forme, ton, longueur)

##### Prompt vague vs Prompt clair  

| Type | Exemple de prompt | Pourquoi ? |
|------|-------------------|------------|
| ❌ Vague | *Créé moi une courte note sur la data integrity* | Trop large, pas de cible ni de contexte |
| ✅ Clair | *Tu es un pharmacien industriel, qui doit à travers une note synthétique de 800 mots maximum effectuer des rappels sur les concepts de data integrity à des opérateurs terrain. La note doit faire référence à la procédure interne jointe. Cette note doit être compréhensible par des personnes n'ayant pas de connaissance du vocabulaire métier.* | Ciblé, clair, orienté utilisateur |

---

#### 2. La méthode TCREI : *Tous Ces Robots Ecrivent Incroyablement*

La méthode **TCREI** est un acronyme qui vous guide pour structurer vos prompts de manière efficace :

##### 📋 **T - Tâche** 
Définissez ce dont vous avez besoin clairement. N'hésitez pas à être précis sur l'attendu, le ton, les contraintes, ...

##### 🎭 **C - Contexte**
Ajoutez des informations de fond pour de meilleurs résultats. Une très bonne technique est de décrire les "Persona" (= qui parle à qui ?) car c'est sur cette base que les LLM ont été entraînés.

##### 🎯 **R - Référence**
Partagez des exemples ou des documents de références (ce point n'est pas réellement applicable dans cet exercice).

##### 🔧 **E - Évaluation**
Développez les critères qui font que la sortie sera appropriée.

##### 🎨 **I - Itération**
Corrigez votre prompt en fonction du résultat de sortie.

---

##### 💡 **Exemple complet TCREI :**
- **Contexte :** Tu es un expert marketing engagé dans la promotion de notre nouveau produit SaaS de gestion de projet qui cible spécifiquement les startups.
- **Tâche :** Écris un post LinkedIn engageant permettant de mettre en avant la nouvelle fonctionnalité "Pomodoro"
- **Référence :** Inspire-toi du style des posts viraux suivants : ...
- **Évaluation :** Le post doit être informatif mais pas trop promotionnel
- **Itération :** Ajoute des emojis et une question pour engager l'audience
""",
    },
    "ex2": {
        "enonce": """
🎯 **Tâche :**  
Votre département **Ressources Humaines** vous sollicite afin de construire un plan de développement lié à la **validation de nettoyage**. 
L'idée est leur fournir un support de départ avec différentes propositions de formation, permettant d'adresser des besoins plus ou moins poussés.
Rédigez un **prompt** afin de produire un **plan de formation structuré** sur les validations de nettoyage,
adapté à un public RH non spécialiste technique.
""",
        "conseils": """
Le format attendu influence beaucoup la qualité des résultats de sortie. Il doit être **clairement spécifié**. 
Il ne faut pas hésiter à utiliser des formats adaptés à des énumérations de type **liste à puces** ou **tableaux**:
   
##### 1️⃣ Indique clairement le type de livrable
Exemples de formulations :
- « Génère un **plan de formation structuré** sous forme de sections et sous-sections. »
- « Présente le plan sous forme de **liste hiérarchisée** (titres, sous-titres, puces). »
- « Présente le résultat sous forme de **tableau**. »

---

##### 2️⃣ Décris les rubriques attendues
Plus ton prompt est précis, plus la sortie sera exploitable :

> « Le tableau contenant les formations devra inclure :
> - Le titre   
> - Le Public cible  
> - Les pré-requis
> - Le mix théorie / pratique  
> - Les arguments pour
> - Les arguments contre »

---

##### 3️⃣ Penser à la réutilisation opérationnelle
Le livrable doit pouvoir être **copié-collé** dans :

- un plan de développement des compétences,
- un support PowerPoint,
- un plan de formation annuel.
""",
    },
    "ex3": {
        "enonce": """
🎯 **Tâche :**  
Le service EHS vous demande du support car il souhaite analyser des narratifs d'accidents et en extraire un certains nombre d'informations, telles que :
- L'age de la victime
- Son métier
- Les symptomes observés
- La cause principale de l'accident (*Root-cause*)

Ces données vont servir à alimenter un tableau de bord de suivi de l'accidentologie.
""",
        "conseils": """
Pour des demandes très spécifiques sur lesquelles n'ont pas été expressément entrainé, il convient d'indiquer de façon très fine 
le format de sortie et la façon la plus efficiente de le faire est à base d'exemples. 

##### 1️⃣ Définir un format de sortie strict et réutilisable, par exemple :
   - {"Age":"XX";"Métier":"YY";"Symptomes":"ZZ";"Cause":"WW"}
   - Age:XX | Métier:YY | Symptomes:ZZ | Cause:WW

##### 2️⃣ Utiliser deux à trois exemples :
   - Pour indiquer le format de la sortie,
   - Pour que le système puisse relier les éléments du narratif au format de sortie,

##### 3️⃣ Ne pas hésiter à apporter des définitions supplémentaires sur la nature des champs en complément des exemples :
   - Age : âge de la victime en numérique ou texte,
   - Métier : fonction principale (Opérateur, Soudeur, Monteur tôlier, etc.),
   - Symptomes : blessures ou conséquences physiques (brûlures, écrasement, décès…),
   - Cause : cause principale de l'accident (explosion, chute de charge, activation involontaire d'un équipement…).

##### 4️⃣ Préciser quoi faire si une information manque :
   - Par exemple, utiliser "Inconnu" ou "NA" pour les champs non renseignés dans le texte.

##### 5️⃣ Penser à l'exploitation ultérieure :
   - Ce format peut être injecté dans un tableau ou un modèle de classification,
   - D'où l'importance d'un format très homogène et d'expressions courtes dans Symptomes et Cause.
""",
    },
}
