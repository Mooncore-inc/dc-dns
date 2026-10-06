import asyncio

import dns.asyncresolver
import dns.exception
import dns.resolver

from demon_cry_base.runner import BaseEntity, ErrorEntity, PluginResult

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


def _error_for(domain: str, qtype: str, exc: Exception) -> ErrorEntity:
    details = {"domain": domain, "qtype": qtype}
    if isinstance(exc, dns.resolver.NXDOMAIN):
        return ErrorEntity(
            code="NXDOMAIN",
            message=f"Domain {domain} does not exist",
            details=details,
        )
    if isinstance(exc, dns.resolver.NoAnswer):
        return ErrorEntity(
            code="NO_ANSWER",
            message=f"No {qtype} records for {domain}",
            details=details,
        )
    if isinstance(exc, dns.exception.Timeout):
        return ErrorEntity(
            code="TIMEOUT",
            message=f"DNS query timed out for {domain} ({qtype})",
            details=details,
        )
    if isinstance(exc, dns.resolver.NoNameservers):
        return ErrorEntity(
            code="NO_NAMESERVERS",
            message=f"No nameservers available for {domain} ({qtype})",
            details=details,
        )
    return ErrorEntity(
        code="DNS_ERROR",
        message=str(exc) or "DNS query failed",
        details=details,
    )


async def _query(
    resolver: dns.asyncresolver.Resolver, domain: str, qtype: str
) -> tuple[list[DnsLookupEntity], ErrorEntity | None]:
    try:
        answer = await resolver.resolve(domain, qtype)
    except dns.exception.DNSException as exc:
        return [], _error_for(domain, qtype, exc)
    return [DnsLookupEntity(qtype=qtype, value=r.to_text()) for r in answer], None


async def run(config: DnsLookupConfig, params: DnsLookupParams) -> PluginResult:
    domain = params.domain.strip().lower().rstrip(".")
    resolver = _make_resolver(config)
    results = await asyncio.gather(
        *(_query(resolver, domain, qtype) for qtype in params.record_type)
    )
    entities = [entity for records, _ in results for entity in records]
    errors = [error for _, error in results if error is not None]
    return PluginResult.build(entities=entities, errors=errors)
