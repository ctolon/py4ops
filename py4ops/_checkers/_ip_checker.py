import socket
from typing import List

def is_valid_ipv4_address(address: str) -> bool:
    """Check if an IPv4 address is valid."""
    
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def is_valid_ipv6_address(address: str) -> bool:
    """Check if an IPv6 address is valid."""
    
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    
    return True

def is_all_valid_ip_addresses(addresses: List[str]) -> bool:
    """Check if all addresses in a list are valid."""
    
    return all([is_valid_ipv4_address(ip) or is_valid_ipv6_address(ip) for ip in addresses])

def is_valid_ip_address(address: str) -> bool:
    """Check if an IP address is valid."""
    
    return is_valid_ipv4_address(address) or is_valid_ipv6_address(address)