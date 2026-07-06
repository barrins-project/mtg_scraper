# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-06

### Fixed

- **MTGO scraper reliability**: `scrape_tournament` and `get_mtgo_tournaments` used
  a fixed `time.sleep()` after loading a page before reading the DOM. Since
  mtgo.com decklist pages render client-side, a slow render (common under the
  4-thread concurrent load used in CI) meant the date element wasn't in the DOM
  yet, which aborted the whole tournament extraction (`⚠️ Aucune balise
  contenant la date a été trouvée.`). After exhausting all retries, affected
  tournaments were silently skipped, losing data.
- **CI push race condition**: the daily scraping workflow and the biweekly
  Sunday workflow are both scheduled at `22:00 UTC` and both commit/push to the
  same `scraped` submodule and to `main`. On Sundays they could run
  concurrently, and the submodule push had no rebase step, risking a rejected
  (non-fast-forward) push and a failed run.
- **`CircuitPlayer.from_raw` union detection**: the field-type coercion in
  `scraper/schemas/player.py` unwrapped `Optional`/`Union` field annotations by
  checking `get_origin(expected) is Union`, which only matches the legacy
  `typing.Optional[X]` / `typing.Union[X, None]` spelling. On Python 3.12/3.13
  (the versions this project actually targets and runs in CI), the modern
  `X | None` syntax now used everywhere else in this codebase produces a
  distinct `types.UnionType` at runtime, so an `Optional` field written that
  way would silently skip unwrapping and the `str`/`bool` coercion below it.
  No current field triggers this (bug was latent), but it would have broken
  silently the moment one was added. The check now also matches
  `types.UnionType`.

### Security

- Removed the `webdriver-manager` dependency. `selenium` (already required,
  ≥4.6) bundles its own first-party Selenium Manager, which resolves and
  downloads the matching Chrome driver directly from Google's official
  distribution points. `webdriver-manager` was a third-party package whose
  entire job was downloading and executing a native binary — dropping it
  shrinks the dependency graph and removes one more party that would need to
  be compromised to tamper with the driver binary this project executes
  unattended, on a schedule, with repo-write credentials.
  `scraper/utils/selenium_driver.py::init_driver` now builds
  `Service(log_output=os.devnull)` with no explicit `executable_path`.
- Added `.github/dependabot.yml` for automated weekly dependency-update PRs
  (`pip` and `github-actions` ecosystems). There was previously no automated
  mechanism to surface outdated or vulnerable dependencies.
- Added a `pip-audit` step to both `daily_scraping.yml` and
  `biweekly_check_gaps.yml`, right after installing the project. The job
  fails (and the existing failure-email notification fires) if a known CVE
  is found in a resolved dependency, instead of silently scraping with
  vulnerable packages.
- Added explicit least-privilege `permissions: contents: read` to both
  workflows. Neither workflow actually needs a *write*-scoped
  `GITHUB_TOKEN`: pushes to `main` and the `scraped` submodule authenticate
  via `secrets.PAT_TOKEN` (set on the checkout step), not the default
  Actions token, so the default token only needs read access.

### Changed

- **Breaking: minimum Python version raised from 3.12 to 3.13**
  (`requires-python = ">=3.13"`). CI (`daily_scraping.yml`,
  `biweekly_check_gaps.yml`) and `mypy`'s `python_version` were updated to
  3.13 to match; installing this package on Python 3.12 will now fail
  `pip`'s `Requires-Python` check.
- Modernized type hints across the whole `scraper` package to Python
  3.12+ syntax: `typing.List/Dict/Tuple/Optional/Union` → builtin
  `list`/`dict`/`tuple`/`X | None`, and `typing.Generator` →
  `collections.abc.Generator`. No behavior change; verified with `ruff`,
  `ruff format --check`, and `mypy` across the full package.
- `scraper/utils/mtgo.py::scrape_tournament` and
  `scraper/utils/selenium_driver.py::get_mtgo_tournaments` now use Selenium's
  `WebDriverWait` with an explicit `expected_conditions.presence_of_element_located`
  condition instead of a blind `time.sleep()`. This returns as soon as the
  page has rendered instead of always waiting the full guessed duration, and
  raises the wait timeout on retry (instead of guessing a longer sleep) so
  transient slow renders resolve without needlessly delaying already-fast
  pages.
- `biweekly_check_gaps.yml` no longer has its own `schedule` trigger. It is
  now invoked as a reusable workflow (`workflow_call`) from
  `daily_scraping.yml` once the daily scrape-and-commit job finishes, but
  only on Sundays (`trigger-biweekly-gaps` job, gated on a day-of-week check).
  This makes the two runs strictly sequential instead of relying on both
  being scheduled at the same time. `workflow_dispatch` is still available
  for ad-hoc manual runs of the biweekly scripts.
- Both workflows still share the same `concurrency.group:
  mtg-scraper-pipeline` as defense in depth (e.g. a manual biweekly dispatch
  overlapping with a scheduled daily run), and both now `git pull --rebase`
  before pushing to the `scraped` submodule, matching the rebase-before-push
  already used for the `main` push.

## [0.1.0] - 2025

### Added

- Initial multithreaded scraper for MTGO and MTGTop8 tournament decklists.
- CLI entry point (`scrape` / `python -m scraper`) with `--source`,
  `--date-from`, `--date-to`, `--force-mtgo`, and `--span` options.
  Standardized JSON output under `scraped/`.
- Daily and biweekly GitHub Actions workflows to run the scraper on a
  schedule and commit results to the `scraped` data submodule.

[Unreleased]: https://github.com/barrins-project/mtg_scraper/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/barrins-project/mtg_scraper/releases/tag/v0.2.0
[0.1.0]: https://github.com/barrins-project/mtg_scraper/releases/tag/v0.1.0
