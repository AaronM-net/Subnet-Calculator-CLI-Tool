#!/usr/bin/env python3
"""Subnet Calculator CLI Tool."""

import argparse
import ipaddress
import os
import sys

# Color Support

# Maps friendly names to ANSI escape sequences
COLORS = {
    "header": "\033[1;36m",
    "label": "\033[1;33m",
    "value": "\033[0;37m",
    "network_bits": "\033[1;32m",
    "host_bits": "\033[1;31m",
    "reset": "\033[0m",
}

# Allows display code to work with or without color
NO_COLORS = {key: "" for key in COLORS}

# Checks the following: an explicit --no-color flag, the NO_COLOR environment variable (a community convention), and whether stdout is a terminal (not a pipe)
def should_use_color(no_color_flag):
    """Determine if color output should be used."""
    if no_color_flag:
        return False
    if os.environ.get("NO_COLOR") is not None:
        return False
    if not sys.stdout.isatty():
        return False
    return True

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

def get_vlsm_table(cidr_input):
    """Generate VLSM subdivision table showing possible subnet splits."""
    # Iterates through progressively smaller subnet sizes, starting one prefix bit longer than the input network
    network = ipaddress.ip_network(cidr_input, strict=False)
    prefix_len = network.prefixlen

    subnets = []
    # Caps how far down the table goes as you never exceed /30 (which gives 2 usable hosts)
    max_prefix = min(prefix_len + 7, 31)

    for new_prefix in range(prefix_len + 1, max_prefix):

        # Calculates usable hosts while the (-2) accounts for the network address and broadcast address that every subnet reserves
        hosts_per_subnet = 2 ** (32 - new_prefix) - 2

        if hosts_per_subnet < 2:
            break

        # Tells you how many subnets of that size fit in the original network where each extra prefix bit doubles the count
        num_subnets = 2 ** (new_prefix - prefix_len)

        # The loop breaks early if hosts_per_subnet < 2, since a subnet with fewer than 2 usable hosts has no practical value for host assignment
        subnets.append({
            "prefix": f"/{new_prefix}",
            "num_subnets": num_subnets,
            "hosts_per_subnet": hosts_per_subnet,
            "subnet_mask": str(ipaddress.IPv4Network(f"0.0.0.0/{new_prefix}").netmask),
        })

    return subnets

# Display Functions
def display_results(results, binary, vlsm_table, colors):
    """The function prints a header section with all subnet details (network address, broadcast, masks, host range) using fixed-width label formatting."""
    c = colors

    print(f"\n{c['header']}{'=' * 60}")
    print(f"  SUBNET CALCULATION RESULTS")
    print(f"{'=' * 60}{c['reset']}\n")

    fields = [
        ("Network Address:", results["network_address"]),
        ("Broadcast Address:", results["broadcast_address"]),
        ("Subnet Mask:", results["subnet_mask"]),
        ("Wildcard Mask:", results["wildcard_mask"]),
        ("Prefix Length:", f"/{results['prefix_length']}"),
        ("Usable Host Range:", f"{results['first_host']} - {results['last_host']}"),
        ("Usable Hosts:", str(results["usable_hosts"])),
        ("Total Addresses:", str(results["total_addresses"])),
    ]

    for label, value in fields:
        print(f"  {c['label']}{label:<20}{c['reset']}{c['value']}{value}{c['reset']}")

    # The binary breakdown iterates bit by bit through all 32 bits. Each bit gets colored green (network bit) or red (host bit) based on whether its position is before or after the prefix length.
    print(f"\n{c['header']}{'\u2500' * 60}")
    print(f"  BINARY BREAKDOWN")
    print(f"{'\u2500' * 60}{c['reset']}\n")

    prefix_len = binary["prefix_length"]
    display_line = "  "
    bit_index = 0

    for i, octet in enumerate(binary["binary_octets"]):
        for bit in octet:
            if bit_index < prefix_len:
                display_line += f"{c['network_bits']}{bit}{c['reset']}"
            else:
                display_line += f"{c['host_bits']}{bit}{c['reset']}"
            bit_index += 1
        if i < 3:
            display_line += "."

    print(display_line)

    # Tells the reader how many bits belong to each category.
    print(f"  {c['network_bits']}N = Network bits ({prefix_len}){c['reset']}  "
          f"{c['host_bits']}H = Host bits ({32 - prefix_len}){c['reset']}")

    print()

# CLI
def main():
    parser = argparse.ArgumentParser(
        description="Subnet Calculator - Compute network details from IP/CIDR notation"
    )
    parser.add_argument(
        "network",
        help="IP address in CIDR notation (e.g., 192.168.1.0/24)"
    )

    # This flag gives users an explicit way to disable color output
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )

    args = parser.parse_args()

    # Decides whether to use the COLORS or NO_COLORS dictionary.
    use_color = should_use_color(args.no_color)
    colors = COLORS if use_color else NO_COLORS

    # This block catches invalid inputs (like not_an_ip) and prints a helpful error to stderr instead of crashing with a traceba
    try:
        results = calculate_subnet(args.network)
        binary = get_binary_breakdown(args.network)
    except ValueError as e:
        print(f"Error: Invalid network input - {e}", file=sys.stderr)
        sys.exit(1)

    # Passes an empty list for the VLSM table parameter
    display_results(results, binary, [], colors)

# Ensures main() only runs if the file is executed directly
if __name__ == "__main__":
    main()