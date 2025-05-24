import streamlit as st
import hashlib
import subprocess
import os
import datetime
import tempfile
import shutil
import threading
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

# -------------------- CONFIG --------------------
INFURA_URL = os.getenv("INFURA_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
MAGNET_SCRIPT = os.path.abspath("magnet.mjs")
UPLOAD_SCRIPT = os.path.abspath("upload.js")


NODE_PATH = shutil.which("node")
if NODE_PATH is None:
    st.sidebar.warning("⚠️ Node.js not found. Torrent generation will not work.")

# -------------------- ABI --------------------
ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "string", "name": "fileHash", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "fileName", "type": "string"},
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "DocumentRegistered",
        "type": "event"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "fileHash", "type": "string"},
            {"internalType": "string", "name": "fileName", "type": "string"}
        ],
        "name": "registerDocument",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "", "type": "string"}],
        "name": "documents",
        "outputs": [
            {"internalType": "string", "name": "fileName", "type": "string"},
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "fileHash", "type": "string"}],
        "name": "getDocument",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# -------------------- WEB3 INIT --------------------
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# -------------------- FUNCTIONS --------------------
def hash_file(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def send_to_node_seeder(file_path):
    with open("seed_task.txt", "w") as f:
        f.write(file_path)


def show_seeding_status(magnet_uri):
    try:
        return subprocess.Popen(
            [NODE_PATH, os.path.abspath("seed_status.mjs"), magnet_uri],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
    except Exception as e:
        return None


def create_torrent(file_path, log_callback):
    try:
        proc = subprocess.Popen(
            [NODE_PATH, MAGNET_SCRIPT, file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        magnet_uri = None
        capture_next = False

        def stream_logs():
            nonlocal magnet_uri, capture_next
            for line in proc.stdout:
                line = line.strip()
                if capture_next:
                    magnet_uri = line
                    capture_next = False
                elif "MAGNET URI" in line:
                    capture_next = True

        thread = threading.Thread(target=stream_logs)
        thread.start()
        thread.join(timeout=20)

        return magnet_uri or "⚠️ Magnet URI not found."
    except Exception as e:
        return f"🚫 Error: {str(e)}"



def upload_to_ipfs_js(file_path):
    try:
        result = subprocess.run([NODE_PATH, UPLOAD_SCRIPT, file_path], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if "IPFS URL" in line and i + 1 < len(lines):
                return lines[i + 1].strip()
        return "⚠️ IPFS URL not found."
    except Exception as e:
        return f"🚫 IPFS Upload error: {e}"



def register_on_chain(file_hash, file_name):
    try:
        nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
        tx = contract.functions.registerDocument(file_hash, file_name).build_transaction({
            'chainId': 11155111,
            'gas': 200000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'nonce': nonce
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return w3.to_hex(tx_hash)
    except Exception as e:
        return str(e)

def verify_document(file_hash):
    try:
        doc = contract.functions.getDocument(file_hash).call()
        if isinstance(doc, (list, tuple)) and len(doc) == 3:
            file_name, owner, timestamp = doc
            if file_name and file_name.strip() != "":
                return {
                    "fileName": file_name,
                    "owner": owner,
                    "timestamp": datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                }
        return None
    except Exception as e:
        print("Error in verify_document:", e)
        return None

# -------------------- STREAMLIT UI --------------------
st.title("📜 Athar Archive – Decentralized Record Verification")
menu = st.sidebar.radio("Choose an action", ["Upload & Register", "Verify Document", "About"])

if menu == "Upload & Register":
    uploaded_file = st.file_uploader("Upload a document")
    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_hash = hash_file(file_bytes)
        st.success(f"SHA-256 Hash: {file_hash}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name
            
        
            
            
        send_to_node_seeder(temp_file_path)
        
        status_placeholder = st.empty()
        
        def update_log(message):   status_placeholder.text(message)
    
            
        with st.spinner("⏳ Generating magnet URI... Please wait..."):
            magnet_uri = create_torrent(temp_file_path, update_log)

        if magnet_uri.lower().startswith("magnet:?"):
            st.success("✅ Magnet URI generated!")
            st.text_area("Magnet URI", magnet_uri, disabled=True)
        else:
            st.error(magnet_uri)  # Show the error message

        print("🧪 Magnet from create_torrent():", magnet_uri)

        

        if "magnet:?" in magnet_uri:
            st.info("🛰️ Seeding started. Torrent will stay active as long as the app is running.")
            if st.button("Show Seeding Console"):
                proc = show_seeding_status(magnet_uri)
                st.code("📡 Seeding live... check your terminal window for updates.", language="bash")
                

        ipfs_url = upload_to_ipfs_js(temp_file_path)
        st.markdown(f"🌐 [View on IPFS]({ipfs_url})", unsafe_allow_html=True)

        try:
            os.remove(temp_file_path)
        except Exception as e:
            st.warning(f"⚠️ Could not delete temporary file: {e}")

        existing = verify_document(file_hash)
        if existing:
            st.warning("⚠️ This document is already registered on-chain.")
            st.write(existing)
        else:
            if st.button("Register on Blockchain"):
                try:
                    tx = register_on_chain(file_hash, uploaded_file.name)
                    st.success(f"✅ Registered! Tx Hash: {tx}")
                except Exception as e:
                    st.error("❌ Blockchain registration failed.")
                    st.text(f"Details: {str(e)}")

elif menu == "Verify Document":
    verify_file = st.file_uploader("Upload file to verify")
    if verify_file:
        file_hash = hash_file(verify_file.read())
        st.info(f"SHA-256: {file_hash}")
        result = verify_document(file_hash)
        if result:
            st.success("✅ Document is registered on-chain.")
            st.write(result)
        else:
            st.error("❌ Document is NOT registered.")

else:
    st.markdown("""
    ### What is Athar?
    Athar is a decentralized archive that protects historical documents and records from tampering by hashing files, generating torrent-based distribution, and registering their metadata on the blockchain.

    **Your file = Hashed 🔐 + Archived 🧾 + Verified 🛡️**
    """)

