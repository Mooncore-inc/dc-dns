import asyncio

import aiodns

from demon_cry_base.plugin import PluginConfig
from demon_cry_base.runner import BaseEntity, PluginResult

from dc_dns.models import DnsLookupParams

NAME_SERVERS = ["1.1.1.1", "8.8.8.8", "9.9.9.9", "77.88.8.8", "208.67.220.220"]

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


async def run(config: PluginConfig, params: DnsLookupParams) -> PluginResult:
    if isinstance(config, dict):
        config = PluginConfig.model_validate(config)
    elif not isinstance(config, PluginConfig):
        config = PluginConfig.model_validate(config.model_dump())

    if isinstance(params, dict):
        params = DnsLookupParams.model_validate(params)
    elif not isinstance(params, DnsLookupParams):
        params = DnsLookupParams.model_validate(params.model_dump())

    _ = config
    resolver = aiodns.DNSResolver(nameservers=NAME_SERVERS)
    types = [t.upper() for t in params.record_type]

    async def query_one(qtype: str):
        try:
            result = await resolver.query_dns(host=params.domain, qtype=qtype)
            return (qtype, result.answer if result.answer else None)
        except Exception:
            return (qtype, None)

    results = await asyncio.gather(*(query_one(t) for t in types))

    entities: list[DnsLookupEntity] = []
    for qtype, records in results:
        fields = RECORD_FIELDS.get(qtype, [])
        if not records:
            continue
        for rec in records:
            values = [str(getattr(rec.data, f, "")) for f in fields]
            entities.append(DnsLookupEntity(qtype=qtype, value=", ".join(values)))

    return PluginResult(status="ok", entities=entities)
