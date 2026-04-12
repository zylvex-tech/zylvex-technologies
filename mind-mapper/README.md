# Mind Mapper

BCI-driven mind mapping platform built by Zylvex Technologies.

## Overview

Mind Mapper lets users visualize cognitive focus as interactive node trees. Neural focus levels (0-100) determine node colour and size — green for high focus, yellow for moderate, red for low.

## Current Status

MVP with manual focus slider (simulates BCI input). Real hardware integration is planned.

## Components

| Component | Path | Description |
|---|---|---|
| `backend-services/` | FastAPI REST API | Mind maps, nodes, BCI sessions |
| `mobile-bci/` | React Native (Expo, TypeScript) | Mobile visualization app |
| `desktop-studio/` | Stub | Desktop editing interface (planned) |
| `ml-models/` | Stub | Real BCI hardware adapter (planned) |

## Quick Start

```bash
docker compose -f ../../docker-compose.full-stack.yml up --build
```

Or start the backend alone:
```bash
cd backend-services && docker compose up --build
```
