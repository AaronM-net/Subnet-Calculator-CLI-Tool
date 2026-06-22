#!/usr/bin/env python3
"""Subnet Calculator CLI Tool."""

import argparse
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