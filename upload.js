import * as Client from '@web3-storage/w3up-client'
import { filesFromPaths } from 'files-from-path'
import path from 'path'

const client = await Client.create()

// use saved space
const space = await client.currentSpace()
if (!space) {
  console.error("❌ No space found. Run login flow first.")
  process.exit(1)
}

const filePath = process.argv[2]
const files = await filesFromPaths([filePath])
const root = await client.uploadDirectory(files)

// ✅ Print the full URL for Python
console.log(`https://${root.toString()}.ipfs.w3s.link/${path.basename(filePath)}`)

console.log("IPFS URL")
console.log(`https://${root.toString()}.ipfs.w3s.link/${path.basename(filePath)}`)

