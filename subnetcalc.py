import ipaddress

# Quick test to confirm the ipaddress module works
network = ipaddress.ip_network('192.168.1.0/24', strict=False)
print(f"Network: {network.network_address}")
print(f"Broadcast: {network.broadcast_address}")
print(f"Netmask: {network.netmask}")
print(f"Hostmask: {network.hostmask}")