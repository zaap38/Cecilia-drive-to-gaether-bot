# Q-Learning pour DriveToGaether

**Auteurs : ALCARAZ Benoît & DEVILLERS Alexandre**



⚠️ Ce README a été généré par [ChatGPT](https://chat.openai.com/), nous avons effectué une relecture, mais il peut rester des coquilles. ⚠️



Nous avons développé un simulateur pour tester notre algorithme d'apprentissage par renforcement. Afin de remplacer le deuxième robot, qui était initialement joué par un humain, nous avons introduit un robot qui effectue des actions aléatoires dans l'environnement.

Après un entraînement de 3 millions d'étapes, soit environ 15 minutes, notre agent est capable de se déplacer pour ramasser les victimes et les rapporter à l'hôpital. Nous avons constaté que notre agent prend parfois une ou deux victimes en fonction des configurations. De plus, nous avons observé que notre agent évite les situations où il pourrait être bloqué, par exemple en avançant face à l'autre agent dans une ligne droite (sachant qu'ils ne peuvent pas faire demi-tour).

Ces résultats démontrent que notre algorithme d'apprentissage par renforcement a réussi à former un agent capable de prendre des décisions intelligentes et d'accomplir efficacement sa tâche dans l'environnement simulé.



Ce projet contient deux classes principales : `RLAgent` et `Environment`, qui sont utilisées pour implémenter un agent d'apprentissage par renforcement (RL) dans un environnement de simulation.



## RLAgent

  

La classe `RLAgent` représente un agent d'apprentissage par renforcement. Voici les principaux attributs et méthodes de la classe :

  

- `id`: Identifiant de l'agent (facultatif).

- `q`: Dictionnaire pour stocker les valeurs Q des états-actions.

- `epsilon`: Paramètre d'exploration pour l'agent.

- `discountEpsilon`: Taux de réduction de l'exploration.

- `gamma`: Facteur de remise pour les récompenses futures.

- `eta`: Taux d'apprentissage.

- `environment`: Référence à l'instance de la classe `Environment` pour l'agent.

- `lastReward`: Dernière récompense reçue par l'agent.

- `lastAction`: Dernière action effectuée par l'agent.

  

Méthodes principales :

  

- `getRandomPolicy()`: Retourne une action aléatoire parmi les actions légales.

- `getBestPolicy(state)`: Retourne la meilleure action possible pour un état donné en utilisant les valeurs Q.

- `getBestPolicyReward(state)`: Retourne la valeur Q de la meilleure action possible pour un état donné.

- `updateQValues(old_state, actionDone, state, reward, final=False)`: Met à jour les valeurs Q en fonction de la récompense reçue et des transitions d'états.

- `selectAction(state, forceExplore=False, debug=False)`: Sélectionne une action à prendre en fonction de l'état actuel de l'agent.

  

## Environment

  

La classe `Environment` représente l'environnement de simulation dans lequel l'agent évolue. Voici les principaux attributs et méthodes de la classe :

  

- `w`: Largeur de l'environnement.

- `h`: Hauteur de l'environnement.

- `cellGrid`: Grille de cellules représentant l'état de l'environnement.

- `saved`: Nombre de victimes sauvées.

- `step`: Compteur d'étapes.

  

Méthodes principales :

  

- `runStep(agent, idiotDuVillage=False)`: Exécute une étape de simulation pour l'agent donné.

- `getLegalActions(agentId)`: Retourne les actions légales pour un agent donné.

- `setCell(x, y, agentIndex=-1, agentOrientation=Orientation.UP, agentInventory=[], hospitalIndex=-1, startIndex=-1, startOrientation=Orientation.UP, victimIndex=-1, openOrientations=set())`: Modifie l'état d'une cellule spécifiée.

- `doAction(agentId, action)`: Effectue une action pour un agent donné et retourne la récompense correspondante.

- `doLeft(agentId)`, `doMove(agentId)`, `doRight(agentId)`, `doPick(agentId)`, `doDrop(agentId)`, `doNone(agentId)`: Méthodes internes pour effectuer des actions spécifiques.

- `isFinal()`: Vérifie si l'environnement est dans un état final.

- `reset()`: Réinitialise l'environnement à son état initial.

- `_getCellAgent(agentId)`: Retourne la cellule où se trouve un agent donné.

- `simulateMove(cell, orientation)`: Simule le déplacement d'une cellule dans une certaine orientation.

- `_moveOrientation(orientation, cell)`: Effectue le déplacement d'une cellule dans une certaine orientation.

  

## Exemple d'utilisation
```bash
python3 main.py
```



Le fichier `main.py` contient un exemple d'utilisation des classes `RLAgent` et `Environment`. Il crée une instance de la classe `Environment`, initialise un agent d'apprentissage par renforcement (`RLAgent`), puis effectue un certain nombre d'étapes de simulation en utilisant la méthode `runStep()` de l'environnement.

  

La simulation se déroule jusqu'à ce que l'environnement atteigne un état final ou que le nombre d'étapes atteigne une limite (150 dans cet exemple). L'agent utilise la méthode `selectAction()` pour choisir une action à chaque étape, en fonction de son état actuel et des valeurs Q apprises.

  

N'hésitez pas à personnaliser et à adapter le code pour répondre à vos besoins spécifiques.