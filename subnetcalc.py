#!/usr/bin/env python3
"""Subnet Calculator CLI Tool."""

import argparse
import ipaddress
import os
import sys

# Subnet Calculation
def calculate_subnet(cidr_input):
    """Calculate all subnet details from a CIDR string."""

    # Creates a network object from the CIDR string ensuring users can type host addresses with no errors using the strict=False flag
    network = ipaddress.ip_network(cidr_input, strict=False)

    # Returns all usuable host addresses (excluding the network & broadcast addresses)
    hosts_list = list(network.hosts())
    num_hosts = len(hosts_list)

    # Grabs the first & last address in the list for the usuable range
    if num_hosts > 0:
        first_host = str(hosts_list[0])
        last_host = str(hosts_list[-1])
    else:
        first_host = "N/A"
        last_host = "N/A"

    return {
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "subnet_mask": str(network.netmask),
        "wildcard_mask": str(network.hostmask),
        "prefix_length": network.prefixlen,
        "first_host": first_host,
        "last_host": last_host,
        "usable_hosts": num_hosts,
        "total_addresses": network.num_addresses,
    }

def get_binary_breakdown(cidr_input):
    """Generate binary representation showing network vs host bits."""
    network = ipaddress.ip_network(cidr_input, strict=False)
    prefix_len = network.prefixlen

    addr_int = int(network.network_address)

    # Converts the IP address integer into a 32-character binary string (padded with leading zeros)
    binary_str = format(addr_int, "032b")

    # Slices that 32-bit string into four 8-bit octets for display
    octets = [binary_str[i:i + 8] for i in range(0, 32, 8)]

    return {
        "binary_octets": octets,
        "prefix_length": prefix_len,

        # Split the bits into network portion based on the prefix length
        "network_bits": binary_str[:prefix_len],

        # # Split the bits into host portion based on the prefix length
        "host_bits": binary_str[prefix_len:],
    }

# Set-up a CLI entry point
def main():
    # Creates a parser with a description that appears in --help output argument below
    parser = argparse.ArgumentParser(
        description="Subnet Calculator - Compute network details from IP/CIDR notation"
    )
    # Defines a required positional argument
    parser.add_argument(
        "network",
        help="IP address in CIDR notation (e.g., 192.168.1.0/24)"
    )
    args = parser.parse_args()
    print(args.network)

# Ensures main() only runs if the file is executed directly
if __name__ == "__main__":
    main()