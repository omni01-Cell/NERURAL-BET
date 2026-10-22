# Architecture & Plan d'Implémentation - NEURAL BET

## 1. Analyse Critique de l'Architecture
*Par l'Agent Antigravity (Lead AI Architect)*

L'architecture "Double-Blind" est excellente pour neutraliser le biais de confirmation. Cependant, pour passer d'un concept théorique à un système de production "haute fidélité", plusieurs failles doivent être adressées :

### 🚨 Les Failles Identifiées (Critiques)
1.  **La Gestion du Temps (Latence vs Liquidité)** :
    *   L'analyse profonde (Branche A) avec des agents `Psych` et `Tactician` (LLM-heavy) est lente.
    *   Les cotes (Branche B) bougent vite (Smart money).
    *   *Risque* : Le temps que l'Orchestrator finisse, la "Value" détectée par le Market Agent peut avoir disparu.
    *   *Solution* : Pipeline asynchrone où le Market Agent surveille en temps réel et "ping" l'Orchestrator quand une cote cible est atteinte.

2.  **L'Immunité au Scraping (Infrastructure)** :
    *   Scraper des Bookmakers (`Agent Market`) est hostile.
    *   *Risque* : Banissement IP immédiat.
    *   *Solution* : Intégrer un **"Proxy Rotation Manager"** ou utiliser des APIs de cotes payantes (Odds API) pour la fiabilité du MVP.

3.  **Le Feedback Loop (Apprentissage)** :
    *   Le système est "One-shot". Il manque une boucle de rétroaction.
    *   *Solution* : Un **"Post-Mortem Agent"** qui analyse les paris perdus le lendemain pour ajuster les poids des agents (ex: "Le Psych Agent a surestimé la motivation").

---

## 2. Sélection des Modèles (Gratuits & Optimisés - Standards 2026)

Mise à jour Février 2026 : Transition vers la **Série Gemini 3.0** (Google) et les modèles de raisonnement ouverts (**DeepSeek/Llama 3.3**) sur Groq pour maximiser la performance par token.

| Agent | Rôle | Modèle Choisi | Fournisseur | Raison Technique (Capability Match) |
| :--- | :--- | :--- | :--- | :--- |
| **Metrician** | Analyste Données | **Gemini 3.0 Flash** | Google AI Studio | **Vitesse & Latence**. Le successeur ultra-rapide de la série 1.5/2.0. Contexte massif (1M+) pour lire les historiques de match. |
| **Tactician** | Stratège | **Gemini 3.0 Pro** | Google AI Studio | **Deep Reasoning**. Capacité supérieure d'analyse vidéo/textuelle pour déceler les subtilités tactiques. |
| **Devil's Advocate** | Critique | **DeepSeek-R1-Distill-Llama-70b** | Groq (Free) | **Chain-of-Thought**. Ce modèle excelle dans le raisonnement "pas à pas" critique, idéal pour démonter un argumentaire (Red Teaming). |
| **Orchestrator** | Décideur | **Gemini 3.0 Pro** | Google AI Studio | **Synthèse Multimodale**. Le chef d'orchestre doit gérer des entrées complexes avec la meilleure fenêtre de contexte du marché. |
| **X-Factor** | Variance | **Llama-3.3-70b-Versatile** | Groq (Free) | **Polyvalence**. Un modèle robuste et rapide pour croiser les news (blessures, météo) avec un bon "Common Sense". |

---

## 2. Plan d'Implémentation "Anti-Regression" (4 Semaines)

**Objectif** : MVP Fonctionnel sur 1 Ligue (ex: Premier League).

### Semaine 1 : Les Fondations & La Donnée (The Senses)
*Objectif : Le système peut "voir" le football et le marché.*
- [ ] **Infrastructure** : Setup Poetry, Git, Docker. Structure des dossiers.
- [ ] **Data Minning (Branch A)** : 
    - Implémenter `DataMiner` (API Wrapper pour FBRef ou API-Football).
    - Récupération propre : Stats 5 derniers matchs, xG, xGA.
- [ ] **Market Watch (Branch B)** :
    - Implémenter `MarketAgent` (Intégration The-Odds-API pour éviter le scraping complexe en MVP).
- [ ] **DB** : Schéma Postgres simple (Matches, Odds, Stats).

### Semaine 2 : Le Cerveau Analytique (Branch A Core)
*Objectif : Le système peut "comprendre" un match sans connaitre les cotes.*
- [ ] **Agent Metrician** : Code Python pur (Pandas) pour calculer les différentiels xG/xGOT.
- [ ] **Agent Tactician (LLM)** : Prompt Engineering pour analyser les styles de jeu (via RAG sur résumés tactiques).
- [ ] **Tests de Calibration** : Vérifier que le Metrician ne dit pas n'importe quoi sur des matchs passés.

