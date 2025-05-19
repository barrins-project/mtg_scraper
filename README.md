# 🧙 MTG Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)


Un scraper modulaire et multithreadé pour récupérer les résultats de tournois Magic: The Gathering depuis plusieurs sources, notamment **MTGO** et **MTGTop8**.
Conçu pour être intégré dans des pipelines de collecte de données, ce projet alimente une base d’analyse statistique et de visualisation dédiée aux formats compétitifs comme **Duel Commander**, **EDH**, ou **Modern**.

## 📦 Fonctionnalités

- 🔎 Scraping de tournois depuis :
  - [x] MTGO (via HTML scraping multithread par émulation de navigateur Chrome)
  - [x] MTGTop8 (via HTML scraping multithread)
- 📅 Filtrage par format (`Standard`, `Modern`, `Duel Commander`, etc.) et plage de dates
- 📂 Sortie au format JSON standardisée
- 🧵 Téléchargement parallèle pour accélérer l’extraction
- 🧪 Prêt pour intégration backend (FastAPI) et machine learning

## 🚀 Utilisation

### 1. Clonage et Installation

Assurez-vous d'avoir Python 3.10+ installé, puis :

```bash
git clone https://github.com/barrins-project/mtg_scraper.git
cd mtg_scraper
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sous Windows
pip install .

### 2. Lancement en CLI

Il existe deux méthodes pour lancer le scraping:

```bash
python -m scraper --source mtgtop8 --date-from 2024-05 --date-to 2024-12
scrape --source mtgtop8 --date-from 2024-05 --date-to 2024-12
```

#### Options

| Paramètre     | Description                                        | Valeur par défaut |
| ------------- | -------------------------------------------------- | ----------------- |
| `--source`    | Source des tournois : `mtgo` ou `mtgtop8`          | `mtgo`            |
| `--date-from` | Date de début (format `YYYY-MM`) (MTGO uniquement) | 5 jours avant     |
| `--date-to`   | Date de fin (format `YYYY-MM`) (MTGO uniquement)   | aujourd’hui       |

### 3. Exemple de code

```python
from scraper import services

# Télécharger les tournois d’avril 2024
services.scrape_mtgtop8("2024-04")
```

Il n'est actuellement pas prévu d'extraire uniquement un seul format depuis n'importe quelle
source

## 🧪 Tests

À venir — contribution bienvenue !

## 📈 Intégration recommandée

Ce projet est conçu pour s’intégrer à un pipeline d’analyse de decks Magic (via base de données + FastAPI).
Tu peux notamment l’utiliser dans un `cronjob` ou depuis une interface admin.

## 🤝 Contribuer

Les contributions sont bienvenues ! Pour toute suggestion ou amélioration :

1. Fork le dépôt
2. Crée une branche `feature/ma-fonctionnalite`
3. Envoie une PR ✨

## 📜 Licence

MIT – libre de réutilisation dans vos projets.

---

**Projet parent :** [barrins-project](https://github.com/barrins-project)
Pour toute question, contact via GitHub ou Discord.
