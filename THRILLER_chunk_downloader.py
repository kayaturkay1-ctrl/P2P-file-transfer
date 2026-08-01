import socket
import json
import os
import random
import base64
import time
import pyDes

TCP_PORT = 6001
DH_P = 907
DH_G = 7
DOWNLOAD_LOG = "download_history.log"
IPS_FILE = "registry_ips.json"
CONTENT_FILE = "registry_content.json"

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def log_download(chunk_name, ip_address):
    log_entry = f"[{get_timestamp()}] Chunk: {chunk_name} | From: {ip_address} | Status: RECEIVED\n"
    with open(DOWNLOAD_LOG, "a") as f:
        f.write(log_entry)

def load_registry(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {}

def derive_des_key(shared_secret):
    des_key_string = str(shared_secret).zfill(8)[:8]
    return des_key_string.encode('utf-8')

def request_chunk(ip_address, chunk_name, secure_mode):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((ip_address, TCP_PORT))
        
        if secure_mode:
            private_key = random.randint(2, DH_P - 2)
            public_key = pow(DH_G, private_key, DH_P)
            
            sock.sendall(json.dumps({"key": str(public_key)}).encode('utf-8'))
            
            resp_data = sock.recv(1024)
            resp = json.loads(resp_data.decode('utf-8'))
            server_public_key = int(resp["key"])
            
            shared_secret = pow(server_public_key, private_key, DH_P)
            
            req_payload = {"requested_secured_content": chunk_name}
            sock.sendall(json.dumps(req_payload).encode('utf-8'))
            
            raw_response = b""
            while True:
                packet = sock.recv(4096)
                if not packet:
                    break
                raw_response += packet
                
            final_resp = json.loads(raw_response.decode('utf-8'))
            b64_string = final_resp["encrypted_chunk"]
            encrypted_bytes = base64.b64decode(b64_string)
            
            des_key_bytes = derive_des_key(shared_secret)
            cipher = pyDes.des(des_key_bytes, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
            raw_bytes = cipher.decrypt(encrypted_bytes)
            
        else:
            req_payload = {"requested_content": chunk_name}
            sock.sendall(json.dumps(req_payload).encode('utf-8'))
            
            raw_response = b""
            while True:
                packet = sock.recv(4096)
                if not packet:
                    break
                raw_response += packet
                
            final_resp = json.loads(raw_response.decode('utf-8'))
            b64_string = final_resp["data"]
            raw_bytes = base64.b64decode(b64_string)
            
        with open(chunk_name, "wb") as f:
            f.write(raw_bytes)
            
        log_download(chunk_name, ip_address)
        return True
        
    except Exception as e:
        print(f"[Error] Failed to download {chunk_name} from {ip_address}: {e}")
        return False
    finally:
        sock.close()

def main():
    while True:
        print("\n=== P2P Chunk Downloader ===")
        print("1. View Contents")
        print("2. Download Content")
        print("3. History")
        print("4. Exit")
        choice = input("Select an option (1-4): ").strip()
        
        content_map = load_registry(CONTENT_FILE)
        ips_map = load_registry(IPS_FILE)
        
        if choice == "1":
            print("\n--- Available Files in LAN Network ---")
            unique_files = set()
            for chunk_name in content_map.keys():
                if "_" in chunk_name:
                    root_name = chunk_name.rsplit("_", 1)[0]
                    unique_files.add(root_name)
            
            if unique_files:
                for f in unique_files:
                    print(f"- {f}")
            else:
                print("No files discovered yet.")
                
        elif choice == "2":
            content_root = input("Enter content name to pull (e.g., 'forest'): ").strip()
            security_choice = input("Download securely? (yes/no): ").strip().lower()
            secure_mode = True if security_choice in ["yes", "y"] else False
            
            success_count = 0
            for index in ["1", "2", "3"]:
                target_chunk = f"{content_root}_{index}"
                
                # Kullanıcı isimleri listesini alıyoruz
                peer_names = content_map.get(target_chunk, [])
                chunk_downloaded = False
                
                for peer_name in peer_names:
                    # Kullanıcı isminden IP'yi buluyoruz (İsterge 2.2.0-E)
                    ip = ips_map.get(peer_name)
                    if not ip:
                        continue
                        
                    print(f"Requesting {target_chunk} from user: {peer_name} ({ip})")
                    
                    if request_chunk(ip, target_chunk, secure_mode):
                        print(f"Successfully received {target_chunk} from {peer_name}!")
                        chunk_downloaded = True
                        success_count += 1
                        break
                    else:
                        print(f"Failed to fetch chunk from {peer_name}. Trying alternative hosts...")
                        
                if not chunk_downloaded:
                    print(f"[Alert] All options exhausted. {target_chunk} is offline.")
            
            if success_count == 3:
                print(f"\n[Success] All 3 parts downloaded! Merging into '{content_root}_assembled.png'...")
                with open(f"{content_root}_assembled.png", "wb") as output_file:
                    for index in ["1", "2", "3"]:
                        with open(f"{content_root}_{index}", "rb") as cf:
                            output_file.write(cf.read())
                print("File assembly finalized. Individual chunks are kept for verification.")
                
        elif choice == "3":
            print("\n--- Local Download History Log ---")
            if os.path.exists(DOWNLOAD_LOG):
                with open(DOWNLOAD_LOG, "r") as f:
                    print(f.read())
            else:
                print("No log files discovered under local working path.")
                
        elif choice == "4":
            print("Exiting Client.")
            break
        else:
            print("Invalid parsing parameter. Please select options 1-4.")

if __name__ == "__main__":
    main()