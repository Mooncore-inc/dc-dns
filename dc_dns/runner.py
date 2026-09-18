import asyncio

import dns.asyncresolver
import dns.exception

from demon_cry_base.runner import BaseEntity, PluginResult

from dc_dns.models import DnsLookupConfig, DnsLookupParams


class DnsLookupEntity(BaseEntity):
    qtype: str
    value: str


def _make_resolver(config: DnsLookupConfig) -> dns.asyncresolver.Resolver:
    resolver = dns.asyncresolver.Resolver(configure=False)
    resolver.nameservers = config.dns_servers
    resolver.timeout = config.timeout
    resolver.lifetime = config.timeout
    return resolver


async def _query(
    resolver: dns.asyncresolver.Resolver, domain: str, qtype: str
) -> list[DnsLookupEntity]:
    try:
        answer = await resolver.resolve(domain, qtype)
    except dns.exception.DNSException:
        return []
    return [DnsLookupEntity(qtype=qtype, value=r.to_text()) for r in answer]


async def run(config: DnsLookupConfig, params: DnsLookupParams) -> PluginResult:
    domain = params.domain.strip().lower().rstrip(".")
    resolver = _make_resolver(config)
    results = await asyncio.gather(
        *(_query(resolver, domain, qtype) for qtype in params.record_type)
    )
    return PluginResult(
        status="ok", entities=[e for records in results for e in records]
    )
