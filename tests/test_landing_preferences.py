from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from landing_content import COPY

ENTRY_POINT = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def render(params=None, release=None):
    st.cache_data.clear()
    app = AppTest.from_file(str(ENTRY_POINT), default_timeout=15)
    app.query_params.update(params or {})
    response = Mock(status_code=200 if release else 404)
    response.json.return_value = release
    with patch("requests.get", return_value=response):
        app.run()
    assert not app.exception
    return app


def markup(app):
    return "\n".join(item.value for item in app.markdown)


def test_default_is_english_and_light_and_controls_can_switch():
    app = render()
    assert app.session_state.site_language == "en"
    assert app.session_state.site_theme == "light"
    assert "Download FishStop." in markup(app)
    app.button(key="language_button").click().run()
    app.button(key="theme_button").click().run()
    assert not app.exception
    assert "Scarica FishStop." in markup(app)
    assert "--canvas:#101012" in markup(app)
    assert app.query_params["lang"] in ("it", ["it"])
    assert app.query_params["theme"] in ("dark", ["dark"])
    assert "?lang=it&theme=dark&page=privacy" in markup(app)
    app.button(key="language_button").click().run()
    app.button(key="theme_button").click().run()
    assert app.session_state.site_language == "en"
    assert app.session_state.site_theme == "light"
    assert app.query_params["lang"] in ("en", ["en"])
    assert app.query_params["theme"] in ("light", ["light"])


@pytest.mark.parametrize("page", ["home", "privacy", "terms"])
@pytest.mark.parametrize("language", ["en", "it"])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_preferences_survive_direct_navigation(page, language, theme):
    app = render({"page": page, "lang": language, "theme": theme})
    assert app.session_state.site_language == language
    assert app.session_state.site_theme == theme
    content = markup(app)
    expected = COPY[language]["download" if page == "home" else f"{page}_title"]
    assert expected in content
    assert f"?lang={language}&theme={theme}" in content
    if page != "home":
        assert content.count('class="legal-section"') == 8
        assert len(app.get("link_button")) == 0


def test_invalid_preferences_fall_back_and_downloads_keep_release_assets():
    assets = [
        {"name": "FishStop_aarch64.dmg", "browser_download_url": "https://example.test/arm.dmg"},
        {"name": "FishStop_x64.dmg", "browser_download_url": "https://example.test/intel.dmg"},
        {"name": "FishStop_x64.msi", "browser_download_url": "https://example.test/windows.msi"},
    ]
    app = render({"lang": "unknown", "theme": "unknown"}, {"tag_name": "v1.0", "assets": assets})
    assert app.session_state.site_language == "en"
    assert app.session_state.site_theme == "light"
    assert [button.url for button in app.get("link_button")] == [asset["browser_download_url"] for asset in assets]


def test_both_languages_have_the_same_copy_keys():
    assert COPY["en"].keys() == COPY["it"].keys()


@pytest.mark.parametrize("name,matching_index", [("FishStop_aarch64.dmg", 0), ("FishStop_x64.dmg", 1)])
def test_single_mac_installer_is_only_offered_for_its_architecture(name, matching_index):
    asset = {"name": name, "browser_download_url": "https://example.test/installer.dmg"}
    app = render(release={"tag_name": "v1.0", "assets": [asset]})
    buttons = app.get("link_button")
    assert buttons[matching_index].url == asset["browser_download_url"]
    assert buttons[1 - matching_index].url.endswith("/releases")


def test_mac_installer_without_architecture_is_not_assumed_compatible():
    asset = {"name": "FishStop.dmg", "browser_download_url": "https://example.test/unknown.dmg"}
    app = render(release={"tag_name": "v1.0", "assets": [asset]})
    assert all(button.url != asset["browser_download_url"] for button in app.get("link_button"))


@pytest.mark.parametrize("language", ["en", "it"])
def test_gpl_terms_do_not_replace_software_freedoms(language):
    content = markup(render({"page": "terms", "lang": language}))
    assert "GPL-3.0-or-later" in content
    assert "fishstop-desktop-email-security" in content
    assert "commercial" in content
    assert "VirusTotal Public" in content
    assert "should not connect an account or use" not in content
    assert "non deve collegare un account o usare" not in content


@pytest.mark.parametrize("language", ["en", "it"])
def test_privacy_discloses_online_indicator_lookups(language):
    content = markup(render({"page": "privacy", "lang": language}))
    assert "OTX" in content and "online" in content
    assert "Spamhaus" in content and "ipwho.is" in content
    assert "Streamlit" in content
    assert "matched locally" not in content
    assert "confrontati localmente" not in content
