"""Public Streamlit landing page for FishStop desktop installers."""

from __future__ import annotations

from html import escape
from base64 import b64encode
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
import streamlit as st
import streamlit.components.v1 as components

from landing_content import COPY, ITALIAN_LEGAL


DESKTOP_REPOSITORY = "EugenioDeRosa/fishstop-desktop-email-security"
RELEASES_URL = f"https://github.com/{DESKTOP_REPOSITORY}/releases"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{DESKTOP_REPOSITORY}/releases/latest"
SITE_URL = "https://fishstop-eml.streamlit.app/"
PRIVACY_URL = f"{SITE_URL}?page=privacy"
TERMS_URL = f"{SITE_URL}?page=terms"
SUPPORT_EMAIL = "info.fishstop@gmail.com"
PLATFORM_LOGOS = {
    name: "data:image/svg+xml;base64," + b64encode(
        (Path(__file__).parent / "assets" / f"{name}.svg").read_bytes()
    ).decode("ascii")
    for name in ("apple", "windows", "flag-uk", "flag-it", "sun", "moon", "fishstop-mail-check")
}
BRAND_MARKUP = f"<img class='brand-mark' src='{PLATFORM_LOGOS['fishstop-mail-check']}' alt='' aria-hidden='true'><span class='fish'>fish<span class='stop'>stop</span></span>"


def page_url(page: str = "home") -> str:
    params = {"lang": st.session_state.site_language, "theme": st.session_state.site_theme}
    if page != "home":
        params["page"] = page
    return "?" + urlencode(params)


def save_preferences() -> None:
    st.query_params["lang"] = st.session_state.site_language
    st.query_params["theme"] = st.session_state.site_theme


def change_language() -> None:
    st.session_state.site_language = "en" if st.session_state.site_language == "it" else "it"
    save_preferences()


def change_theme() -> None:
    st.session_state.site_theme = "light" if st.session_state.site_theme == "dark" else "dark"
    save_preferences()


def render_page_behavior() -> None:
    # A changed srcdoc reruns the lifecycle after each preference update.
    revision = f"{st.session_state.site_language}:{st.session_state.site_theme}"
    script = (Path(__file__).parent / "assets" / "landing-scroll.js").read_text(encoding="utf-8")
    components.html(f"<script>/* {revision} */" + script + "</script>", height=0)


def t(key: str) -> str:
    return COPY[st.session_state.site_language][key]


