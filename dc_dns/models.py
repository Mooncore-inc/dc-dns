from typing import Literal
from demon_cry_base import PluginParameters
from pydantic import Field


RecordType = Literal["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]


class DnsLookupParams(PluginParameters):
    domain: str = Field(description="Domain to lookup")
    record_type: list[RecordType] = Field(
        default=["A"], description='Record types to query (e.g. ["A", "MX", "NS"])'
    )