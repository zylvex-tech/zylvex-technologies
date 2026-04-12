# Spatial Canvas Mobile

React Native AR camera app for placing and discovering spatial anchors. Built with Expo.

## Prerequisites

- Node 18+
- Expo CLI: `npm install -g expo-cli`

## Setup

```bash
npm install
cp .env.example .env
```

Edit `.env` to point `EXPO_PUBLIC_API_URL` at the Spatial Canvas API and `EXPO_PUBLIC_AUTH_URL` at the Auth service.

## Environment

| Variable | Default | Description |
|---|---|---|
| `EXPO_PUBLIC_API_URL` | `http://localhost:8000` | Spatial Canvas API base URL |
| `EXPO_PUBLIC_AUTH_URL` | `http://localhost:8001` | Auth service base URL |

## Running

```bash
expo start
```

Then scan the QR code, or press `a` for Android / `i` for iOS simulator.
