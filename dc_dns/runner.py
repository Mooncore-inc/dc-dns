import asyncio
from typing import Any

import aiodns

from demon_cry_base.runner import BaseEntity, PluginResult

from dc_dns.models import DnsLookupParams, DnsLookupConfig

RECORD_FIELDS = {
    "A": ["addr"],
    "AAAA": ["addr"],
    "MX": ["priority", "exchange"],
    "NS": ["nsdname"],
    "TXT": ["data"],
    "CNAME": ["cname"],
    "SOA": ["mname", "rname", "serial", "refresh", "retry", "expire", "minimum"],
    "PTR": ["dname"],
}


class DnsLookupEntity(BaseEntity):
    qtype: str
    value: str


def _format_record(qtype: str, record: Any) -> DnsLookupEntity | None:
    values = []
    for field in RECORD_FIELDS.get(qtype, []):
        value = str(getattr(record.data, field, "")).strip()
        if value:
            values.append(value)
    if not values:
        return None
    return DnsLookupEntity(qtype=qtype, value=", ".join(values))


async def _query(
    resolver: aiodns.DNSResolver, domain: str, qtype: str
) -> list[DnsLookupEntity]:
    try:
        result = await resolver.query_dns(host=domain, qtype=qtype)
    except Exception:
        return []
    return [
        entity
        for rec in (result.answer or [])
        if (entity := _format_record(qtype, rec)) is not None
    ]


async def run(config: DnsLookupConfig, params: DnsLookupParams) -> PluginResult:
    domain = params.domain.strip().lower().rstrip(".")
    resolver = aiodns.DNSResolver(nameservers=config.dns_servers)
    results = await asyncio.gather(
        *(_query(resolver, domain, qtype) for qtype in params.record_type)
    )
    return PluginResult(
        status="ok", entities=[e for records in results for e in records]
    )
