import WebTorrent from 'webtorrent'
import fs from 'fs'
import path from 'path'

// 📁 Input path from command line
const filePath = process.argv[2]

if (!filePath || !fs.existsSync(filePath)) {
  console.error("❌ Please provide a valid file or folder path.")
  process.exit(1)
}

// 🚀 Initialize client
const client = new WebTorrent()

client.seed(filePath, {
  path: path.dirname(filePath),
  announce: [
    "wss://tracker.openwebtorrent.com",
    "wss://tracker.btorrent.xyz",
    "wss://tracker.fastcast.nz",
    "wss://tracker.files.fm:7073/announce",
    "wss://tracker.webtorrent.io"
  ]
}, torrent => {
  console.log("\n📡 Seeding started!")
  console.log("📁 Name:", torrent.name)
  console.log("📦 Size:", (torrent.length / (1024 * 1024)).toFixed(2), "MB")
  console.log("🔗 MAGNET URI:\n" + torrent.magnetURI)

  // 🔄 Live stats every 5 seconds
  setInterval(() => {
    console.log(`\n👥 Peers: ${torrent.numPeers}`)
    torrent.wires.forEach((wire, i) => {
      console.log(`- Peer ${i + 1}: ${wire.remoteAddress || 'unknown'} (${(wire.downloaded / 1024).toFixed(1)} KB downloaded)`)
    })
  }, 5000)
})
