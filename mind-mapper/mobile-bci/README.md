# Mind Mapper Mobile (BCI)

React Native BCI visualization app for Mind Mapper. Written entirely in TypeScript.

## Setup

```bash
npm install
cp .env.example .env
```

## Environment

| Variable | Default | Description |
|---|---|---|
| `EXPO_PUBLIC_API_URL` | `http://localhost:8002` | Mind Mapper API base URL |
| `EXPO_PUBLIC_AUTH_URL` | `http://localhost:8001` | Auth service base URL |

## BCI Simulator

The focus slider (0–100) simulates neural input:
- **High (>70):** nodes rendered green — peak cognitive engagement
- **Moderate (40–70):** nodes rendered yellow — normal working state
- **Low (<40):** nodes rendered red — fatigue or distraction

## Running

```bash
expo start
```

Then scan the QR code, or press `a` for Android / `i` for iOS simulator.
