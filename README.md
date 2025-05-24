# Athar: Decentralized Historical Archiving System

Athar is a blockchain-powered archival platform that securely stores historical texts and documents using torrent and smart contract technologies. It ensures the integrity, verifiability, and permanence of historical records.

## 📦 Features

- Document hashing and torrent generation
- Blockchain-based smart contract for verification
- File upload, verification, and record lookup
- Frontend built with Streamlit
- Torrent seeding and magnet URI generation

## 🚀 How It Works

1. Upload a document.
2. It's hashed (SHA-256) and turned into a torrent file.
3. The document’s hash and metadata are registered on Ethereum via a smart contract.
4. Anyone can later verify that the document hasn’t changed by uploading it and checking the hash on-chain.

## 🛠️ Tech Stack

- Python (Streamlit)
- Node.js (torrent handling)
- Web3.py (Ethereum smart contract)
- IPFS (optional for P2P distribution)

## ⚙️ Setup Instructions

```bash
pip install -r requirements.txt
npm install

Make sure to add a .env file with:

INFURA_URL=your_infura_url
PRIVATE_KEY=your_private_key
WALLET_ADDRESS=your_wallet_address
CONTRACT_ADDRESS=your_contract_address


streamlit run athar.py
