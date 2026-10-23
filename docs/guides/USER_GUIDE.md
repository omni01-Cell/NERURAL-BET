# 📖 NEURAL BET - Guide d'Utilisation

Bienvenue dans **Neural Bet**, votre système d'analyse prédictive de football propulsé par une architecture multi-agents de pointe (Mistral, Groq, Kimi).

---

## 🛠️ 1. Prérequis & Installation

### Dépendances Python
Depuis la racine du dépôt, utilisez Python 3.12 dans un environnement virtuel, puis installez le projet et ses dépendances déclarées :
```bash
python -m venv .venv
# Activez .venv, ou utilisez directement son exécutable Python.
python -m pip install -e .
```

### Clés API (Indispensable)
Le système repose sur 3 fournisseurs d'IA majeurs. Vous devez remplir votre fichier `.env` à la racine du projet :

1.  **MISTRAL_API_KEY** : Pour les agents Metrician (Stats) et Tactician.
2.  **GROQ_API_KEY** : Pour le Devil's Advocate (Critique) et le Value Hunter.
3.  **FIREWORKS_API_KEY** : Pour le modèle **Kimi k2.5** (Orchestrateur).

*Optionnel :* `NEWS_API_KEY` (NewsAPI.org) pour des actualités réelles dans l'agent Psychologue.

---

## 🚀 2. Démarrage de l'Interface (TUI)

Pour lancer le dashboard interactif, exécutez la commande suivante :

```bash
python -m src.tui
```

### Commandes de l'Interface :
*   **Saisie puis `Entrée`** : Envoyez une demande de match dans le champ d'accueil, puis répondez aux demandes de confirmation dans la conversation.
*   **`Ctrl+Q`** : Quitte l'application.
*   **`Ctrl+D`** : Change le thème.
*   **`Ctrl+P`** : Ouvre la palette de commandes.
*   **Souris** : Vous pouvez cliquer sur les panneaux pour faire défiler les logs.

---

## 🧠 3. Comprendre le Pipeline "Double-Aveugle"

Après l'identification et la confirmation du match dans la conversation, le système exécute les étapes suivantes :

1.  **Extraction (Data Miner)** : Récupère les stats brutes (xG, forme, etc.).
2.  **Analyse Sportive (Branche A)** :
    *   **Metrician** : Détecte la variance et la chance.
    *   **Tactician** : Étudie les styles de jeu.
    *   **Psych** : Analyse le moral et le contexte news.
    *   **Devil's Advocate** : Tente de détruire le consensus pour éviter le biais de confirmation.
3.  **Synthèse (Orchestrator)** : Kimi k2.5 pondère les rapports et rend un **Verdict**.
4.  **Analyse Marché (Branche B)** : Scanne les cotes actuelles.
5.  **Convergence (Value Hunter)** : Calcule si le verdict de l'IA offre une opportunité financière (EV+).

---

## 📊 4. Lecture des Résultats

*   **Le Panneau central (Logs)** : Affiche les "réflexions" en temps réel. C'est ici que vous verrez les arguments tactiques et les critiques du Devil's Advocate.
*   **Verdict Final** : Apparaît à la fin du log avec un score de confiance (0-100%).
*   **Opportunité de Valeur** : Si une cote mathématiquement intéressante est détectée, elle sera surlignée en jaune.

---

## ⚠️ 5. Dépannage
*   **Erreur d'API** : Vérifiez que vos clés sont valides et que vous avez des crédits sur les plateformes respectives (Fireworks, Mistral, Groq).
*   **Interface figée** : La TUI utilise `asyncio`. Si un agent met trop de temps (timeout réseau), attendez quelques secondes ou vérifiez votre connexion.

---

### *Bonne analyse avec NEURAL BET !* ⚽💸
