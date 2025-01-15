"""Constants for DNSPod."""
import re

DOMAIN = "dnspod"

# Config
CONF_RECORDS = "records"
CONF_DOMAINS = "domains"
CONF_DOMAIN_NAME = "name"
CONF_IP_GETTER = "ip_getter"
CONF_LINKSYS = "linksys"
CONF_EXTERNAL_URLS = "external_urls"
CONF_API_TOKEN = "api_token"

# Data
DATA_UPDATE_INTERVAL = "update_interval"

# Defaults
DEFAULT_UPDATE_INTERVAL = 3  # in minutes

# Services
SERVICE_UPDATE_RECORDS = "update_records"

# DNS Service URL
DNSPOD_SERVICE_BASE_URL = "dnsapi.cn/Record"

# DNS INFO Service URL
DNSPOD_ID_URL = "https://{}.List".format(DNSPOD_SERVICE_BASE_URL)

# DNS UPDATE Service URL
DNSPOD_UPDATE_URL = "https://{}.Ddns".format(DNSPOD_SERVICE_BASE_URL)

DEFAULT_EXTERNAL_URLS = [
    "http://myip.ipip.net/",
    "http://www.httpbin.org/ip",
    "http://54.236.246.173/ip",
    "http://3.220.112.94/ip",
]

IP_REGEX = re.compile(
    r"\D*("
    + r"(?:1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\."
    + r"(?:1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\."
    + r"(?:1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\."
    + r"(?:1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)"
    + r")\D*"
)
