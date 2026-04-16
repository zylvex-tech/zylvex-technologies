---
id: mobile-setup
title: Mobile Setup Guide
sidebar_label: Mobile Setup
slug: /guides/mobile-setup
---

# Mobile Setup Guide

This guide covers running both Zylvex mobile apps — **Spatial Canvas** (JavaScript) and **Mind Mapper** (TypeScript) — on iOS Simulator and Android Emulator using Expo.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| npm | 9+ | Bundled with Node |
| Xcode | 15+ | Mac App Store (iOS only) |
| Android Studio | latest | [developer.android.com](https://developer.android.com/studio) |
| Expo Go (physical device) | latest | App Store / Play Store |

---

## 1. Start the Backend

Both mobile apps need the backend services running:

```bash
cd zylvex-technologies
docker compose -f docker-compose.full-stack.yml up --build
```

Or just the required services:

```bash
docker compose -f docker-compose.full-stack.yml up \
  postgres-auth auth-service \
  postgres-spatial spatial-canvas-backend \
  postgres-mm mind-mapper-backend
```

---

## 2. Spatial Canvas Mobile (JavaScript)

```bash
cd spatial-canvas/mobile
npm install
cp .env.example .env
```

Edit `.env`:

```env
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_AUTH_URL=http://localhost:8001
```

### Run on iOS Simulator

```bash
npx expo start --ios
```

### Run on Android Emulator

```bash
npx expo start --android
```

---

## 3. Mind Mapper Mobile (TypeScript)

```bash
cd mind-mapper/mobile-bci
npm install
cp .env.example .env
```

Edit `.env`:

```env
EXPO_PUBLIC_API_URL=http://localhost:8002
EXPO_PUBLIC_AUTH_URL=http://localhost:8001
```

### Run on iOS Simulator

```bash
npx expo start --ios
```

### Run on Android Emulator

```bash
npx expo start --android
```

---

## 4. iOS Simulator Setup

### Install Xcode Command Line Tools

```bash
xcode-select --install
```

### Install an iOS Runtime

1. Open Xcode → **Settings → Platforms**
2. Download **iOS 17** (or latest)

### Start the Simulator

```bash
# List available simulators
xcrun simctl list devices

# Boot a specific simulator
xcrun simctl boot "iPhone 15 Pro"

# Open the Simulator.app
open -a Simulator
```

---

## 5. Android Emulator Setup

### Create an AVD

1. Open Android Studio → **More Actions → Virtual Device Manager**
2. Click **Create Virtual Device**
3. Select **Pixel 7 Pro** → **API Level 34** (Android 14)
4. Click **Finish**

### Start the Emulator

```bash
# Via Android Studio: click ▶ next to the AVD
# Or from command line:
$ANDROID_HOME/emulator/emulator -avd Pixel_7_Pro_API_34
```

:::note Android and localhost
Android Emulator uses `10.0.2.2` to reach the host machine's localhost. Update your `.env`:

```env
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
EXPO_PUBLIC_AUTH_URL=http://10.0.2.2:8001
```
:::

---

## 6. Physical Device (Expo Go)

```bash
npx expo start
# Scan the QR code with the Expo Go app
```

For physical devices, replace `localhost` with your machine's LAN IP (e.g., `192.168.1.42`):

```env
EXPO_PUBLIC_API_URL=http://192.168.1.42:8000
EXPO_PUBLIC_AUTH_URL=http://192.168.1.42:8001
```

---

## 7. Camera and Location Permissions

### Camera (Spatial Canvas)

iOS will show a native permission dialog on first launch.  
To reset on simulator: **Settings → Privacy & Security → Camera**

Android:

```bash
adb shell pm grant com.zylvex.spatialcanvas android.permission.CAMERA
```

### Location

**iOS Simulator:** Simulate location via **Debug → Simulate Location** in the menu bar.

**Android Emulator:**

```bash
adb emu geo fix -122.4194 37.7749
```

---

## 8. Running Both Apps Simultaneously

```bash
# Terminal 1 — Spatial Canvas on port 8082
cd spatial-canvas/mobile && npx expo start --port 8082

# Terminal 2 — Mind Mapper on port 8083
cd mind-mapper/mobile-bci && npx expo start --port 8083
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Metro bundler fails | `npx expo start --clear` |
| "Network request failed" | Check backend is running; use LAN IP for physical devices |
| iOS CocoaPods error | `cd ios && pod install --repo-update` |
| Expo SDK mismatch | `npx expo install --fix` |
