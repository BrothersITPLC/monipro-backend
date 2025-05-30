import logging
import socket

from pythonping import ping

django_logger = logging.getLogger("django")


def check_reachability(is_domain: bool, target: str, timeout: int = 5) -> bool:
    """
    Check if a target is reachable.

    Args:
        is_domain (bool): If True, treat `target` as a domain name and attempt DNS resolution.
                          If False, treat `target` as an IP address and attempt to ping it using pythonping.
        target (str): The domain name or IP address to check.
        timeout (int): Timeout in seconds for DNS resolution or ping command.

    Returns:
        bool: True if the domain resolves or the IP responds to ping; False otherwise.
    """
    if is_domain:
        try:
            socket.setdefaulttimeout(timeout)
            socket.gethostbyname(target)
            return True
        except (socket.gaierror, socket.timeout) as e:
            django_logger.error(f"Failed to resolve domain '{target}': {str(e)} ")
            return False
    else:
        try:
            response = ping(target, count=1, timeout=timeout)
            return response.success()
        except Exception as e:
            django_logger.error(f"Failed to ping IP '{target}': {str(e)} ")
            return False
