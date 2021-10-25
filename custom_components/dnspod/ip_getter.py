from http import HTTPStatus
import logging
import requests
from .const import DEFAULT_EXTERNAL_URLS, IP_REGEX

_LOGGER = logging.getLogger(__name__)


def get_ip(conf):
    urls = []
    if conf:
        if "linksys" in conf:
            ip = get_ip_from_linksys_router(conf['linksys'])
            if ip:
                _LOGGER.debug(f"get external ip {ip} from linksys")
                return ip
        urls = conf.get('external_urls', [])
    urls += DEFAULT_EXTERNAL_URLS
    for url in urls:
        ip = get_ip_from_website(url)
        if ip:
            _LOGGER.debug(f"get external ip {ip} from {url}")
            return ip
    _LOGGER.warning(f"Could not get external ip, please check config")
    return None


def _make_linksys_request(url, action):
    # Weirdly enough, this doesn't seem to require authentication
    data = [
        {
            "request": {},
            "action": f"http://linksys.com/jnap/{action}"
        }
    ]
    headers = {"X-JNAP-Action": "http://linksys.com/jnap/core/Transaction"}
    return requests.post(url, timeout=3, headers=headers, json=data)


def get_ip_from_linksys_router(gw_ip):
    url = f"http://{gw_ip}/JNAP/"
    r = _make_linksys_request(url, 'router/GetWANStatus')
    if not r.status_code == HTTPStatus.OK:
        _LOGGER.error("get ip failed: %s", r.text)
        return None
    ip = r.json()\
          .get('responses', [{}])[0]\
          .get('output', {})['wanConnection']['ipAddress']
    return ip


def get_ip_from_website(url):
    try:
        r = requests.get(url=url, timeout=10)
        return IP_REGEX.match(r.text).group(1)
    except Exception as e:
        _LOGGER.warning(f"get ip from {url} FAILED, error: {str(e)}")
        return None
