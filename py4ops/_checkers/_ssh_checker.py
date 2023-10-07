import socket

from ._ip_checker import is_valid_ip_address

def check_ssh(server_ip: str, port=22, timeout=None) -> bool:
    """Function to check if a port is open on a server."""
    
    if not is_valid_ip_address(server_ip):
        raise TypeError(f"{server_ip} is not valid ipv4/ipv6 address.")
    
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout:
            test_socket.settimeout(timeout)
        test_socket.connect((server_ip, port))    
    except Exception as e:
        # print(e)
        return False
    finally:
        test_socket.close()
    return True