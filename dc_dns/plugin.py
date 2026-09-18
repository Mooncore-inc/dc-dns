from demon_cry_base.plugin import BasePlugin
from dc_dns.models import DnsLookupConfig, DnsLookupParams


class DnsLookup(BasePlugin):
    name = "dns_lookup"
    description = "finds DNS records"
    category = "network"
    config_model = DnsLookupConfig
    parameters_model = DnsLookupParams
    execute_func = "dc_dns.runner:run"
