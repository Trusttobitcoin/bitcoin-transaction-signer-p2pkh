# Bitcoin Testnet Transaction Signer

## Overview

This Python script provides functionality to sign and broadcast Bitcoin transactions on the testnet. It is specifically designed for use with the Bitcoin testnet. This tool demonstrates how to work with Bitcoin testnet transactions programmatically, including UTXO management, transaction creation, signing, and broadcasting. It's intended for educational purposes and to help developers understand the intricacies of Bitcoin transactions in a safe, test environment.

## Features

- Create and sign Bitcoin testnet transactions
- Fetch Unspent Transaction Outputs (UTXOs) from BlockCypher's testnet API
- Broadcast signed transactions to the Bitcoin testnet
- Support for Pay-to-Public-Key-Hash (P2PKH) testnet addresses



## How It Works

1. The script first fetches the UTXOs for your testnet address using the BlockCypher testnet API.
2. It then creates a transaction input using one of the available testnet UTXOs.
3. Two transaction outputs are created: one for the amount you're sending, and one for the change (if any).
4. The transaction is then constructed and signed using your testnet private key.
5. Finally, the signed transaction is broadcast to the Bitcoin testnet network via the BlockCypher testnet API.

## Key Components

- `PrivateKey`: Manages the testnet private key and derives the public key
- `Transaction`: Represents a Bitcoin testnet transaction
- `TxInput`: Represents a transaction input
- `TxOutput`: Represents a transaction output
- `create_p2pkh_script`: Creates a Pay-to-Public-Key-Hash script for testnet addresses
- `sign_and_transfer`: The main function that orchestrates the testnet transaction creation and signing process

## Security Considerations

- This script is for educational purposes only and should be used exclusively on the Bitcoin testnet.
- Never use this script with real bitcoins or on the Bitcoin mainnet without thorough testing and understanding of the risks involved.
- While testnet coins have no real value, still practice good security habits as if you were dealing with real bitcoins.
- The script uses the BlockCypher testnet API, which may have rate limits or require an API key for extensive usage.

## Contributing

Contributions to improve the script or expand its functionality are welcome. Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is provided "as is", without warranty of any kind. Use at your own risk. The authors or copyright holders shall not be liable for any claim, damages, or other liability arising from the use of the software. This script is designed for use with the Bitcoin testnet only and should never be used with real bitcoins or on the Bitcoin mainnet.

---

Remember to always practice safe key management, even with testnet coins. Happy coding and exploring the world of Bitcoin testnet transactions!
