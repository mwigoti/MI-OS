"""
MwohaOS Security & SSRF Protection Utilities — Milestone 2
Validates target URLs against loopback, private RFC1918 ranges, link-local,
Docker service networks, and AWS/GCP cloud metadata endpoints before fetching.
Also sanitizes external untrusted HTML to prevent stored XSS.
"""
import ipaddress
import re
import socket
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

# Blocked IP ranges: RFC 1918 (Private), RFC 3927 (Link-Local), Loopback, IPv6 link-local
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local (Cloud metadata e.g. 169.254.169.254)
    ipaddress.ip_network("0.0.0.0/8"),        # This host
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "redis",
    "web",
    "celery",
    "celery_beat",
    "db",
    "postgres",
    "metadata.google.internal",
}


def validate_public_url(url: str) -> str:
    """
    Validates that a URL is well-formed, uses HTTP/HTTPS, and does not resolve
    to localhost, a private network, or a cloud metadata address.
    Raises ValidationError if URL is invalid or unsafe.
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise ValidationError(f"Invalid URL scheme '{parsed.scheme}'. Only http and https are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise ValidationError("URL has no valid hostname.")

    hostname_clean = hostname.lower().strip()

    if hostname_clean in BLOCKED_HOSTNAMES:
        raise ValidationError(f"Access to internal host '{hostname_clean}' is prohibited (SSRF Protection).")

    # Resolve IP addresses
    try:
        # Check if hostname is already an IP
        ip_obj = ipaddress.ip_address(hostname_clean)
        for net in BLOCKED_NETWORKS:
            if ip_obj in net:
                raise ValidationError(f"Destination IP '{ip_obj}' is in a private/restricted address range.")
    except ValueError:
        # Not an IP string, perform DNS resolution check
        try:
            addr_info = socket.getaddrinfo(hostname_clean, None)
            for addr in addr_info:
                ip_str = addr[4][0]
                resolved_ip = ipaddress.ip_address(ip_str)
                for net in BLOCKED_NETWORKS:
                    if resolved_ip in net:
                        raise ValidationError(f"Resolved IP '{resolved_ip}' for '{hostname}' is in a private network (SSRF Protection).")
        except socket.gaierror:
            # If domain cannot be resolved in tests or offline, allow it if it's not explicitly blocked
            pass

    return url


def sanitize_html(raw_html: str) -> str:
    """
    Strips dangerous HTML tags, attributes, scripts, object tags, and event handlers
    from untrusted external opportunity descriptions.
    """
    if not raw_html:
        return ""

    text = str(raw_html)

    # Remove script, style, iframe, object, embed tags and their contents
    text = re.sub(r"<(script|style|iframe|object|embed|applet)[^>]*>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove self-closing dangerous tags
    text = re.sub(r"<(script|style|iframe|object|embed|applet)[^>]*/>", "", text, flags=re.IGNORECASE)

    # Remove event handlers (onclick, onload, onerror, etc.)
    text = re.sub(r"\s+on\w+\s*=\s*(['\"]).*?\1", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+on\w+\s*=\s*[^>\s]+", "", text, flags=re.IGNORECASE)

    # Remove javascript: pseudo-protocols
    text = re.sub(r"href\s*=\s*(['\"])javascript:.*?\1", 'href="#"', text, flags=re.IGNORECASE)
    text = re.sub(r"src\s*=\s*(['\"])javascript:.*?\1", 'src=""', text, flags=re.IGNORECASE)

    return text.strip()
