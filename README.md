# Générateur Audio Vibrotactile

Le Générateur Audio Vibrotactile est une application avancée en Python conçue pour générer et lire des fichiers audio imitant des sensations tactiles. Cet outil est idéal pour les développeurs et chercheurs travaillant sur des projets liés à la rétroaction haptique, en particulier dans les jeux vidéo et les applications de réalité étendue (XR).

## Fonctionnalités

- **Génération Audio** : Utilise un modèle de langage (LLM) pour produire des descriptions vibrotactiles détaillées et AudioCraft pour générer les fichiers audio correspondants.
- **Mode Avancé** : Permet aux utilisateurs de modifier les réponses du LLM avec des retours avant de générer l’audio.
- **Lecture Audio** : Lecteur intégré pour écouter les fichiers audio générés.
- **Paramètres Personnalisables** : Modifiez les paramètres du LLM, des chemins de sauvegarde et des options de génération.
- **Gestion des Fichiers** : Parcourez et gérez facilement les fichiers générés.

## Comment ça fonctionne

1. **Entrer une description** : Fournissez une description d’une sensation tactile.
2. **Générer une description** : Le LLM génère une description détaillée en termes de feedback haptique vibrotactile.
3. **Créer l’audio** : AudioCraft transforme la description générée par le LLM en un fichier audio.
4. **Revoir et ajuster** : Utilisez le mode avancé pour apporter des modifications de manière itérative.
5. **Lecture** : Écoutez les fichiers audio générés directement dans l’application.

## Configuration

Le fichier `config.py` contient les paramètres personnalisables :
- `model_name` : Spécifie le modèle LLM à utiliser.
- `api_url` : URL de base pour l'API du LLM.
- `temperature` : Contrôle la variabilité des réponses du LLM (valeurs plus élevées = plus de variabilité).
- `default_save_path` : Chemin pour sauvegarder les fichiers audio générés.
- `advanced_mode_enabled` : Active ou désactive le mode avancé au démarrage.

Modifiez les paramètres selon vos besoins avant de lancer l’application.

## Structure des fichiers

Voici un aperçu de la structure du projet :

- **`main.py`** : Point d'entrée de l'application.
- **`gui.py`** : Implémente l'interface utilisateur graphique.
- **`logic.py`** : Utilise AudioCraft pour générer les fichiers audio à partir des descriptions.
- **`audio_player.py`** : Gère la lecture audio.
- **`llm.py`** : Génère des descriptions vibrotactiles à l’aide d’un modèle de langage (LLM).
- **`utils.py`** : Fonctions utilitaires pour sauvegarder et gérer les fichiers audio.
- **`config.py`** : Fichier de configuration des paramètres.

### Installation des Dépendances

Pour exécuter ce programme, suivez les étapes suivantes :

1. **Installer Python 3.10**  
   Le programme a été testé avec Python 3.10, car lors de mes essais, je n’ai pas pu faire fonctionner AudioCraft avec d'autres versions. Si vous parvenez à faire fonctionner AudioCraft avec une version plus récente, vous pouvez l’utiliser sans problème.  
   Vous pouvez télécharger Python 3.10 depuis [python.org](https://www.python.org/).

2. **Installer AudioCraft et ses dépendances**  
AudioCraft est utilisé pour générer les fichiers audio. Suivez les instructions d’installation fournies dans le dépôt officiel d’AudioCraft :  
[Installation d'AudioCraft](https://github.com/facebookresearch/audiocraft/tree/main).

Voici les instructions qu'ils donnent:
AudioCraft requires Python 3.9, PyTorch 2.1.0. To install AudioCraft, you can run the following:
```
# Best to make sure you have torch installed first, in particular before installing xformers.
# Don't run this if you already have PyTorch installed.
python -m pip install 'torch==2.1.0'
# You might need the following before trying to install the packages
python -m pip install setuptools wheel
# Then proceed to one of the following
python -m pip install -U audiocraft  # stable release
python -m pip install -U git+https://git@github.com/facebookresearch/audiocraft#egg=audiocraft  # bleeding edge
python -m pip install -e .  # or if you cloned the repo locally (mandatory if you want to train).
python -m pip install -e '.[wm]'  # if you want to train a watermarking model
```

We also recommend having ffmpeg installed, either through your system or Anaconda:
```
sudo apt-get install ffmpeg
# Or if you are using Anaconda or Miniconda
conda install "ffmpeg<5" -c conda-forge
```

3. **Installer LangChain et LangChain OpenAI**  
LangChain est utilisé pour gérer les interactions avec les modèles de langage. Installez LangChain ainsi que LangChain OpenAI avec les commandes suivantes :  
```
pip install langchain langchain-openai
```

4. **Installer `pygame` pour la lecture audio**  
Utilisez la commande suivante pour installer `pygame` :  
```
pip install pygame
```

5. **Vérifiez la disponibilité de Tkinter**  
Tkinter est utilisé pour l'interface graphique et est généralement inclus par défaut avec Python. Si ce n'est pas le cas, installez-le via votre gestionnaire de paquets :  
- Sur **Ubuntu/Linux** :  
  ```
  sudo apt-get install python3-tk
  ```
- Sur **Windows/MacOS**, il est inclus avec l'installation standard de Python.

6. **Tester l'installation**  
Une fois toutes les dépendances installées, exécutez le programme pour vérifier qu’il fonctionne correctement :  
```
python main.py
```

### Remarques

- **Python 3.10** est recommandé, car AudioCraft n'a pas fonctionné avec d'autres versions lors de mes tests. Si vous réussissez à le faire fonctionner avec une version plus récente de Python, vous pouvez l’utiliser sans problème.  
- Veillez à bien suivre les instructions d’installation d’AudioCraft, car il installe également des dépendances importantes comme PyTorch et Torchaudio.

Si vous rencontrez des problèmes, assurez-vous que toutes les étapes ont été suivies correctement et que vos bibliothèques sont à jour.

## Utilisation

### Mode Normal
1. Ouvrez l'application et entrez une description d’une sensation tactile dans le champ de saisie.
2. Cliquez sur **Démarrer** pour générer une description et créer un fichier audio.
3. Revoyez l’audio généré dans l’onglet **Lecture Audio**.

### Mode Avancé
1. Cochez l’option **Mode Avancé** dans l’onglet **Génération Audio**.
2. Modifiez et affinez les réponses du LLM de manière itérative.
3. Générez l’audio après avoir finalisé les réponses.

### Lecture et Gestion
- Utilisez l’onglet **Lecture Audio** pour écouter les fichiers audio.
- Ouvrez le dossier de sortie pour gérer les fichiers générés.

## Technologies Utilisées

- **Python** : Langage de programmation principal.
- **Tkinter** : Cadriciel GUI pour des interfaces multiplateformes.
- **LangChain** : Génère les descriptions vibrotactiles via le LLM.
- **AudioCraft** : Transforme les descriptions en fichiers audio.
- **PyGame** : Support pour la lecture audio.
- **TorchAudio** : Pour la sauvegarde et le traitement des fichiers audio.
