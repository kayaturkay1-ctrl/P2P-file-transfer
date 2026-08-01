import socket
import json
import time
import os
import math

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 6000
ANNOUNCE_INTERVAL = 8

def get_available_chunks(directory="."):
    """Klasördeki paylaşıma uygun tüm parça dosyalarını (chunk) bulur."""
    chunks = []
    for f in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, f)):
            # Python scriptlerini, logları, ana dosyaları vb. hariç tut
            if not f.endswith(('.py', '.json', '.txt', '.log', '.png', '.jpg', '.pdf')):
                # İndirici tarafından birleştirilmiş son haldeki dosyaları da gizle
                if "_assembled" not in f:
                    chunks.append(f)
    return chunks

def split_real_file_into_chunks(filepath):
    file_size = os.path.getsize(filepath)
    chunk_size = math.ceil(file_size / 3)
    base_name = os.path.basename(filepath)
    name_without_ext, _ = os.path.splitext(base_name)
    
    chunks_created = []
    with open(filepath, "rb") as original_file:
        for i in range(1, 4):
            chunk_data = original_file.read(chunk_size)
            if not chunk_data:
                break
            chunk_filename = f"{name_without_ext}_{i}"
            with open(chunk_filename, "wb") as chunk_file:
                chunk_file.write(chunk_data)
            chunks_created.append(chunk_filename)
            
    print(f"[{filepath}] dosyası {len(chunks_created)} parçaya bölündü: {chunks_created}")
    return chunks_created

def announce_chunks(username, udp_socket):
    try:
        print("Duyuru yayını başlatıldı (Her 8 saniyede bir)...")
        while True:
            # Klasörü her döngüde yeniden tara (Dinamik paylaşım)
            current_chunks = get_available_chunks() 
            message_dict = {
                "username": username,
                "chunks": current_chunks
            }
            message_bytes = json.dumps(message_dict).encode('utf-8')
            udp_socket.sendto(message_bytes, (BROADCAST_IP, BROADCAST_PORT))
            print(f"[DUYURU] Gönderildi: {message_dict}")
            time.sleep(ANNOUNCE_INTERVAL)
    except KeyboardInterrupt:
        print("\nDuyuru durduruldu.")
    finally:
        udp_socket.close()

if __name__ == "__main__":
    print("--- P2P Dosya Paylaşım: Parça Duyurucu ---")
    current_user = input("Kullanıcı adınızı girin: ").strip()
    
    with open("my_username.txt", "w", encoding="utf-8") as f:
        f.write(current_user)

    while True:
        filepath = input("Paylaşmak istediğiniz gerçek dosyanın yolunu/adını girin (örn: forest.png): ").strip()
        if os.path.exists(filepath):
            break
        else:
            print(f"[UYARI] '{filepath}' bu klasörde bulunamadı! Lütfen tekrar deneyin.")

    split_real_file_into_chunks(filepath)
    
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    announce_chunks(current_user, udp_socket)