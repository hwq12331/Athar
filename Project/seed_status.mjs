// seed_status.mjs
import WebTorrent from 'webtorrent'
import path from 'path'

const magnetURI = process.argv[2]
const client = new WebTorrent()

client.add(magnetURI, torrent => {
  console.log("📡 Monitoring Torrent:")
  const interval = setInterval(() => {
    const progress = (torrent.progress * 100).toFixed(2)
    const up = formatBytes(torrent.uploadSpeed)
    const peers = torrent.numPeers
    const eta = torrent.timeRemaining === Infinity ? "∞" : (torrent.timeRemaining / 1000).toFixed(1) + "s"

    console.clear()
    console.log(`Peers: ${peers} | Upload: ${up}/s | Progress: ${progress}% | ETA: ${eta}`)
  }, 1000)

  torrent.on('done', () => {
    console.log('✅ Torrent fully uploaded!')
    clearInterval(interval)
  })
})

function formatBytes(bytes) {
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}
