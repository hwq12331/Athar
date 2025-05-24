import WebTorrent from 'webtorrent'
import fs from 'fs'
import path from 'path'

const filePath = process.argv[2]

if (!filePath || !fs.existsSync(filePath)) {
  console.error("❌ Please provide a valid file or folder path.")
  process.exit(1)
}

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
  // ✅ Python will look for this
  console.log("MAGNET URI")
  console.log(torrent.magnetURI)
})
