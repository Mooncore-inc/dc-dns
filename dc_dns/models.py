from typing import Literal
from demon_cry_base.plugin import PluginParameters, PluginConfig
from pydantic import Field


RecordType = Literal["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]


class DnsLookupParams(PluginParameters):
    domain: str = Field(min_length=1, max_length=253, description="Domain to lookup")
    record_type: list[RecordType] = Field(
        default=["A"],
        min_length=1,
        description='Record types to query (e.g. ["A", "MX", "NS"])',
    )


class DnsLookupConfig(PluginConfig):
    dns_servers: list[str] = Field(
        default=[
            "1.1.1.1",
            "8.8.8.8",
            "9.9.9.9",
            "77.88.8.8",
            "208.67.220.220",
        ],
        min_length=1,
        description="DNS servers to query",
    )
    timeout: float = Field(
        default=5.0, gt=0, le=60, description="DNS query timeout in seconds"
    )
