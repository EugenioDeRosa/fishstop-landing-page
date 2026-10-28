# FishStop Landing Page

The public download website for the FishStop desktop email-security application,
built with Streamlit. This repository contains the landing page only.

## Features

- Installer downloads for macOS Apple Silicon, macOS Intel and Windows.
- Automatic installer links from the latest public release of
  [the desktop application](https://github.com/EugenioDeRosa/fishstop-desktop-email-security/releases).
- English by default, with an Italian language option.
- Light and dark themes, with light as the default. The switches apply instantly in
  the browser (one crossfade where view transitions are supported); the rerun that
  follows only records the preference, so the page never repaints mid-switch.
- Language and theme preferences preserved in the URL and internal page links.
- Smooth scroll snapping between two sections: overview and downloads, with
  features and footer included in the download section.
- Phone layout hides the hero description and shows the three installers in a
  horizontal carousel with snapping on each card. Vertical section snapping is
  preserved. Scrolling stays within tall download sections until their top is reached;
  language and theme changes preserve the reading position.
- Public Privacy Policy and Terms of Service pages in both languages.

## Run locally

Requires Python 3.11 or later.

```sh
python -m venv .venv
```

Activate the environment (`.venv\Scripts\Activate.ps1` on Windows, or
`source .venv/bin/activate` on macOS/Linux), then run:

```sh
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open http://localhost:8501. No API keys or mailbox credentials are required.
If GitHub is unavailable or no installer has been published, the page links to
the releases page instead.

## Pages and preferences

- Home: `/`
- Privacy Policy: `/?page=privacy`
- Terms of Service: `/?page=terms`

The controls set `lang=en|it` and `theme=light|dark`. For example,
`/?lang=it&theme=dark&page=privacy` opens the Italian Privacy Policy in dark mode.
A fresh URL without preferences uses English and the light theme. Scroll
snapping applies only to the home page and is disabled for reduced-motion users.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

The tests cover preferences, legal-page navigation, translations and installer
selection using mocked GitHub responses.

## Deployment

For Streamlit Community Cloud, select the repository, the `main` branch and
`streamlit_app.py` as the entry point. Runtime dependencies are in
`requirements.txt`; visual settings are in `.streamlit/config.toml`.

The public site is [fishstop-eml.streamlit.app](https://fishstop-eml.streamlit.app/).
If the repository is renamed, verify its connection in Streamlit Cloud and
reconnect it if necessary. The public URL does not need to change.

To run with Docker:

```sh
docker build -t fishstop-landing-page .
docker run --rm -p 8501:8501 fishstop-landing-page
```

The scheduled GitHub Actions workflow visits the public landing page every four
hours to wake a sleeping Streamlit app. Its separate browser dependency is
installed by the workflow and is not needed to run the site.

## Repository layout

- `streamlit_app.py`: page rendering, downloads, preferences and legal routes.
- `landing_content.py`: English/Italian copy and Italian legal content.
- `tests/`: landing-page tests.
- `.streamlit/`: Streamlit appearance and server configuration.
- `scripts/keep_streamlit_awake.py`: public-site availability check.
- `.github/workflows/`: scheduled availability workflow.
- `Dockerfile` and `.devcontainer/`: optional development and deployment setup.

The desktop application is maintained in its own repository. Email analysis,
model training and datasets are not part of this website.

## Licenza e codice sorgente

Copyright (C) 2026 Eugenio De Rosa. Il codice originale di questo repository è
distribuito sotto **GPL-3.0-or-later**: puoi usarlo, modificarlo e ridistribuirlo,
anche commercialmente, rispettando la [licenza](LICENSE). Le versioni derivate
coperte dalla GPL che distribuisci devono mantenere le stesse libertà e rendere
disponibile ai destinatari il sorgente corrispondente. Non viene fornita alcuna
garanzia, nei limiti consentiti dalla legge.

Le dipendenze e gli asset di terze parti mantengono le proprie licenze.
Nome e logo non concedono diritti sui marchi o il permesso di presentare un fork
come release ufficiale. Le condizioni delle API esterne restano indipendenti
dalla licenza del software; una chiave personale non autorizza ogni tipo di uso.

Sorgenti desktop: https://github.com/EugenioDeRosa/fishstop-desktop-email-security
