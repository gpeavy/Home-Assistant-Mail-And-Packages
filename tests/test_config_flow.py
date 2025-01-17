""" Test Mail and Packages config flow """

import logging
from unittest.mock import patch

import pytest
from homeassistant import config_entries, setup
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mail_and_packages.config_flow import _validate_user_input
from custom_components.mail_and_packages.const import (
    CONF_AMAZON_FWDS,
    CONF_GENERATE_MP4,
    CONF_IMAP_TIMEOUT,
    CONF_SCAN_INTERVAL,
    CONF_STORAGE,
    DOMAIN,
)
from custom_components.mail_and_packages.helpers import _check_ffmpeg, _test_login
from tests.const import FAKE_CONFIG_DATA, FAKE_CONFIG_DATA_BAD

_LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,step_id_5,input_5,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": True,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email,amazon@example.com,fake@email%$^&@example.com,bogusemail@testamazon.com",
            },
            "config_3",
            {
                "custom_img_file": "images/test.gif",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email,amazon@example.com,fake@email%$^&@example.com,bogusemail@testamazon.com",
                "custom_img": True,
                "custom_img_file": "images/test.gif",
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    step_id_5,
    input_5,
    title,
    data,
    hass,
    mock_imap,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.config_flow.path",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_5
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_5
        )

    assert result["type"] == "create_entry"
    assert result["title"] == title
    assert result["data"] == data

    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,step_id_5,input_5,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": True,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "(none)",
            },
            "config_3",
            {
                "custom_img_file": "images/test.gif",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": [],
                "custom_img": True,
                "custom_img_file": "images/test.gif",
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_no_fwds(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    step_id_5,
    input_5,
    title,
    data,
    hass,
    mock_imap,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.config_flow.path",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_5
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_5
        )

    assert result["type"] == "create_entry"
    assert result["title"] == title
    assert result["data"] == data

    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": True,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email",
            },
            "config_3",
            {
                "custom_img_file": "images/test.gif",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": ["fakeuser@test.email", "fakeuser2@test.email"],
                "custom_img": True,
                "custom_img_file": "images/test.gif",
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_invalid_custom_img_path(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass,
    mock_imap,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

    assert result["type"] == "form"
    assert result["step_id"] == step_id_4
    assert result["errors"] == {"custom_img_file": "file_not_found"}


@pytest.mark.parametrize(
    "input_1,step_id_2",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "user",
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_connection_error(input_1, step_id_2, hass, mock_imap):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login",
        return_value=False,
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result2["type"] == "form"
        assert result2["step_id"] == step_id_2
        assert result2["errors"] == {"base": "communication"}


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "folder": '"INBOX"',
                "generate_mp4": True,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "(none)",
            },
            "imap.test.email",
            {
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": [],
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_invalid_ffmpeg(
    input_1, step_id_2, input_2, step_id_3, input_3, title, data, hass, mock_imap
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=False,
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result2["type"] == "form"
        assert result2["step_id"] == step_id_2

        result3 = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

    assert result3["type"] == "form"
    assert result3["step_id"] == step_id_2
    assert result3["errors"] == {CONF_GENERATE_MP4: "ffmpeg_not_found"}


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "(none)",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "custom_img": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": [],
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_index_error(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass,
    mock_imap_index_error,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "os.path.exists", return_value=True
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

    assert "error" not in result
    assert result["type"] == "create_entry"
    assert result["title"] == title
    assert result["data"] == data

    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "(none)",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": [],
                "custom_img": False,
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_index_error_2(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass,
    mock_imap_index_error_2,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "os.path.exists", return_value=True
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

    assert result["type"] == "create_entry"
    assert result["title"] == title
    assert result["data"] == data

    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "(none)",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "custom_img": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": [],
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_mailbox_format2(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass,
    mock_imap_mailbox_format2,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "os.path.exists", return_value=True
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

    assert result["type"] == "create_entry"
    assert result["title"] == title
    assert result["data"] == data

    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "(none)",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "custom_img": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": [],
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_mailbox_format3(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass,
    mock_imap_mailbox_format3,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "os.path.exists", return_value=True
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

    assert result["type"] == "create_entry"
    assert result["title"] == title
    assert result["data"] == data

    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.asyncio
async def test_valid_ffmpeg(test_valid_ffmpeg):
    result = await _check_ffmpeg()
    assert result


@pytest.mark.asyncio
async def test_invalid_ffmpeg(test_invalid_ffmpeg):
    result = await _check_ffmpeg()
    assert not result


@pytest.mark.asyncio
async def test_imap_login(mock_imap):
    result = await _test_login(
        "127.0.0.1", 993, "fakeuser@test.email", "suchfakemuchpassword", "SSL", False
    )
    assert result


@pytest.mark.asyncio
async def test_imap_connection_error(caplog):
    await _test_login(
        "127.0.0.1", 993, "fakeuser@test.email", "suchfakemuchpassword", "SSL", False
    )
    assert "Error connecting into IMAP Server:" in caplog.text


@pytest.mark.asyncio
async def test_imap_login_error(mock_imap_login_error, caplog):
    await _test_login(
        "127.0.0.1", 993, "fakeuser@test.email", "suchfakemuchpassword", "SSL", True
    )
    assert "Error logging into IMAP Server:" in caplog.text


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "testemail@amazon.com",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_amazon_error(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    mock_imap,
    hass,
    caplog,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "os.path.exists", return_value=True
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )
        assert result["type"] == "create_entry"
        assert (
            "Amazon domain found in email: testemail@amazon.com, this may cause errors when searching emails."
            in caplog.text
        )


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "@bademail.com, amazon.com",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_amazon_error_2(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    mock_imap,
    hass,
    caplog,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        assert "Missing '@' in email address: amazon.com" in caplog.text
        assert result["errors"] == {CONF_AMAZON_FWDS: "invalid_email_format"}


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "config_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "config_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email,amazon@example.com,fake@email%$^&@example.com,bogusemail@testamazon.com",
            },
            "config_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email,amazon@example.com,fake@email%$^&@example.com,bogusemail@testamazon.com",
                "custom_img": True,
                "custom_img_file": "images/test.gif",
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_security": "SSL",
                "imap_timeout": 30,
                "scan_interval": 20,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_form_storage_error(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass,
    mock_imap,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "custom_components.mail_and_packages.config_flow._test_login", return_value=True
    ), patch(
        "custom_components.mail_and_packages.config_flow._check_ffmpeg",
        return_value=True,
    ), patch(
        "custom_components.mail_and_packages.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.mail_and_packages.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

    assert result["type"] == "form"
    assert result["step_id"] == step_id_4
    assert result["errors"] == {CONF_STORAGE: "path_not_found"}


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,step_id_5,input_5,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "reconfig_2",
            {
                "allow_external": False,
                "custom_img": True,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 120,
                "scan_interval": 60,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "reconfig_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email",
            },
            "reconfig_3",
            {
                "custom_img_file": "images/test.gif",
            },
            "reconfig_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email",
                "custom_img": True,
                "custom_img_file": "images/test.gif",
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "image_name": "mail_today.gif",
                "image_path": "custom_components/mail_and_packages/images/",
                "image_security": True,
                "imap_security": "SSL",
                "imap_timeout": 120,
                "scan_interval": 60,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_delivered",
                    "amazon_packages",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                    "mail_updated",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_reconfigure(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    step_id_5,
    input_5,
    title,
    data,
    hass: HomeAssistant,
    integration,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    mock_update,
) -> None:
    """Test reconfigure flow."""
    entry = integration

    with patch(
        "custom_components.mail_and_packages.config_flow.path",
        return_value=True,
    ):

        reconfigure_result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        assert reconfigure_result["type"] is FlowResultType.FORM
        assert reconfigure_result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            input_1,
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_5
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_5
        )
        # assert "errors" not in result

        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        await hass.async_block_till_done()

        _LOGGER.debug("Entries: %s", len(hass.config_entries.async_entries(DOMAIN)))
        entry = hass.config_entries.async_entries(DOMAIN)[0]
        assert entry.data.copy() == data


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "reconfig_2",
            {
                "allow_external": False,
                "custom_img": True,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 120,
                "scan_interval": 60,
                "resources": [
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "reconfig_3",
            {
                "custom_img_file": "images/test.gif",
            },
            "reconfig_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": "fakeuser@fake.email, fakeuser2@fake.email",
                "custom_img": True,
                "custom_img_file": "images/test.gif",
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "image_name": "mail_today.gif",
                "image_path": "custom_components/mail_and_packages/images/",
                "image_security": True,
                "imap_security": "SSL",
                "imap_timeout": 120,
                "scan_interval": 60,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                    "mail_updated",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_reconfigure_no_amazon(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass: HomeAssistant,
    integration,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    mock_update,
) -> None:
    """Test reconfigure flow."""
    entry = integration

    with patch(
        "custom_components.mail_and_packages.config_flow.path",
        return_value=True,
    ):

        reconfigure_result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        assert reconfigure_result["type"] is FlowResultType.FORM
        assert reconfigure_result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            input_1,
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        await hass.async_block_till_done()

        _LOGGER.debug("Entries: %s", len(hass.config_entries.async_entries(DOMAIN)))
        entry = hass.config_entries.async_entries(DOMAIN)[0]
        assert entry.data.copy() == data


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "reconfig_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 120,
                "scan_interval": 60,
                "resources": [
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "reconfig_storage",
            {
                "storage": ".storage/mail_and_packages/images",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": "fakeuser@fake.email, fakeuser2@fake.email",
                "custom_img": False,
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "image_name": "mail_today.gif",
                "image_path": "custom_components/mail_and_packages/images/",
                "image_security": True,
                "imap_security": "SSL",
                "imap_timeout": 120,
                "scan_interval": 60,
                "storage": ".storage/mail_and_packages/images",
                "resources": [
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                    "mail_updated",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_reconfigure_no_amazon_no_custom_image(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    title,
    data,
    hass: HomeAssistant,
    integration,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    mock_update,
) -> None:
    """Test reconfigure flow."""
    entry = integration

    with patch(
        "custom_components.mail_and_packages.config_flow.path",
        return_value=True,
    ):

        reconfigure_result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        assert reconfigure_result["type"] is FlowResultType.FORM
        assert reconfigure_result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            input_1,
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        await hass.async_block_till_done()

        _LOGGER.debug("Entries: %s", len(hass.config_entries.async_entries(DOMAIN)))
        entry = hass.config_entries.async_entries(DOMAIN)[0]
        assert entry.data.copy() == data


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,step_id_4,input_4,title,data",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "reconfig_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 120,
                "scan_interval": 60,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "reconfig_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email",
            },
            "reconfig_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
            "imap.test.email",
            {
                "allow_external": False,
                "amazon_days": 3,
                "amazon_domain": "amazon.com",
                "amazon_fwds": "fakeuser@test.email,fakeuser2@test.email",
                "custom_img": False,
                "host": "imap.test.email",
                "port": 993,
                "username": "test@test.email",
                "password": "notarealpassword",
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "image_name": "mail_today.gif",
                "image_path": "custom_components/mail_and_packages/images/",
                "image_security": True,
                "imap_security": "SSL",
                "imap_timeout": 120,
                "scan_interval": 60,
                "storage": "custom_components/mail_and_packages/images/",
                "resources": [
                    "amazon_delivered",
                    "amazon_packages",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                    "mail_updated",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                ],
                "verify_ssl": False,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_reconfig_no_cust_img(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    step_id_4,
    input_4,
    title,
    data,
    hass: HomeAssistant,
    integration,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    mock_update,
) -> None:
    """Test reconfigure flow."""
    entry = integration

    with patch(
        "custom_components.mail_and_packages.config_flow.path",
        return_value=True,
    ):

        reconfigure_result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        assert reconfigure_result["type"] is FlowResultType.FORM
        assert reconfigure_result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            input_1,
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_4
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_4
        )

        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        await hass.async_block_till_done()

        _LOGGER.debug("Entries: %s", len(hass.config_entries.async_entries(DOMAIN)))
        entry = hass.config_entries.async_entries(DOMAIN)[0]
        assert entry.data.copy() == data


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "reconfig_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 120,
                "scan_interval": 60,
                "resources": [
                    "amazon_packages",
                    "fedex_delivered",
                    "fedex_delivering",
                    "fedex_packages",
                    "mail_updated",
                    "ups_delivered",
                    "ups_delivering",
                    "ups_packages",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                    "dhl_delivered",
                    "dhl_delivering",
                    "dhl_packages",
                    "amazon_delivered",
                    "auspost_delivered",
                    "auspost_delivering",
                    "auspost_packages",
                    "poczta_polska_delivering",
                    "poczta_polska_packages",
                    "inpost_pl_delivered",
                    "inpost_pl_delivering",
                    "inpost_pl_packages",
                ],
            },
            "reconfig_amazon",
            {
                "amazon_domain": "amazon.com",
                "amazon_days": 3,
                "amazon_fwds": "amazon.com",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_reconfig_amazon_error(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    hass: HomeAssistant,
    integration,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    mock_update,
    caplog,
) -> None:
    """Test reconfigure flow."""
    entry = integration

    with patch(
        "custom_components.mail_and_packages.config_flow.path",
        return_value=True,
    ):

        reconfigure_result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        assert reconfigure_result["type"] is FlowResultType.FORM
        assert reconfigure_result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            input_1,
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == step_id_3
        assert "Missing '@' in email address: amazon.com" in caplog.text
        assert result["errors"] == {CONF_AMAZON_FWDS: "invalid_email_format"}


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3",
    [
        (
            {
                "host": "imap.test.email",
                "port": "993",
                "username": "test@test.email",
                "password": "notarealpassword",
                "imap_security": "SSL",
                "verify_ssl": False,
            },
            "reconfig_2",
            {
                "allow_external": False,
                "custom_img": False,
                "folder": '"INBOX"',
                "generate_mp4": False,
                "gif_duration": 5,
                "imap_timeout": 30,
                "scan_interval": 20,
                "resources": [
                    "mail_updated",
                    "usps_delivered",
                    "usps_delivering",
                    "usps_mail",
                    "usps_packages",
                    "zpackages_delivered",
                    "zpackages_transit",
                ],
            },
            "reconfig_storage",
            {
                "storage": "custom_components/mail_and_packages/images/",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_reconfig_storage_error(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    hass: HomeAssistant,
    integration,
    mock_imap_no_email,
):
    """Test we get the form."""
    entry = integration

    reconfigure_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"],
        input_1,
    )
    assert result["type"] == "form"
    assert result["step_id"] == step_id_2

    result = await hass.config_entries.flow.async_configure(result["flow_id"], input_2)

    assert result["type"] == "form"
    assert result["step_id"] == step_id_3

    with patch(
        "custom_components.mail_and_packages.config_flow._validate_user_input",
        return_value=({CONF_STORAGE: "path_not_found"}, input_3),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

    assert result["type"] == "form"
    assert result["step_id"] == step_id_3
    assert result["errors"] == {CONF_STORAGE: "path_not_found"}
