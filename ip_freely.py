#!/usr/bin/env python3

import sys
import ipaddress
import subprocess
import platform
import re

def ping_host(ip):
    """
    Pings a host once and returns:
    ("UP", response_time_ms)
    ("DOWN", "No response")
    ("ERROR", error_message)
    """

    system = platform.system().lower()

    # Windows uses -n and -w (timeout in ms)
    if system == "windows":
        command = ["ping", "-n", "1", "-w", "1000", str(ip)]
    else:
        # Linux / macOS
        command = ["ping", "-c", "1", "-W", "1", str(ip)]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Try to extract response time
            match = re.search(r'time[=<]\s?(\d+\.?\d*)', result.stdout)
            if match:
                response_time = int(float(match.group(1)))
            else:
                response_time = 0

            return ("UP", response_time)

        else:
            return ("DOWN", "No response")

    except Exception as e:
        return ("ERROR", str(e))


def main():
    if len(sys.argv) != 2:
        print("Usage: python ip_freely.py <CIDR>")
        sys.exit(1)

    cidr_input = sys.argv[1]

    try:
        network = ipaddress.ip_network(cidr_input, strict=False)
    except ValueError:
        print("Invalid CIDR notation.")
        sys.exit(1)

    print(f"\nScanning network {network}...\n")

    up_count = 0
    down_count = 0
    error_count = 0

    for host in network.hosts():
        status, info = ping_host(host)

        if status == "UP":
            print(f"{host}  - UP   ({info}ms)")
            up_count += 1

        elif status == "DOWN":
            print(f"{host}  - DOWN (No response)")
            down_count += 1

        elif status == "ERROR":
            print(f"{host}  - ERROR ({info})")
            error_count += 1

    print("\nScan complete. "
          f"Found {up_count} active hosts, "
          f"{down_count} down, "
          f"{error_count} error")


if __name__ == "__main__":
    main()