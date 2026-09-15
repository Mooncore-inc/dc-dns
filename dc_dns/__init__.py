import asyncio
from typing import Literal

import aiodns
from demon_cry_base import BasePlugin, PluginConfig, PluginParameters
from pydantic import Field

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


RecordType = Literal["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]


class DnsLookupParams(PluginParameters):
    domain: str = Field(description="Domain to lookup")
    record_type: list[RecordType] = Field(
        default=["A"], description='Record types to query (e.g. ["A", "MX", "NS"])'
    )


class DnsLookup(BasePlugin):
    name = "dns_lookup"
    description = "finds DNS records"
    category = "network"
    parameters_model = DnsLookupParams

    async def execute(self, config: PluginConfig, params: PluginParameters) -> dict:
        if not isinstance(params, DnsLookupParams):
            params = DnsLookupParams.model_validate(params.model_dump())
        resolver = aiodns.DNSResolver(nameservers=NAME_SERVERS)
        types = [t.upper() for t in params.record_type]

        async def query_one(qtype: str):
            try:
                result = await resolver.query_dns(host=params.domain, qtype=qtype)
                return (qtype, result.answer if result.answer else None)
            except Exception:
                return (qtype, None)

        results = await asyncio.gather(*(query_one(t) for t in types))

        lines = []
        for qtype, records in results:
            fields = RECORD_FIELDS.get(qtype, [])
            if records:
                for rec in records:
                    values = [str(getattr(rec.data, f, "")) for f in fields]
                    lines.append(f"| {qtype} | {', '.join(values)} |")
            else:
                lines.append(f"| {qtype} | No records |")

        table = "| Type | Value |\n|---|---|\n" + "\n".join(lines)

        return {"result": table}
