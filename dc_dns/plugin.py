from demon_cry_base import BasePlugin
from dc_dns.models import DnsLookupParams

class DnsLookup(BasePlugin):
    name = "dns_lookup"
    description = "finds DNS records"
    category = "network"
    parameters_model = DnsLookupParams
    execute_func = "dc_dns.runner:run"
