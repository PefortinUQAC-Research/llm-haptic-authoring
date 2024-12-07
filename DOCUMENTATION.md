# Génération Audio : Fonctionnement et Méthodes en Détail

Ce document fournit une vue d’ensemble complète du processus de génération audio dans l’application, y compris les méthodes et composants clés.

## Vue d’Ensemble de la Génération Audio

L’application génère des fichiers audio à partir de descriptions de sensations tactiles fournies par l’utilisateur. Elle utilise :
- **Modèles de Langage (LLM)** : Pour créer des descriptions détaillées en termes de feedback haptique.
- **AudioCraft** : Pour générer des fichiers audio basés sur ces descriptions.
- **Interface Graphique (GUI)** : Une interface conviviale pour les entrées, la configuration et les résultats.

Le processus comprend :
1. La saisie par l’utilisateur d’une description de sensation tactile.
2. L’utilisation du LLM pour créer des descriptions détaillées.
3. Le raffinage des descriptions grâce à des options avancées (ex. : feedback de l’utilisateur).
4. La génération des fichiers audio avec AudioCraft.
5. La lecture et la gestion des fichiers générés.

---

## Composants et Méthodes Clés

### 1. **Interface Graphique (GUI)**
L’interface graphique permet aux utilisateurs d’interagir avec le programme. La classe principale pour la GUI est `AppGUI`.

#### **Méthodes dans la GUI**
- `generate_output` : Lance le processus de génération audio en coordonnant les entrées et les sorties.
- `regenerate_response` : Permet aux utilisateurs de régénérer les sorties du LLM.
- `edit_with_llm` : Permet aux utilisateurs de fournir des commentaires pour affiner les réponses du LLM.

---

### 2. **Intégration avec le LLM**
Le LLM gère la création de descriptions détaillées pour les sensations tactiles. Il prend en charge :
- **Prompt 1** : Convertit une entrée tactile de l’utilisateur en description détaillée.
- **Prompt 2** : Traduit cette description en une analogie sonore quotidienne.

#### **Méthodes dans le LLM**
- `generate_description_prompt1` : Génère une description détaillée basée sur l’entrée utilisateur.
- `generate_description_prompt2` : Traduit la description en termes sonores.
- `generate_edited_prompt` : Ajuste les réponses du LLM selon le feedback de l’utilisateur.

---

### 3. **Génération Audio avec AudioCraft**
AudioCraft est l’outil principal utilisé pour générer les fichiers audio. La classe `VibrotactileGenerator` gère l’intégration avec AudioCraft.

#### **Méthodes dans l’Intégration avec AudioCraft**
- `update_model_settings` : Configure les paramètres de génération comme la durée et l’échantillonnage.
- `generate_model` : Génère des fichiers audio à partir des descriptions fournies par le LLM.

---

### 4. **Mode Avancé**
Le mode avancé permet aux utilisateurs de revoir et d’affiner manuellement les descriptions avant de procéder à la génération des fichiers audio.

#### **Fonctionnalités Clés**
- Les utilisateurs peuvent examiner et modifier les prompts en détail.
- Les réponses peuvent être régénérées en utilisant le LLM avec un feedback personnalisé.
- Les prompts finalisés sont transmis à AudioCraft pour générer l’audio.

---

## Étapes de la Génération Audio

1. **Saisie** :
   - L’utilisateur fournit une description de sensation tactile via la GUI.

2. **Création de Description** :
   - `generate_description_prompt1` génère une description détaillée de la sensation.
   - L’utilisateur peut revoir et affiner cette sortie.

3. **Traduction en Terme Sonore** :
   - `generate_description_prompt2` traduit la description en caractéristiques sonores.

4. **Génération de Fichiers Audio** :
   - Le prompt finalisé est transmis à AudioCraft.
   - AudioCraft génère des fichiers audio en fonction des descriptions et des paramètres de durée.

5. **Lecture et Gestion** :
   - Les fichiers audio générés peuvent être écoutés ou gérés dans le répertoire de sortie.

---

## Validation des Entrées

Le programme inclut une validation robuste des entrées pour :

- **Nombre de générations** : Vérifie un entier positif.
- **Durée** : Valide un nombre à virgule flottante supérieur à zéro.
- **Descriptions** : Vérifie que les entrées ne sont pas vides, etc.

---

## Gestion des Erreurs

Le programme utilise :

- **Blocs try-except** : Capturent et signalent les erreurs lors de la génération des réponses du LLM et des fichiers audio.
- **Messages d’avertissement et d’erreur** : Fournissent un retour direct à l’utilisateur dans la GUI.

---

## Gestion des Sorties

Les fichiers audio générés sont sauvegardés dans le répertoire de sortie spécifié. La convention de nommage inclut :

- **Nom de fichier** : Basé sur le nom généré par le LLM ou fourni par l’utilisateur.
- **Itération** : Ajoutée pour les générations multiples.

### Exemple :  
`output_file_0.wav`, `output_file_1.wav`

---

## Fonctionnalités Avancées

- **Feedback Itératif** :
  - Les utilisateurs peuvent fournir des commentaires pour améliorer les prompts.
  - L’application intègre ce feedback de manière dynamique.

- **Générations Multiples** :
  - Les utilisateurs peuvent spécifier le nombre de fichiers audio à générer.
  - Utile pour créer des variations de la même sensation tactile.

- **Configuration des Paramètres** :
  - Les paramètres ajustables incluent les paramètres API du LLM, la température et les chemins de sauvegarde.

---

Ce guide détaillé met en lumière l’intégration des LLM, d’AudioCraft et de la GUI pour une génération audio fluide. Chaque couche et méthode est conçue pour offrir flexibilité et contrôle à l’utilisateur.
