# Spatial Canvas Mobile App

React Native mobile app for the Spatial Canvas AR platform.

## Features

- **AR Camera Screen**: Place text/emoji anchors in the real world
- **Nearby Anchors Screen**: View anchors within 0.5km radius
- **GPS Integration**: Save and retrieve anchors by location
- **Cross-platform**: Works on iOS and Android

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the backend (in separate terminal):
```bash
cd ../backend
docker-compose up -d
```

3. Start the mobile app:
```bash
npm start
```

4. Use Expo Go app on your phone to scan QR code, or run on simulator.

## Screens

### Camera Screen
- Live camera view
- Tap to place anchor
- Input modal for anchor content
- GPS location capture

### Nearby Anchors Screen
- Shows anchors within 0.5km
- Distance and timestamp display
- Pull-to-refresh

## Environment Variables

Create `.env` file:
```
EXPO_PUBLIC_API_URL=http://localhost:8000
```

## Tech Stack

- React Native
- Expo (expo-camera, expo-location)
- React Navigation
- Axios for API calls

## Development

```bash
# Start development server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android
```

## Backend Integration

The app connects to the Spatial Canvas backend at `EXPO_PUBLIC_API_URL`.

Required endpoints:
- `POST /api/v1/anchors` - Create anchor
- `GET /api/v1/anchors` - Get nearby anchors
