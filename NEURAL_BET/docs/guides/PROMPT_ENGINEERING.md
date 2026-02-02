# 🏗️ Guide de Prompt Engineering (Standard Anthropic 2026)

Pour maximiser la précision des agents de **NEURAL BET**, nous suivons les meilleures pratiques édictées par Anthropic (Claude) et adaptées aux modèles SOTA (Mistral, Groq, Kimi).

## 1. Utilisation de balises XML
Les modèles modernes sont entraînés pour porter une attention particulière aux structures délimitées par des balises XML. Cela permet de séparer clairement les instructions des données.

**Exemple :**
```xml
<instructions>
Analyse les données suivantes...
</instructions>

<data>
{ "xg": 1.5 }
</data>
```

## 2. Chaîne de Pensée (Chain of Thought)
Demander à l'IA de "réfléchir" avant de répondre augmente drastiquement la qualité du raisonnement logique. Nous utilisons la balise `<thinking>` pour cela.

## 3. Personnalisation de Persona
Chaque agent doit avoir une identité forte, un rôle précis et des contraintes de ton.

## 4. Format de Sortie Strict
Toujours spécifier le format attendu (JSON, Markdown, Bullets) pour faciliter l'intégration.

## 5. Gestion de l'Incertitude
Autoriser explicitement l'agent à dire "Je ne sais pas" ou "Données insuffisantes" pour éviter les hallucinations.
