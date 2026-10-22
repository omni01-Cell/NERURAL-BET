# Plan d'Implémentation Phase 2 : "The Full Picture" & Market Integration

## Analyse & Stratégie (Brainstorming Synthesis)
Basé sur le document de référence (Méthode 4D) et l'audit du code actuel, nous devons activer la **Branche B (Marché)** et approfondir la **Dimension Contextuelle (Branche A)**.

### Le Manque à Gagner (Gap Analysis)
1.  **Vision Tunnel** : Le système actuel ne voit que le terrain (Stats/Tactique), pas le contexte humain (News/Psych) ni le marché (Cotes).
2.  **Absence de "Value"** : Sans les cotes, le système prédit un vainqueur mais ne détecte pas l'opportunité financière.

---

## Plan d'Ingénieur Pro (Zero Regression)

### 1. Audit & Impact Analysis
*   **Fichiers Impactés** :
    *   `src/agents/base.py` : Modification de `AgentState` pour inclure `news_data` (Psych) et `odds_data` (Market).
    *   `src/main.py` : Orchestration parallèle (Branche A vs Branche B).
*   **Nouvelles Dépendances** :
    *   News API / Google Search (pour `PsychAgent`).
    *   The-Odds-API ou Scraper Custom (pour `MarketAgent`).
*   **Risque de Régression** : Faible. Les nouveaux agents sont additifs. Seul l'Orchestrator devra apprendre à lire les nouveaux rapports.

### 2. Filet de Sécurité (Safety Net)
*   **Mock Providers** : Création immédiate de `MockMarketProvider` et `MockNewsProvider` pour coder la logique sans dépendre d'APIs externes payantes ou instables au début.
*   **Tests Isolés** : Chaque agent sera testable unitairement avec des inputs JSON statiques (ex: Simulation d'une news "Star player injured").

### 3. Stratégie d'Implémentation (Step-by-Step)

#### Étape A : La Dimension Contextuelle (Psych Agent)
*Objectif : Donner une "Conscience" au système (Fatigue, Motivation).*
1.  **Infrastructure** : Créer `src/providers/news_provider.py` (Interface `NewsDataProvider`).
2.  **Agent Logic** : Créer `src/agents/psych.py`.
    *   *Prompt* : Analyseur de sentiments et détecteur de mots-clés ("Blessure", "Rotation", "Must win").
    *   *Input* : Titres de presse récents & Calendrier.

#### Étape B : La Branche Marché (Market Agent)
*Objectif : Voir la matrice financière.*
1.  **Infrastructure** : Créer `src/providers/market_provider.py` (Interface `MarketDataProvider`).
2.  **Agent Logic** : Créer `src/agents/market.py`.
    *   *Tâche* : Récupérer les cotes 1N2, BTTS, Over/Under.
    *   *Note* : Utilisation de `The-Odds-API` recommandée pour la stabilité (Free Tier disponible).

#### Étape C : La Synthèse Temporelle (Scenario Agent)
*Objectif : Raconter l'histoire du match (0-90min).*
1.  **Agent Logic** : Créer `src/agents/scenario.py` ( ou intégration dans Orchestrator V2).
    *   *Prompt* : Génération de timeline basée sur les inputs Tactician (Style) + Psych (Fatigue fin de match).

#### Étape D : Le Value Hunter (Convergence)
*Objectif : Décider de la mise.*
1.  **Agent Logic** : Créer `src/agents/value_hunter.py`.
    *   *Algorithme* : `(Probabilité % * Cote) - 100`.
    *   *Logique* : Comparaison aveugle entre le verdict Orchestrator et les Cotes Market.

### 4. Architecture Cible (Dossiers)

```text
src/
├── providers/
│   ├── base.py
│   ├── understat_provider.py
│   ├── fbref_provider.py
│   ├── news_provider.py       <-- NEW (Google RSS / Search)
│   └── market_provider.py     <-- NEW (Odds API)
├── agents/
│   ├── psych.py               <-- NEW
│   ├── market.py              <-- NEW
│   ├── value_hunter.py        <-- NEW
│   └── ...
```

### 5. Plan de Déploiement
1.  Implémenter les `Providers` (News/Market) avec des données Mock au début.
2.  Implémenter les agents `Psych` et `Market` et vérifier qu'ils peuplent le `State`.
3.  Connecter le `ValueHunter` en bout de chaîne.
4.  Basculer sur les APIs réelles.
