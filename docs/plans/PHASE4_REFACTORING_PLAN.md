# Plan d'Implémentation : Refactoring "Enterprise Production" (Post-Audit)

## 1. Analyse d'Impact
*   **Fichiers touchés** :
    *   `src/agents/base.py` (Centralisation de la logique)
    *   `src/agents/*.py` (Mise à jour de tous les agents pour utiliser les nouveaux helpers)
    *   `src/providers/*.py` (Gestion des sessions HTTP)
    *   `src/tui.py` (Robustesse asyncio)
*   **Risques** : Rupture de la chaîne de dépendances si les injections de providers ne sont pas correctement gérées dans le point d'entrée.

---

## 2. Filet de Sécurité (Safety Net)
*   **Test de Caractérisation** : S'assurer que `python src/tui.py` se lance sans erreur avant de commencer.
*   **Validation après chaque étape** : Vérifier que le pipeline (Touche `R`) arrive jusqu'au bout.

---

## 3. Stratégie d'Implémentation

### Étape A : Centralisation & Robustesse (DRY)
*   Modifier `BaseAgent` pour inclure un helper de gestion d'erreurs et de logging unifié.
*   Refactorer les agents pour supprimer les blocs `try...except` redondants.

### Étape B : Injection de Dépendances Rigoureuse (Couplage)
*   Supprimer les imports tardifs.
*   Modifier les constructeurs des agents (`DataMiner`, `Psych`) pour exiger des interfaces de providers.

### Étape C : Optimisation des Ressources (Performance)
*   Implémenter un gestionnaire de session `aiohttp` dans les providers pour éviter la création de sockets à chaque requête.

### Étape D : Robustesse Asyncio (TUI)
*   Ajouter un tracking des tâches dans la classe `NeuralBetApp` pour éviter les tâches "orphelines".

---

## 4. Architecture Cible (Snippets Pro)

### BaseAgent Unifié
```python
async def run_safe(self, state: AgentState, logic_func):
    self.log("Starting execution...")
    try:
        return await logic_func(state)
    except Exception as e:
        self.log(f"Error: {e}", level="error")
        state.errors.append(f"{self.name}: {e}")
        return state
```

### Provider avec Session Partagée
```python
class BaseProvider:
    def __init__(self, session=None):
        self._session = session
        self._own_session = False

    async def get_session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        return self._session
```

---

## 5. Plan de Recette
1.  **Vérification Unit** : Lancement du `main.py` (CLI).
2.  **Vérification UI** : Lancement du `tui.py` et crash-test (appuis répétés sur `R`).
3.  **Audit Final** : Relancer le diagnostic pour confirmer la résolution des points Majeurs.
