# Decentralized Chat

A peer-to-peer chat application built on the Kademlia DHT protocol. Supports private (1-to-1) messaging and public group chats.

## Features

- **Decentralized**: No central server, nodes discover each other via DHT
- **Private messaging**: Direct encrypted messages between two users
- **Group chats**: Public nodes act as broadcast hubs for group conversations
- **Web interface**: Browser-based UI with real-time updates via WebSocket

## Requirements

- Python 3.8+
- Flask
- Flask-SocketIO

## Installation

```bash
pip install flask flask-socketio
```

## Usage

Start the application:

```bash
python Main.py
```

Access the web interface at **http://127.0.0.1:12345** (may take a few seconds to start).

## Running Tests

```bash
python -m pytest Tests/
```

## Architecture

### Kademlia DHT

Nodes are identified by SHA-1 hashes of usernames. The routing table organizes known nodes into k-buckets based on XOR distance, enabling efficient node lookup in O(log n) hops.

### Node Types

| Type | Description |
|------|-------------|
| Private | Receives direct messages only |
| Public | Acts as group chat hub, broadcasts messages to all subscribers |

### Protocol Commands

| Command | Description |
|---------|-------------|
| `FIND_NODE` | Locate a node by ID, returns k closest nodes |
| `STORE` | Send a message to a node |
| `PING` | Check if a node is alive |
| `SUBSCRIBE` | Join a public chat |
| `UNSUBSCRIBE` | Leave a public chat |

### Components

- **Client**: Initiates outbound requests (node lookup, message sending)
- **Server**: Handles inbound requests, manages message queues
- **RoutingTable**: Maintains k-buckets of known nodes
- **FlaskThread**: Web server with Socket.IO for real-time updates

## Configuration

Key parameters in `Main.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `k` | 10 | Max nodes returned per lookup |
| `alpha` | 3 | Parallel lookups during discovery |
| `bucket_limit` | 20 | Max nodes per k-bucket |
| `bootstrap_node` | 127.0.0.1:5555 | Initial node for network entry |