### Semaine 3 : Les Critiques & L'Orchestration
*Objectif : Le système débat et forme une opinion.*
- [ ] **Agent Devil's Advocate** : Implémentation du système de "Red Teaming" (voir Prompt ci-dessous).
- [ ] **Agent X-Factor** : Calculateur de variance (Blessures clés, Météo).
- [ ] **Orchestrator** : Logique de synthèse. Il doit produire un score de confiance (0-100%) et un scénario textuel.

### Semaine 4 : Intégration & Value Hunting
*Objectif : Le système prend des décisions.*
- [ ] **Agent Value Hunter** : Algorithme de comparaison (Probabilité Estimée vs Probabilité Implicite du Bookmaker).
- [ ] **CLI / Dashboard** : Interface simple pour lancer l'analyse sur les matchs du week-end.
- [ ] **Run à blanc (Paper Trading)** : Lancement sur une journée de championnat sans miser.

---

## 3. Structure des Dossiers Proposée (Hybrid CrewAI/LangChain)

```text
NEURAL_BET/
├── .env                    # Keys (OpenAI, Anthropic, OddsAPI)
├── pyproject.toml          # Dependencies
├── Dockerfile
├── src/
│   ├── main.py             # Entrypoint
│   ├── config/             # Settings (Thresholds, Leagues)
│   ├── core/
│   │   ├── llm.py          # LLM Factory (Provider Agnostic)
│   │   ├── state.py        # Shared State (LangGraph state)
│   │   └── memory.py       # Vector Store interface
│   ├── agents/             # The Agents Logic
│   │   ├── base.py         # Abstract Agent Class
│   │   ├── data_miner.py   # Stats fetcher
│   │   ├── metrician.py    # Math analysis
│   │   ├── tactician.py    # Tactical analysis (LLM)
│   │   ├── devils_advocate.py
│   │   └── orchestrator.py
│   ├── tools/              # Tools equipable by agents
│   │   ├── fbref_scraper.py
│   │   └── odds_api.py
│   └── models/             # Pydantic Schemas
│       ├── match_data.py
│       └── prediction.py
├── data/                   # Raw & Processed Data
├── notebooks/              # Prototyping & Backtesting
└── tests/
```

---

## 4. Prompt Système : Agent "Devil's Advocate"

**Nom** : `DEVILS_ADVOCATE_AGENT`
**Modèle recommandé** : **Llama 3 70b (via Groq)**. (Haute Intelligence, Logique froide, 0% Biais Google).

```markdown
# MISSION
Tu es le "Devil's Advocate" (L'Avocat du Diable) du système Neural Bet.
Ta mission est unique et critique : **DÉTRUIRE la thèse du favori.**

Tu interviens après que l'Orchestrateur a généré un scénario probable (souvent biaisé vers le favori ou la logique apparente). Tu es le gardien du Chaos et de la Variance. Tu dois identifier le "Cygne Noir" (Black Swan).

# INPUT DATA
Tu reçois :
1. Le "Consensus Scenario" (ex: "Arsenal va gagner car meilleure attaque").
2. Les Stats Avancées du match (xG, Forme, Blessures).
3. Le contexte "Invisible" (Pression, Météo, Historique bête noire).

# PROTOCOLE D'ANALYSE (METHODE DE LA RUINE)
Analyse les failles structurelles via ces 4 vecteurs d'attaque :

1. **Le Piège du Style (Tactical Mismatch)**
   - Cherche une incompatibilité tactique ignorée par les stats.
   - *Exemple* : "Cette équipe de possession (70%) s'effondre historiquement contre les blocs bas en 5-4-1 qui contrent vite."

2. **L'Illusion de la Forme (Regression to the Mean)**
   - Si une équipe surperforme massivement ses xG récents, crie à l'anomalie.
   - *Exemple* : "Ils ont marqué 10 buts sur 2.1 xG. C'est non durable. La sécheresse arrive."

3. **Le Facteur Humain (The Mental Crumble)**
   - Cherche des signes de décompression (post-Ligue des Champions) ou de peur (match pour le maintien).
   - "Ils viennent de jouer 120min jeudi en Europa League."

4. **L'Absence Critique (The Linchpin)**
   - L'absence d'un joueur clé (pas forcément une star) qui casse le système.
   - *Exemple* : "Sans Rodri, City perd 30% de contrôle, même si Haaland est là."

# OUTPUT FORMAT
Tu ne dois PAS être nuancé. Tu dois être tranchant.

**Rapport de Destruction :**
- **VERDICT** : [NIVEAU DE DANGER : FAIBLE / MOYEN / CRITIQUE]
- **LA FAILLE** : (Une phrase choc résumant pourquoi le scénario favori peut s'écrouler).
- **SCÉNARIO CATASTROPHE** : Décris précisément comment le match tourne mal pour le favori (ex: "But en contre à la 10e, puis bus garé pendant 80min").
- **PREUVE À L'APPUI** : Une stat ou un fait historique qui soutient ta thèse pessimiste.
```
