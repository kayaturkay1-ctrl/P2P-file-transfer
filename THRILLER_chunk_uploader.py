import socket
import json
import os
import random
import base64
import time
import pyDes
import threading

TCP_PORT = 6001
DH_P = 907
DH_G = 7
UPLOAD_LOG = "upload_history.log"
IPS_FILE = "registry_ips.json"

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def log_upload(chunk_name, recipient_ip):
    recipient_name = recipient_ip
    if os.path.exists(IPS_FILE):
        try:
            with open(IPS_FILE, "r") as file_obj:
                maps = json.load(file_obj)
                recipient_name = maps.get(recipient_ip, recipient_ip)
        except: 
            pass

    log_entry = f"[{get_timestamp()}] Chunk: {chunk_name} | To: {recipient_name} | Status: SENT\n"
    with open(UPLOAD_LOG, "a") as file_obj:
        file_obj.write(log_entry)

def derive_des_key(shared_secret):
    des_key_string = str(shared_secret).zfill(8)[:8]
    return des_key_string.encode('utf-8')

def client_handler(client_connection, client_address):
    recipient_ip = client_address[0]
    try:
        while True:
            received_data = client_connection.recv(1024)
            if not received_data:
                break
                
            payload = json.loads(received_data.decode('utf-8'))
            
            if "key" in payload:
                client_public = int(payload["key"])
                private_key = random.randint(2, DH_P - 2)
                public_key = pow(DH_G, private_key, DH_P)
                
                client_connection.sendall(json.dumps({"key": str(public_key)}).encode('utf-8'))
                
                shared_secret = pow(client_public, private_key, DH_P)
                continue
                
            elif "requested_secured_content" in payload:
                chunk_name = payload["requested_secured_content"]
                if not os.path.exists(chunk_name):
                    break
                    
                with open(chunk_name, "rb") as file_obj:
                    raw_bytes = file_obj.read()
                    
                des_key_bytes = derive_des_key(shared_secret)
                cipher = pyDes.des(des_key_bytes, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
                encrypted_bytes = cipher.encrypt(raw_bytes)
                
                # type: ignore eklenerek analizörün pyDes belirsizliği yüzünden hata vermesi engellendi
                b64_string = base64.b64encode(encrypted_bytes).decode('utf-8')  # type: ignore
                response = {
                    "chunk_name": chunk_name,
                    "encrypted_chunk": b64_string
                }
                client_connection.sendall(json.dumps(response).encode('utf-8'))
                log_upload(chunk_name, recipient_ip)
                break
                
            elif "requested_content" in payload:
                chunk_name = payload["requested_content"]
                if not os.path.exists(chunk_name):
                    break
                    
                with open(chunk_name, "rb") as file_obj:
                    raw_bytes = file_obj.read()
                    
                # type: ignore eklenerek analizörün tip karmaşası yaşaması engellendi
                b64_string = base64.b64encode(raw_bytes).decode('utf-8')  # type: ignore
                response = {
                    "chunk_name": chunk_name,
                    "data": b64_string
                }
                client_connection.sendall(json.dumps(response).encode('utf-8'))
                log_upload(chunk_name, recipient_ip)
                break
    except Exception as error_msg:
        print(f"[Handler Error] Issue dealing with {recipient_ip}: {error_msg}")
    finally:
        client_connection.close()

def main():
    print("=== Chunk Uploader Process ===")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", TCP_PORT))
    server_socket.listen(5)
    print(f"[Listening] Running file transfer engine on TCP Port {TCP_PORT}...")

    try:
        while True:
            client_connection, client_address = server_socket.accept()
            client_thread = threading.Thread(target=client_handler, args=(client_connection, client_address), daemon=True)
            client_thread.start()
    except Exception as error_msg:
        print(f"[Server Error] {error_msg}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()