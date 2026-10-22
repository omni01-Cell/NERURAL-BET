# Plan d'Implémentation Phase 3 : Terminal User Interface (TUI)

## Objectif
Transformer le script CLI linéaire en une application interactive "Dashboard" style Cyberpunk/Trader, utilisant la bibliothèque **Textual**.

## Référence Esthétique
*   **Style** : OpenCode / Bloomberg Terminal moderne.
*   **Couleurs** : Dark Background, Neon Green (Profit), Warning Orange (Alerts), Electric Blue (Structure).
*   **UX** : Navigation clavier/souris, Logs défilants, Tableaux de données dynamiques.

---

## Plan Technique (Engineering Standard)

### 1. Architecture UI (`src/ui/`)
Nous séparons la logique d'affichage du cœur de l'IA.

```text
src/
└── ui/
    ├── app.py              # Point d'entrée TUI
    ├── styles.tcss         # Feuille de style CSS
    ├── widgets/
    │   ├── header.py       # Custom Cyber Header
    │   ├── log_panel.py    # Affichage temps réel des logs agents
    │   ├── match_view.py   # Carte du match (Score, Cotes)
    │   └── agent_status.py # Indicateur d'activité (Spinner)
    └── screens/
        └── dashboard.py    # Écran principal (Grid Layout)
```

### 2. Pont Logique (The Bridge)
Le défi est de connecter le pipeline `asyncio` existant (Agents) à la boucle d'événements de Textual.

*   **Composant Clé** : `PipelineController`
*   **Mécanisme** : 
    1.  L'App Textual lance le pipeline dans un `asyncio.create_task`.
    2.  Les `Agents` écrivent des logs via le module standard `logging`.
    3.  Un `TextualLogHandler` personnalisé capture ces logs et les envoie au widget `LogPanel` via `post_message`.

### 3. Étapes d'Implémentation

#### Étape A : Fondations & Dépendances
*   Ajout de `textual` aux requirements.
*   Création de la structure de dossiers.

#### Étape B : Le Logging Handler
*   Créer une classe qui hérite de `logging.Handler`.
*   Elle doit appeler `app.query_one(LogPanel).write()` de manière thread-safe.

#### Étape C : Widgets de Base
*   **Header** : Titre "NEURAL BET", Heure, Statut API.
*   **LogPanel** : `RichLog` widget pour afficher les messages colorés.
*   **ControlPanel** : Bouton "RUN ANALYSIS" pour lancer le script.

#### Étape D : Intégration du Pipeline
*   Modifier `main.py` (ou créer `tui_integration.py`) pour accepter une instance de callback ou un signal.
*   Lier le bouton "Start" à l'exécution de `orchestrator.process()`.

### 4. Code "Squelette" (Proof of Concept)

*Le fichier `tui.py` servira de nouveau point d'entrée.*

```python
# Exemple conceptuel
class NeuralBetApp(App):
    CSS_PATH = "ui/styles.tcss"
    def compose(self):
        yield Header()
        yield Grid(
            MatchInfoWidget(id="match_info"),
            LogPanel(id="logs"),
            ActionPanel(id="actions")
        )
```
