# 🌐 Subnet Calculator CLI

A zero-dependency Python command-line tool that takes any IP address and prefix length and tells you everything about that network — including a color-coded binary breakdown that makes the math *visible*.

Built to reinforce CompTIA Network+ subnetting concepts through code.

---

## What Problem Does This Solve?

Subnetting trips people up because it feels abstract. You're dividing invisible address space using binary math in your head. This tool makes the invisible visible:

- **What does my subnet actually look like in binary?** → It shows you, bit by bit, with color.
- **How many usable hosts do I have?** → Calculated and displayed instantly.
- **What if I need to split this network into smaller pieces?** → The VLSM table shows every valid split.

---

## How to Run It

**No installation required.** Python's standard library handles everything (`ipaddress`, `argparse`, `json`).

```bash
# Basic usage
python subnetcalc.py 192.168.1.0/24

# Export results to JSON
python subnetcalc.py 10.0.0.0/8 --export results.json

# Disable color (useful when piping output to a file)
python subnetcalc.py 172.16.0.0/12 --no-color
```

---

## What the Output Looks Like

Running `python subnetcalc.py 192.168.1.0/24` gives you three sections:

### 1. Subnet Summary
All the key facts about your network in one place:

```
  Network Address:    192.168.1.0
  Broadcast Address:  192.168.1.255
  Subnet Mask:        255.255.255.0
  Wildcard Mask:      0.0.0.255
  Prefix Length:      /24
  Usable Host Range:  192.168.1.1 - 192.168.1.254
  Usable Hosts:       254
  Total Addresses:    256
```

### 2. Binary Breakdown
This is where the concept clicks. Each of the 32 bits is shown individually. **Green bits** are network bits (locked — they identify the network). **Red bits** are host bits (free — they identify individual devices).

```
  11000000.10101000.00000001.00000000
  N = Network bits (24)   H = Host bits (8)
```

A `/24` means the first 24 bits are green and the last 8 are red — giving you 2⁸ = 256 total addresses (254 usable after reserving the network and broadcast addresses).

### 3. VLSM Subdivision Table
Shows how your network can be split into progressively smaller subnets:

```
  Prefix     Subnets     Hosts/Subnet    Mask
  ──────────────────────────────────────────────
  /25        2           126             255.255.255.128
  /26        4           62              255.255.255.192
  /27        8           30              255.255.255.224
  /28        16          14              255.255.255.240
  /29        32          6               255.255.255.248
  /30        64          2               255.255.255.252
```

Each row borrows one more bit from the host side, doubling the subnet count and halving the host count. That's the core trade-off in all of subnetting.

---

## Flags

| Flag | What it does |
|---|---|
| `--export FILE` | Dumps all results to a `.json` file |
| `--no-color` | Disables ANSI color codes (auto-disabled when piping) |

---

## How Color Degrades Gracefully

Color is automatically disabled in three situations:

1. You pass the `--no-color` flag explicitly
2. The `NO_COLOR` environment variable is set on your system (a community standard)
3. The output is being piped to a file or another program

This prevents raw escape codes like `\033[1;32m` from cluttering your output files.

---

## Why No External Libraries?

Everything runs on Python's built-in standard library:

| Module | Role |
|---|---|
| `ipaddress` | All subnet math — network addresses, masks, host ranges |
| `argparse` | Parses command-line flags cleanly |
| `json` | Serializes results for the `--export` flag |
| `os` / `sys` | Checks the environment for color support |

Zero `pip install`. Clone and run.

---

## Project Structure

```
subnetcalc/
├── subnetcalc.py   # The entire tool — one file, ~200 lines
└── README.md
```

---

## Key Concepts This Tool Reinforces

**Why does a /24 give 254 usable hosts and not 256?**
Every subnet reserves two addresses: the **network address** (first) and the **broadcast address** (last). 256 − 2 = 254.

**Why does adding one prefix bit halve the hosts?**
Each bit is binary — it doubles the subnets and halves the space available for hosts. `/24` → `/25` goes from 254 hosts to 126 hosts per subnet, but you now have 2 subnets instead of 1.

**What is a wildcard mask?**
The inverse of the subnet mask. Where the subnet mask has `1`s, the wildcard has `0`s. Used in ACLs and routing protocols (like OSPF) to define which bits to match.

---

*Built as a Network+ study project — because the best way to understand subnetting is to implement it.*