def render_legal_page(page: str) -> None:
    is_privacy = page == "privacy"
    title = t(f"{page}_title")
    eyebrow = t(f"{page}_eyebrow")
    intro = t(f"{page}_intro")
    if is_privacy:
        body = f"""
        <section class="legal-section"><h2>1. Who is responsible</h2><p>FishStop is a desktop email-security project maintained by Eugenio De Rosa. Privacy questions can be sent to <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>.</p></section>
        <section class="legal-section"><h2>2. Information FishStop accesses</h2><p>Current public builds use a local guest workspace and do not sign in to Google/Microsoft or connect inboxes: those controls are disabled. The display name chosen for the dashboard stays on the device and can be changed in Settings. Guest history and preferences persist locally; anyone using the same OS session can reopen that workspace. The currently disabled OAuth code provides the following behaviour if enabled in future versions. Signing in with Google or Microsoft provides the account identifier, name, email address and, when available, profile picture needed to create the local workspace. Connecting Gmail or Outlook is a separate, optional authorization.</p><p>For Gmail, FishStop requests the read-only <code>gmail.readonly</code> permission. It lists metadata and previews for up to ten recent Inbox messages. The complete MIME email is retrieved only after the user explicitly selects <strong>Analyse</strong>. FishStop cannot send, delete, move or modify mailbox messages.</p></section>
        <aside class="local-boundary"><span>LOCAL PROCESSING BOUNDARY</span><strong>Email bodies, attachments and AI analysis remain on the user's device.</strong><p>FishStop does not operate a remote analysis server and does not use Google user data to train shared AI models or for advertising.</p></aside>
        <section class="legal-section"><h2>3. How information is used</h2><p>Email data is used only to perform the security analysis requested by the user: parsing message structure and authentication headers, examining links and attachments, detecting identity inconsistencies, and producing a local risk assessment.</p><p>FishStop's use and transfer to any other app of information received from Google APIs adheres to the <a href="https://developers.google.com/terms/api-services-user-data-policy" target="_blank" rel="noopener">Google API Services User Data Policy</a>, including the Limited Use requirements.</p></section>
        <section class="legal-section"><h2>4. Storage and retention</h2><p>VirusTotal results may be cached locally for one hour with persistent quota counters. The cache can include indicator metadata; expired entries are removed on subsequent use. The mailbox refresh token is stored in the operating system's secure credential store. Analysis history and preferences are stored on the user's device and separated by account. A selected email may be written to a temporary local file while it is analysed and is removed when that processing step finishes.</p><p>FishStop does not maintain a central copy of mailbox messages or analysis history.</p></section>
        <section class="legal-section"><h2>5. External services and indicators</h2><p>If the user configures third-party reputation services, FishStop may submit technical indicators such as URLs, domains, IP addresses or file hashes to services such as VirusTotal or AbuseIPDB. The complete email, its body and attachments are not submitted by FishStop to those services. Their own privacy policies apply.</p><p>AlienVault OTX receives indicators such as URLs, sender domains and file hashes for online lookups; results may be cached locally. Spamhaus ZEN and IP geolocation are off by default and independently opt-in. When enabled, Spamhaus receives an IP-derived DNS query. Local only disables external analysis lookups, including DNS/RDAP and online brand checks; sign-in, mailbox retrieval, model downloads and app updates remain separate online actions. IP geolocation (ipwho.is), DNS/RDAP, Wikidata and crt.sh may receive an IP address, domain or brand name. URLs can contain personal identifiers or tokens; technical indicators are not necessarily anonymous. Wikidata receives extracted brand/organization names and entity queries; RDAP services receive domains, and the configured DNS resolver receives DNS names such as DKIM selectors. The crt.sh and organizational-site redirect helpers exist in the code but have no callers in the audited active path. Model installation contacts Hugging Face and its storage/CDN; updates and GPU-runtime downloads contact GitHub and its release infrastructure. Automatic update checks are enabled by default, run at startup and hourly when the app is available, and can be disabled in Settings. Manual checks remain available; installation requires confirmation. These downloads do not transmit emails. These services also receive connection metadata, such as the requesting IP address, but not the complete message.</p></section>
        <section class="legal-section"><h2>6. Sharing and sale</h2><p>FishStop does not sell Google user data, mailbox content or analysis history. It does not share that information for advertising, credit decisions or user profiling. Information is disclosed only when initiated by an optional user-configured reputation lookup, required by law, or necessary to protect users and the integrity of the software.</p></section>
        <section class="legal-section"><h2>7. User controls and deletion</h2><p>The user can select <strong>Disconnect</strong> in FishStop to remove the locally stored mailbox authorization, clear local analysis history from the application, revoke FishStop from the Google Account permissions page, or uninstall the application to remove its installed components. Sign out does not erase history; uninstallation may leave user-data folders. Clearing history does not delete original EML files, exported reports, backups or separate caches. Because FishStop has no central mailbox database, support cannot remotely erase files that exist only on the user's device.</p></section>
        <section class="legal-section"><h2>8. Security and changes</h2><p>FishStop uses OAuth Authorization Code with PKCE, loopback callbacks and the operating system credential store. No system can guarantee absolute security. The download website is hosted by Streamlit and retrieves release information from GitHub. Visiting the website involves connection metadata processed by those hosting providers under their own privacy policies; the website does not upload or analyse email files. Full technical data-flow documentation is available in the <a href="https://github.com/{DESKTOP_REPOSITORY}/blob/dev/docs/privacy-data-flows.md" target="_blank" rel="noopener">source repository</a>. This policy may be updated when features or legal requirements change; the revision date below will be updated accordingly.</p></section>
        """
    else:
        body = f"""
        <section class="legal-section"><h2>1. Software license and services</h2><p>FishStop is free and open-source software under <a href="https://github.com/{DESKTOP_REPOSITORY}/blob/dev/LICENSE" target="_blank" rel="noopener">GPL-3.0-or-later</a>, copyright © 2026 Eugenio De Rosa. You may use, study, modify and redistribute it, including commercially, under that license. Covered derivative versions that you distribute must preserve those freedoms and provide corresponding source to recipients. See the <a href="https://github.com/{DESKTOP_REPOSITORY}" target="_blank" rel="noopener">source repository</a> and the source archive accompanying each new release. These terms describe account connections and external services; they do not replace or restrict GPL rights. The <a href="{PRIVACY_URL}">Privacy Policy</a> explains data handling. Third-party components retain their own licenses.</p></section>
        <section class="legal-section"><h2>2. Purpose of the service</h2><p>FishStop is a defensive email-analysis application designed to help users inspect suspicious messages, links, attachments and authentication evidence. It provides decision support and does not guarantee that every malicious email will be detected or that every warning represents an actual attack.</p></section>
        <aside class="local-boundary"><span>USER-CONTROLLED ANALYSIS</span><strong>The user chooses which email is analysed and remains responsible for the final decision.</strong><p>Do not open, execute, reply to or pay based solely on an automated result when material risk is involved.</p></aside>
        <section class="legal-section"><h2>3. Account and mailbox access</h2><p>The user may connect only accounts they own or are authorized to access. Gmail and Outlook connections are read-only. The user is responsible for protecting their device and account and for revoking access if the device is lost or shared.</p></section>
        <section class="legal-section"><h2>4. Acceptable use</h2><p>Users remain responsible for complying with applicable law, privacy rights and authorization requirements for accounts and data. This is not an additional restriction on the software license. No trademark rights or permission to present a fork as an official FishStop release are granted; truthful attribution remains allowed.</p></section>
        <section class="legal-section"><h2>5. Third-party services</h2><p>Google, Microsoft, GitHub, VirusTotal, AbuseIPDB, AlienVault OTX and other optional sources operate under their own terms. The GPL does not license access to their APIs or data. VirusTotal Public prohibits commercial products/services and business workflows that do not contribute new files. Free OTX and public Spamhaus services have non-commercial/fair-use conditions; AbuseIPDB and ipwho.is have plan limits and data-reuse conditions. A personal key does not override those terms. Check each provider’s current terms and obtain an appropriate plan or authorization. FishStop does not control their availability, results or policies. An unavailable provider may limit a feature without affecting local analysis.</p></section>
        <section class="legal-section"><h2>6. Availability and updates</h2><p>FishStop is a desktop email-security application. Features may change, be suspended or be discontinued. Updates may be necessary for compatibility, security or provider-policy changes.</p></section>
        <section class="legal-section"><h2>7. Disclaimer and liability</h2><p>To the maximum extent permitted by applicable law, FishStop is provided without warranties of uninterrupted availability, complete detection or fitness for a specific purpose. The maintainer is not liable for decisions, payments, data loss or security incidents caused by relying exclusively on an automated assessment.</p></section>
        <section class="legal-section"><h2>8. Contact and changes</h2><p>Questions may be sent to <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>. Updates to this page do not revoke GPL rights already granted for released software; the license of a released copy remains applicable.</p></section>
        """
    if st.session_state.site_language == "it":
        body = ITALIAN_LEGAL[page].format(support=SUPPORT_EMAIL, privacy=page_url("privacy"))
    else:
        body = body.replace(PRIVACY_URL, page_url("privacy"))
    st.markdown(
        f"""
        <nav class="nav legal-nav"><a class="wordmark" href="{page_url()}">{BRAND_MARKUP}</a><div><a href="{page_url('privacy')}" class="{'active' if is_privacy else ''}">Privacy</a><a href="{page_url('terms')}" class="{'active' if not is_privacy else ''}">{t('terms')}</a></div></nav>
        <main class="legal-shell"><header class="legal-hero"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{intro}</p><small>{t('updated')}</small></header>{body}</main>
        <footer class="legal-footer"><span>FishStop · {t('security')}</span><a href="{page_url()}">{t('back')}</a></footer>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=900, show_spinner=False)
def latest_release() -> dict[str, Any] | None:
    try:
        response = requests.get(LATEST_RELEASE_URL, headers={"Accept": "application/vnd.github+json"}, timeout=8)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def installer_for(release: dict[str, Any] | None, platform: str, architecture: str | None = None) -> dict[str, Any] | None:
    if not release:
        return None
    extensions = (".dmg",) if platform == "macos" else (".msi", ".exe")
    candidates = [asset for asset in release.get("assets", []) if str(asset.get("name", "")).lower().endswith(extensions)]
    if platform != "macos" or architecture is None:
        return candidates[0] if candidates else None
    markers = ("aarch64", "arm64") if architecture == "apple-silicon" else ("x86_64", "x64", "intel")
    matching = next((asset for asset in candidates if any(marker in str(asset.get("name", "")).lower() for marker in markers)), None)
    return matching


def download_card(icon: str, platform: str, title: str, description: str, asset: dict[str, Any] | None, version: str | None) -> None:
    st.markdown(
        f"<div class='download-card-head'><span class='platform-icon'><img class='{icon}-logo' src='{PLATFORM_LOGOS[icon]}' alt='' aria-hidden='true'></span><p class='platform-label'>{escape(platform)}</p></div>"
        f"<h2>{escape(title)}</h2><p class='platform-copy'>{escape(description)}</p>",
        unsafe_allow_html=True,
    )
    if asset:
        st.link_button(t("installer"), asset["browser_download_url"], use_container_width=True)
        st.caption(f"{version} · {asset['name']}")
    else:
        st.link_button(t("releases"), RELEASES_URL, use_container_width=True)
        st.caption(t("pending"))


st.set_page_config(page_title="FishStop — Download", page_icon="◒", layout="wide", initial_sidebar_state="collapsed")

for key, parameter, choices, default in (
    ("site_language", "lang", ("en", "it"), "en"),
    ("site_theme", "theme", ("light", "dark"), "light"),
):
    if key not in st.session_state:
        value = str(st.query_params.get(parameter, default)).lower()
        st.session_state[key] = value if value in choices else default

st.markdown(
    """
    <style>
      :root { --ink:#0b1220; --muted:#64748b; --line:#e5eaf1; --canvas:#f7f9fc; --blue:#2563eb; --teal:#0f9f8f; --aqua:#dff8f3; }
      html,body,[class*="css"] { font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Inter",sans-serif; }
      .stApp { background:var(--canvas); color:var(--ink); } [data-testid="stHeader"] { height:0; background:transparent; }
      #MainMenu,footer,[data-testid="stToolbar"] { display:none; }
      [data-testid="stMainBlockContainer"] { max-width:1180px; padding:1.35rem 1.5rem 3rem; }
      .nav { display:flex; align-items:center; justify-content:space-between; min-height:3rem; margin-bottom:clamp(4.5rem,10vw,8.5rem); }
      .wordmark { margin:0; font-size:1.17rem; letter-spacing:-.065em; font-weight:760; } .fish { color:var(--ink); } .stop { color:var(--teal); }
      .nav-note { margin:0; color:#8a98ab; font-size:.75rem; font-weight:650; letter-spacing:.1em; text-transform:uppercase; }
      .hero { position:relative; isolation:isolate; max-width:930px; padding-bottom:5.7rem; }
      .hero::before { content:""; position:absolute; z-index:-1; width:600px; height:430px; left:-230px; top:-220px; border-radius:50%; background:radial-gradient(circle,rgba(37,99,235,.14),rgba(15,159,143,.07) 41%,transparent 72%); filter:blur(8px); pointer-events:none; }
      .eyebrow { display:inline-flex; align-items:center; gap:.5rem; margin:0 0 1.25rem; color:var(--teal); font-size:.73rem; font-weight:760; letter-spacing:.13em; text-transform:uppercase; }
      .eyebrow::before { content:""; width:.48rem; height:.48rem; border-radius:999px; background:var(--teal); box-shadow:0 0 0 5px rgba(15,159,143,.11); }
      .hero h1 { max-width:880px; margin:0; color:var(--ink); font-size:clamp(3.55rem,8.1vw,7.3rem)!important; font-weight:720; line-height:.93; letter-spacing:-.078em; }
      .hero h1 em { color:var(--teal); font-style:normal; } .hero-copy { max-width:630px; margin:1.7rem 0 0; color:var(--muted); font-size:1.15rem; line-height:1.65; letter-spacing:-.012em; }
      .download-section { border-top:1px solid var(--line); padding-top:2.15rem; } .download-kicker { margin:0 0 .45rem; color:var(--blue); font-size:.73rem; font-weight:760; letter-spacing:.13em; text-transform:uppercase; }
      .download-section h3 { margin:0; color:var(--ink); font-size:clamp(2rem,4vw,3rem); line-height:1; letter-spacing:-.062em; } .release-status { margin:.85rem 0 1.8rem; color:var(--muted); font-size:.9rem; } .release-status strong { color:var(--ink); font-weight:700; }
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-height:278px; padding:1.45rem; border:1px solid var(--line); border-radius:22px; background:rgba(255,255,255,.84); box-shadow:0 2px 5px rgba(15,23,42,.018),0 14px 32px rgba(15,23,42,.035); transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:hover { transform:translateY(-4px); border-color:#cdd8e7; box-shadow:0 20px 42px rgba(15,23,42,.08); }
      .download-card-head { display:flex; align-items:center; gap:.72rem; } .platform-icon { display:grid; place-items:center; width:2.1rem; height:2.1rem; border-radius:10px; background:linear-gradient(145deg,#eff6ff,var(--aqua)); color:var(--teal); font-size:1.12rem; }
      .platform-label { margin:0; color:#75839a; font-size:.72rem; font-weight:740; letter-spacing:.08em; text-transform:uppercase; } h2 { margin:1.25rem 0 .52rem!important; color:var(--ink); font-size:1.45rem!important; letter-spacing:-.045em; }
      .platform-copy { min-height:3rem; margin:0 0 1.3rem; color:var(--muted); font-size:.91rem; line-height:1.55; }
      [data-testid="stLinkButton"] a { min-height:2.85rem; border:0; border-radius:999px; background:var(--ink); color:white; font-size:.88rem; font-weight:700; transition:transform .18s ease,background .18s ease; }
      [data-testid="stLinkButton"] a:hover { background:var(--teal); color:white; transform:scale(1.012); } [data-testid="stCaptionContainer"] { color:#8a98ab; font-size:.7rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
      .trust-row { display:grid; grid-template-columns:repeat(3,1fr); gap:1.3rem; margin-top:5rem; padding-top:1.65rem; border-top:1px solid var(--line); }.trust-item { color:var(--muted); font-size:.87rem; line-height:1.55; }.trust-item strong { display:block; margin-bottom:.34rem; color:var(--ink); font-size:.92rem; letter-spacing:-.018em; }
      .footer-line { display:flex; justify-content:space-between; gap:1rem; margin-top:4.5rem; color:#8a98ab; font-size:.75rem; }.footer-line a { color:var(--teal); text-decoration:none; }
      .footer-links { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:1rem; }
      .legal-nav { margin-bottom:clamp(3.5rem,7vw,6rem); }.legal-nav a { text-decoration:none; }.legal-nav>div { display:flex; gap:.35rem; }.legal-nav>div a { padding:.48rem .72rem; border-radius:999px; color:var(--muted); font-size:.78rem; font-weight:690; }.legal-nav>div a:hover,.legal-nav>div a.active { color:var(--ink); background:white; box-shadow:inset 0 0 0 1px var(--line); }
      .legal-shell { width:min(760px,100%); margin:0 auto; }.legal-hero { margin-bottom:3.6rem; padding-bottom:2.3rem; border-bottom:1px solid var(--line); }.legal-hero h1 { margin:0; color:var(--ink); font-size:clamp(3rem,7vw,5.4rem)!important; line-height:.93; letter-spacing:-.075em; }.legal-hero>p:not(.eyebrow) { max-width:620px; margin:1.35rem 0 .8rem; color:var(--muted); font-size:1.08rem; line-height:1.65; }.legal-hero small { color:#8a98ab; font-size:.76rem; }
      .legal-section { margin:0 0 2.6rem; }.legal-section h2 { margin:0 0 .75rem!important; color:var(--ink); font-size:1.18rem!important; letter-spacing:-.028em; }.legal-section p { margin:.55rem 0; color:var(--muted); font-size:.94rem; line-height:1.75; }.legal-section a,.legal-footer a { color:var(--teal); text-underline-offset:3px; }.legal-section code { padding:.14rem .34rem; border-radius:5px; color:#0b6f66; background:#e7f5f1; font-size:.82rem; }
      .local-boundary { position:relative; margin:3.3rem 0; padding:1.55rem 1.65rem 1.45rem; overflow:hidden; border:1px solid #cde8e1; border-radius:20px; background:linear-gradient(145deg,#eefaf6,#fff); }.local-boundary::after { content:""; position:absolute; width:130px; height:130px; right:-55px; top:-62px; border:24px solid rgba(15,159,143,.07); border-radius:50%; }.local-boundary span,.local-boundary strong,.local-boundary p { position:relative; z-index:1; display:block; }.local-boundary span { color:var(--teal); font-size:.67rem; font-weight:800; letter-spacing:.13em; }.local-boundary strong { max-width:570px; margin:.65rem 0; color:var(--ink); font-size:1.12rem; line-height:1.4; }.local-boundary p { max-width:600px; margin:0; color:var(--muted); font-size:.86rem; line-height:1.6; }
      .legal-footer { width:min(760px,100%); display:flex; justify-content:space-between; gap:1rem; margin:4rem auto 0; padding-top:1.5rem; border-top:1px solid var(--line); color:#8a98ab; font-size:.76rem; }.legal-footer a { text-decoration:none; font-weight:700; }
      @media(max-width:760px) { [data-testid="stMainBlockContainer"] { padding:1.1rem 1.1rem 2rem; }.nav { margin-bottom:4rem; }.nav-note { display:none; }.hero { padding-bottom:4rem; }.hero h1 { font-size:clamp(3.1rem,16vw,4.5rem)!important; }.hero-copy { font-size:1.02rem; }.trust-row { grid-template-columns:1fr; gap:1.15rem; margin-top:3.7rem; }.footer-line,.legal-footer { flex-direction:column; margin-top:3.4rem; }.footer-links { justify-content:flex-start; }.legal-nav { align-items:flex-start; gap:1rem; margin-bottom:3.6rem; }.legal-hero { margin-bottom:2.6rem; }.local-boundary { margin:2.7rem 0; padding:1.3rem; } [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-height:auto; margin-bottom:.85rem; } }
      @media(prefers-reduced-motion:reduce) { * { transition:none!important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

dark = st.session_state.site_theme == "dark"
st.markdown(
    """<style>
    :root { --apple-logo-filter:none; }
    :root { --surface:#ffffff; --button-text:#ffffff; --icon-start:#eff6ff; --hover-line:#cdd8e7; --subtle:#64748b; --code-bg:#e7f5f1; --code-ink:#0b6f66; --boundary-start:#eefaf6; --boundary-line:#cde8e1; color-scheme:light; }
    .st-key-downloads [data-testid="stColumn"] { background:var(--surface); }
    .st-key-downloads [data-testid="stColumn"]:hover { border-color:var(--hover-line); }
    .st-key-preferences [data-testid="stColumn"] { min-height:0; padding:0; border:0; border-radius:0; background:transparent; box-shadow:none; }
    .st-key-preferences [data-testid="stColumn"]:hover { transform:none; box-shadow:none; }
    .st-key-preferences { max-width:380px; margin-left:auto; margin-bottom:1rem; }
    .st-key-preferences label, .st-key-preferences label p { color:var(--muted); }
    [data-baseweb="select"]>div, [data-baseweb="popover"], [data-baseweb="popover"] ul { background:var(--surface); color:var(--ink); border-color:var(--line); }
    [data-baseweb="select"] svg { fill:var(--ink); }
    .st-key-preferences [data-testid="stSelectbox"] [role="group"],
    .st-key-preferences [role="combobox"], .st-key-preferences [data-testid="stSelectbox"] button { background:var(--surface); color:var(--ink); border-color:var(--line); }
    [role="listbox"] { background:var(--surface); color:var(--ink); }
    [role="option"] { color:var(--ink); background:var(--surface); }
    [role="option"]:hover, [role="option"][aria-selected="true"] { background:var(--aqua); }
    .platform-icon { background:linear-gradient(145deg,var(--icon-start),var(--aqua)); }
    .platform-icon img { width:1.2rem; height:1.2rem; object-fit:contain; }
    .platform-icon .apple-logo { filter:var(--apple-logo-filter,none); }
    [data-testid="stLinkButton"] a { color:var(--button-text); }
    [data-testid="stLinkButton"] a:hover { color:var(--button-text); }
    .nav-note,.platform-label,.footer-line,.legal-hero small,.legal-footer,[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:var(--subtle); }
    .legal-nav>div a:hover,.legal-nav>div a.active { background:var(--surface); }
    .legal-section code { background:var(--code-bg); color:var(--code-ink); }
    .local-boundary { border-color:var(--boundary-line); background:linear-gradient(145deg,var(--boundary-start),var(--surface)); }
    .st-key-preferences [data-baseweb="select"]>div:focus-within { outline:2px solid var(--teal); outline-offset:2px; }
    @media(max-width:760px) { .st-key-preferences { max-width:none; } .st-key-preferences [data-testid="stHorizontalBlock"] { flex-wrap:nowrap; } .st-key-preferences [data-testid="stColumn"] { min-width:0; flex:1 1 0; } }
    </style>""",
    unsafe_allow_html=True,
)

st.markdown("""<style>
    [data-testid="stElementContainer"]:has(style) { display:none; }
    .st-key-preferences { position:fixed; top:1rem; right:max(1.1rem,calc((100vw - 1132px)/2)); width:220px; z-index:100; margin:0; padding:.65rem .8rem; border:1px solid var(--line); border-radius:999px; background:var(--surface); box-shadow:0 6px 24px #00000012; }
    .st-key-preferences [data-testid="stHorizontalBlock"] { flex-wrap:nowrap; gap:.7rem; }
    .st-key-preferences [data-testid="stColumn"] { min-width:0; flex:1 1 0; margin:0; }
    .st-key-preferences label { gap:.35rem; }
    .st-key-preferences label p { font-size:.85rem; white-space:nowrap; }
    .st-key-preferences [role="switch"] { transition:background .25s ease,transform .25s ease; }
    .nav { padding-right:235px; }
    .nav-note { display:none; }
    [data-testid="stElementContainer"]:has(iframe[title="streamlit.components.v1.html"]) { position:fixed; bottom:0; width:0; height:0; overflow:hidden; pointer-events:none; }
    @media(max-width:760px) { .st-key-preferences { width:204px; top:.65rem; right:.7rem; } .nav { padding-right:210px; } }
    </style>""", unsafe_allow_html=True)

minimal_style = (Path(__file__).parent / "assets" / "minimal.css").read_text(encoding="utf-8")
st.markdown("<style>" + minimal_style + "</style>", unsafe_allow_html=True)
# Keep the same element tree in both themes so Streamlit reconciles in place.
theme_tokens = (
    "--ink:#f5f5f7; --muted:#a1a1a6; --canvas:#101012; --surface:#1c1c1e; --line:#333336; --teal:#54d8c1; --blue:#54d8c1; --apple-logo-filter:invert(1); --button-text:#0b1220; --icon-start:#1b2e49; --hover-line:#536a87; --subtle:#a1b0c6; --code-bg:#173d3a; --code-ink:#8aebd5; --boundary-start:#102c2a; --boundary-line:#28514b; color-scheme:dark;"
    if dark else "color-scheme:light;"
)
st.markdown("<style>:root {" + theme_tokens + "}</style>", unsafe_allow_html=True)

st.markdown(f"""<style>
    .st-key-preferences button {{ position:relative; width:60px; min-height:34px; padding:0; border:0; border-radius:999px; background:var(--line); cursor:pointer; }}
    .st-key-preferences button p {{ position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); }}
    .st-key-preferences button::before {{ content:""; position:absolute; left:3px; top:4px; width:26px; height:26px; border-radius:50%; background:white; box-shadow:0 2px 5px #0002; transition:transform .28s ease; pointer-events:none; }}
    .st-key-preferences button::after {{ content:""; position:absolute; left:7px; top:8px; width:18px; height:18px; background:center/contain no-repeat; transition:transform .28s ease; pointer-events:none; }}
    .st-key-preferences button[aria-label="Italiano"],.st-key-preferences button[aria-label="English"] {{ background:var(--line); }}
    .st-key-language_switch button::before,.st-key-language_switch button::after {{ transform:translateX({'28px' if st.session_state.site_language == 'it' else '0'}); }}
    .st-key-theme_switch button::before,.st-key-theme_switch button::after {{ transform:translateX({'28px' if dark else '0'}); }}
    .st-key-language_switch button::after {{ background-image:url('{PLATFORM_LOGOS['flag-it' if st.session_state.site_language == 'it' else 'flag-uk']}'); }}
    .st-key-theme_switch button::after {{ background-image:url('{PLATFORM_LOGOS['moon' if dark else 'sun']}'); }}
    .st-key-preferences button:focus-visible {{ outline:2px solid var(--teal); outline-offset:3px; }}
    </style>""", unsafe_allow_html=True)

with st.container(key="preferences"):
    language_control, theme_control = st.columns(2, gap="small")
    with language_control:
        with st.container(key="language_switch"):
            st.button("Italiano",
                      key="language_button", on_click=change_language)
    with theme_control:
        with st.container(key="theme_switch"):
            st.button("Dark mode", key="theme_button", on_click=change_theme)

requested_page = str(st.query_params.get("page", "home")).strip().lower()
if requested_page in {"privacy", "terms"}:
    render_legal_page(requested_page)
    render_page_behavior()
    st.stop()

st.markdown(
    """<style>
    [data-testid="stMain"], [data-testid="stAppViewContainer"]>.main {
        scroll-snap-type:y mandatory; scroll-behavior:smooth;
    }
    .st-key-overview_panel,.st-key-download_panel {
        min-height:calc(100dvh - 3rem); scroll-snap-align:start; scroll-snap-stop:always;
        display:flex; flex-direction:column; justify-content:center;
    }
    .st-key-overview_panel .nav { margin-bottom:clamp(2rem,6vh,5rem); }
    .st-key-overview_panel .hero { padding-bottom:2rem; }
    .st-key-download_panel .trust-row { margin-top:1.6rem; padding-top:1.2rem; }
    .st-key-download_panel .footer-line { margin-top:1.5rem; }
    @media(max-width:760px) {
        [data-testid="stMain"], [data-testid="stAppViewContainer"]>.main { scroll-snap-type:y proximity; }
    }
    @media(prefers-reduced-motion:reduce) {
        [data-testid="stMain"], [data-testid="stAppViewContainer"]>.main { scroll-behavior:auto; scroll-snap-type:none; }
    }
    </style>""", unsafe_allow_html=True,
)

with st.container(key="overview_panel"):
    st.markdown(
        f"""
        <nav class="nav"><p class="wordmark">{BRAND_MARKUP}</p><p class="nav-note">{t('nav')}</p></nav>
        <section class="hero" id="overview"><p class="eyebrow">{t('eyebrow')}</p><h1>{t('hero')}</h1><p class="hero-copy">{t('intro')}</p></section>
        """,
        unsafe_allow_html=True,
    )


with st.container(key="download_panel"):
    st.markdown(f'<section class="download-section" id="download"><p class="download-kicker">{t("edition")}</p><h3>{t("download")}</h3></section>', unsafe_allow_html=True)
    release = latest_release()
    version = (release.get("name") or release.get("tag_name")) if release else None
    if release:
        st.markdown(f"<p class='release-status'>{t('latest')} <strong>{escape(str(version))}</strong></p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='release-status'>{t('coming')}</p>", unsafe_allow_html=True)

    with st.container(key="downloads"):
        mac_arm, mac_intel, windows = st.columns(3, gap="medium")
    with mac_arm:
        download_card("apple", "macOS · Apple Silicon", t("mac_arm"), t("mac_arm_copy"), installer_for(release, "macos", "apple-silicon"), version)
    with mac_intel:
        download_card("apple", "macOS · Intel", t("mac_intel"), t("mac_intel_copy"), installer_for(release, "macos", "intel"), version)
    with windows:
        download_card("windows", "Windows · 64 bit", t("windows"), t("windows_copy"), installer_for(release, "windows"), version)


    st.markdown(
        f"""<section class="trust-row" id="features"><div class="trust-item"><strong>{t('private')}</strong>{t('private_copy')}</div><div class="trust-item"><strong>{t('ready')}</strong>{t('ready_copy')}</div><div class="trust-item"><strong>{t('triage')}</strong>{t('triage_copy')}</div></section>""",
        unsafe_allow_html=True,
    )
    with st.container(key="site_footer"):
        st.markdown(
            f"""<div class="footer-line"><span>FishStop · {t('security')}</span><span class="footer-links"><a href="{page_url('privacy')}">Privacy</a><a href="{page_url('terms')}">{t('terms')}</a><a href="mailto:{SUPPORT_EMAIL}">{t('support')}</a><a href="https://github.com/{DESKTOP_REPOSITORY}" target="_blank" rel="noopener">GPLv3 · {"Sorgenti" if st.session_state.site_language == "it" else "Source code"}</a><a href="{RELEASES_URL}" target="_blank" rel="noopener">{t('all_releases')}</a></span></div>""",
            unsafe_allow_html=True,
        )

render_page_behavior()
