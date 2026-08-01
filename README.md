P2P File Sharing Application

A peer-to-peer (P2P) local network file sharing system written in Python that handles chunked file distribution across network peers[cite: 1, 2]. Files are split into 3 chunks for distribution[cite: 2]. The system supports secure file transfers using Diffie-Hellman Key Exchange and DES Encryption[cite: 3, 4].

---

## 👥 Authors
* **Türkay KAYA, Reyyan ATBAY **[cite: 1]

---

## 📁 Repository File Structure

* **`THRILLER_content_discovery.py`** — Listens for UDP broadcasts on port 6000 to maintain active peer and content registries[cite: 5]. It flushes inactive registry data every 60 seconds[cite: 5].
* **`THRILLER_chunk_announcer.py`** — Splits a specified target file into 3 chunks[cite: 2]. It periodically broadcasts the host's available chunks and username over UDP every 8 seconds[cite: 2].
* **`THRILLER_chunk_uploader.py`** — Acts as a TCP server on port 6001 that handles chunk upload requests[cite: 4]. It supports Diffie-Hellman key exchange and encrypts the chunks using pyDes before transmission[cite: 4].
* **`THRILLER_chunk_downloader.py`** — An interactive terminal dashboard to discover files and request chunks securely or unsecurely from peers[cite: 3]. It automatically assembles the 3 downloaded chunks into the final file[cite: 3].
* **`THRILLER_Project_Report.pdf`** — Detailed technical documentation and project report[cite: 1].
* **`THRILLER_encrypted_chunk_exchange.png`** — Network diagram illustrating encrypted chunk transfer flow[cite: 1].
* **`THRILLER_unencrypted_chunk_exchange.png`** — Network diagram illustrating unencrypted chunk transfer flow[cite: 1].

---

## 📄 Generated Data & Log Files
*(These files are generated locally during the execution of the application)*

* **`registry_ips.json` & `registry_content.json`** — Local database files tracking active peers and their hosted chunks[cite: 5].
* **`download_history.log`** — Local log file recording successfully received chunks and their source IPs[cite: 3].
* **`upload_history.log`** — Local log file recording successfully sent chunks and their destination IPs or Usernames[cite: 4].
* **`my_username.txt`** — Stores the local user's chosen username for broadcasts[cite: 2].

---

## ⚙️ System Requirements & Software Versions

* **Operating System:** Windows 10/11, macOS, or Linux[cite: 1]
* **Python Version:** Python 3.12.x[cite: 1]
* **Tools:** VS Code, Wireshark[cite: 1]
* **Network:** Local Area Network (LAN)[cite: 3]

---

## 📦 Required Package Installations

```bash
pip install pyDes[cite: 1]