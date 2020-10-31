# -*- coding: utf-8 -*-
"""Update the IP addresses of your DNSPod DNS records."""
from datetime import datetime, timedelta
import logging
from typing import Dict

import voluptuous as vol
import requests

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import track_time_interval
from homeassistant.const import (CONF_API_KEY, CONF_EMAIL, HTTP_OK)
from .const import (
    CONF_RECORDS,
    CONF_DOMAINS,
    CONF_DOMAIN_NAME,
    CONF_LINKSYS,
    CONF_EXTERNAL_URLS,
    CONF_IP_GETTER,
    DATA_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    SERVICE_UPDATE_RECORDS,
    DNSPOD_ID_URL,
    DNSPOD_UPDATE_URL
)
from .ip_getter import get_ip

_LOGGER = logging.getLogger(__name__)

DOMAIN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DOMAIN_NAME): cv.string,
        vol.Required(CONF_RECORDS): vol.All(cv.ensure_list, [cv.string]),
    })

IP_GETTER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_LINKSYS): cv.string,
        vol.Optional(CONF_EXTERNAL_URLS): vol.All(cv.ensure_list, [cv.url])
    })


CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_IP_GETTER): IP_GETTER_SCHEMA,
        vol.Required(CONF_DOMAINS): vol.All(cv.ensure_list, [DOMAIN_SCHEMA]),
    }),
}, extra=vol.ALLOW_EXTRA)

_DP_IP_POOL = {}
MAX_IP_TIMEDELTA = timedelta(minutes=DEFAULT_UPDATE_INTERVAL*10)


def _ip_need_update(ip):
    now = datetime.now()
    need_update = not (
        ip in _DP_IP_POOL
        and _DP_IP_POOL[ip] - now < MAX_IP_TIMEDELTA)
    _DP_IP_POOL[ip] = now
    return need_update


def get_record_ids(domain, sdns, data_params, header):
    result = []
    resp = requests.post(
        DNSPOD_ID_URL, data=data_params, headers=header)
    records = resp.json().get('records', {})
    for item in records:
        sd_name = item.get('name')
        if sd_name in sdns:
            result.append((sd_name, item.get('id')))
            _ip_need_update(item.get('value'))
            sdns.remove(sd_name)
            _LOGGER.debug(
                "get record_id: %s for sub_domain %s" % (
                    item.get('id'), sd_name))
    if sdns:
        _LOGGER.warning(f'Could not find sub_domain {",".join(sdns)}, Please check configuration')
    return result


def get_update_params(data_params_template, domains, header):
    update_url_params = []
    data_params = data_params_template.copy()
    for item in domains:
        domain_name = item[CONF_DOMAIN_NAME]
        records = item[CONF_RECORDS]
        data_params['domain'] = domain_name
        record_infos = get_record_ids(
            domain_name, records, data_params, header)
        for (record, rid) in record_infos:
            data_params['sub_domain'] = record
            data_params['record_id'] = rid
            update_url_params.append(data_params.copy())
    return update_url_params


def setup(hass: HomeAssistant, config: Dict) -> bool:
    """Set up the component."""
    conf = config.get(DOMAIN, None)
    if not conf:
        return False
    header = {
        'User-Agent': 'Client/0.0.1 ({})'.format(
            conf[CONF_EMAIL])}
    token = conf[CONF_API_KEY]
    data_params_template = {
        'login_token': token,
        'format': 'json',
        'record_line': '默认'
    }
    update_url_params = get_update_params(
        data_params_template, conf[CONF_DOMAINS], header)
    _LOGGER.debug(update_url_params)

    def update_records_interval(now):
        """Set up recurring update."""
        update_dnspod(update_url_params, header,
                      conf.get(CONF_IP_GETTER, None))

    def update_records_service(now):
        """Set up service for manual trigger."""
        update_dnspod(update_url_params, header,
                      conf.get(CONF_IP_GETTER, None))

    update_interval = timedelta(minutes=DEFAULT_UPDATE_INTERVAL)
    track_time_interval(hass, update_records_interval, update_interval)

    hass.services.register(DOMAIN, "update_records", update_records_service)
    return True


def update_dnspod(params, header, ip_getter=None):
    _LOGGER.debug("Trying to get ip")
    current_ip = get_ip(ip_getter)
    if not current_ip:
        logging.error('get current ip FAILED.')
        return

    if not _ip_need_update(current_ip):
        return

    # new ip found
    logging.info("new ip found: %s", current_ip)
    for param in params:
        r = requests.post(
            DNSPOD_UPDATE_URL, data=param, headers=header)
        if not r.status_code == HTTP_OK:
            logging.error("update ip failed: %s", r.text)
        logging.info("update ip: %s", r.text)
