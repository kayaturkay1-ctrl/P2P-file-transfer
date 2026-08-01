import socket
import json
import os
import time
import threading

UDP_PORT = 6000
IPS_FILE = "registry_ips.json"
CONTENT_FILE = "registry_content.json"

file_lock = threading.Lock()

def initialize_files():
    with file_lock:
        for f in [IPS_FILE, CONTENT_FILE]:
            if not os.path.exists(f):
                with open(f, "w") as file:
                    json.dump({}, file)

def update_registries(username, ip_address, chunks):
    with file_lock:
        try:
            with open(IPS_FILE, "r") as f: ips_map = json.load(f)
        except: ips_map = {}
        try: 
            with open(CONTENT_FILE, "r") as f: content_map = json.load(f)
        except: content_map = {}

        ips_map[ip_address] = username
        ips_map[username] = ip_address

        for chunk in chunks:
            if chunk not in content_map:
                content_map[chunk] = []
            # IP yerine USERNAME listeye ekleniyor (İsterge 2.2.0-D)
            if username not in content_map[chunk]:
                content_map[chunk].append(username)
                
        with open(IPS_FILE, "w") as f:
            json.dump(ips_map, f, indent=4)
        with open(CONTENT_FILE, "w") as f:
            json.dump(content_map, f, indent=4)
            
    print(f"[Discovered] {username} is hosting: {', '.join(chunks)}")

def wipe_content_routine():
    while True:
        time.sleep(60)
        with file_lock:
            with open(CONTENT_FILE, "w") as f:
                json.dump({}, f, indent=4)
            print("\n[Registry Clean] Flushed content dictionary for recency check.")

def main():
    initialize_files()
    print("=== Content Discovery Process ===")
    print(f"[Listening] Waiting for UDP traffic on port {UDP_PORT}...")

    cleaner = threading.Thread(target=wipe_content_routine, daemon=True)
    cleaner.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", UDP_PORT))

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            ip_address = addr[0]
            try:
                payload = json.loads(data.decode('utf-8'))
                username = payload.get("username")
                chunks = payload.get("chunks", [])
                
                if username and chunks:
                    update_registries(username, ip_address, chunks)
            except json.JSONDecodeError:
                pass
    except KeyboardInterrupt:
        print("\nShutting down discovery.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()