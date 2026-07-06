# 🧙 MTG Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Changelog](https://img.shields.io/badge/changelog-0.2.0-blue.svg)](CHANGELOG.md)

[Français](https://github.com/barrins-project/mtg_scraper/blob/main/README.md) | [Anglais](https://github.com/barrins-project/mtg_scraper/blob/main/README_EN.md)

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
- ⏱️ Scraping MTGO piloté par des attentes explicites Selenium (`WebDriverWait`)
  plutôt que des `sleep()` fixes : le scraper attend que la page ait
  réellement fini de se rendre, avec un timeout croissant lors des tentatives
  suivantes en cas de rendu lent

## 🚀 Utilisation

### 1. Clonage et Installation

Assurez-vous d'avoir Python 3.13+ installé, puis :

```bash
git clone https://github.com/barrins-project/mtg_scraper.git
cd mtg_scraper
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sous Windows
pip install .

# Initialisation du sous-module de réception des données
git submodule init
git submodule update
```

### 2. Lancement en CLI

Il existe deux méthodes pour lancer le scraping:

```bash
python -m scraper --source mtgtop8 --date-from 2024-05 --date-to 2024-12
scrape --source mtgtop8 --date-from 2024-05 --date-to 2024-12
```

#### Options

| Paramètre | Description | Valeur par défaut |
| --------- | ----------- | ----------------- |
| `--source` | Source des tournois : `mtgo` ou `mtgtop8` | `mtgo` |
| `--date-from` | Date de début (format `YYYY-MM`) *(**MTGO** uniquement)* | 5 jours avant |
| `--date-to` | Date de fin (format `YYYY-MM`) *(**MTGO** uniquement)* | aujourd’hui |
| `--force-mtgo` | Force le re-scrape des tournois déjà récupérés *(**MTGO** uniquement)* | Faux |
| `--span` | Nombre de tournois à inspecter *(**MTGTOP8** uniquement)* | 1000 |

### 3. Exemple de code

```python
from datetime import datetime
from scraper import services

# Télécharger les tournois d’avril 2024
services.scrape_mtgtop8(datetime(2024, 4, 1).date())
```

Il n'est actuellement pas prévu d'extraire uniquement un seul format depuis n'importe quelle
source

## 🧪 Tests

À venir — contribution bienvenue !

## 📝 Changelog

Les changements notables de chaque version sont documentés dans
[CHANGELOG.md](CHANGELOG.md), qui suit les conventions
[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et [Semantic
Versioning](https://semver.org/lang/fr/).

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
