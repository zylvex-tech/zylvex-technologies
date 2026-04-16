---
id: competitive-analysis
title: Competitive Analysis
sidebar_label: Competitive Analysis
slug: /business/competitive-analysis
---

# Competitive Analysis

Zylvex sits at the intersection of several existing categories. This analysis compares Zylvex to the nearest competitors in each dimension.

---

## Comparison Table

| Feature | **Zylvex** | Pokémon GO / Niantic | Notion | Miro | LinkedIn |
|---------|-----------|---------------------|--------|------|----------|
| **Primary use case** | Spatial-social knowledge platform | Location-based gaming | Document/wiki | Visual collaboration | Professional social network |
| **Spatial anchors at GPS coords** | ✅ Full API | ✅ Game-only, closed | ❌ | ❌ | ❌ |
| **Open developer API** | ✅ Full REST API | ⚠️ Lightship VPS (limited) | ✅ Database API | ✅ Canvas API | ⚠️ Limited |
| **Mind mapping** | ✅ BCI-enhanced canvas | ❌ | ⚠️ Basic only | ✅ (no BCI) | ❌ |
| **BCI / focus data** | ✅ First-class feature | ❌ | ❌ | ❌ | ❌ |
| **Social graph** | ✅ Follow, reactions, feeds | ✅ Team/friend system | ⚠️ Workspace only | ⚠️ Team only | ✅ Full social graph |
| **Real-time collaboration** | ✅ WebSocket (OT planned) | ❌ | ✅ | ✅ | ⚠️ Comments only |
| **Mobile app** | ✅ iOS + Android (Expo) | ✅ Native | ✅ | ✅ | ✅ |
| **AR camera overlay** | ✅ | ✅ Game-grade AR | ❌ | ❌ | ❌ |
| **Self-hostable** | ✅ Enterprise tier | ❌ | ❌ | ❌ | ❌ |
| **Open source** | ✅ Core platform | ❌ | ❌ | ❌ | ❌ |
| **Creator monetization** | ✅ Marketplace (Phase 3) | ⚠️ Limited | ❌ | ❌ | ✅ Creator mode |
| **Free tier** | ✅ 50 anchors, 10 maps | ✅ Full free | ✅ Limited blocks | ✅ 3 boards | ✅ Full free |
| **Enterprise SSO** | ✅ Phase 2 | ❌ | ✅ | ✅ | ✅ |

---

## Zylvex vs Niantic / Pokémon GO

### Similarities
- GPS-anchored content at real-world locations
- Mobile AR camera overlay
- Social network around physical places

### Key Differences

| Dimension | Niantic | Zylvex |
|-----------|---------|--------|
| **Content model** | Game entities (Pokémon, gyms) | User-created knowledge (text, image, video, audio) |
| **Developer access** | Lightship VPS — limited, gated | Open REST API from day 1 |
| **Use case** | Entertainment / gaming | Knowledge work, exploration, education, business |
| **Monetization** | In-app purchases (game items) | SaaS tiers + creator marketplace |
| **BCI integration** | ❌ | ✅ |
| **Mind mapping** | ❌ | ✅ |
| **Self-hostable** | ❌ | ✅ |

**Verdict:** Niantic owns the *gaming* spatial layer; Zylvex owns the *knowledge* spatial layer. Different markets, minimal overlap.

---

## Zylvex vs Notion

### Similarities
- Target knowledge workers
- Team collaboration features
- REST API available

### Key Differences

| Dimension | Notion | Zylvex Mind Mapper |
|-----------|--------|-------------------|
| **Knowledge structure** | Pages, databases, blocks (flat) | Hierarchical mind map tree (spatial) |
| **Geographic context** | ❌ No location awareness | ✅ Anchors link knowledge to places |
| **BCI / cognitive data** | ❌ | ✅ Focus scores on every node |
| **Visual canvas** | Limited (tables/kanban) | Full ReactFlow drag-and-drop |
| **Real-time collab** | ✅ Mature | Planned Phase 3 |
| **AI features** | ✅ Notion AI ($10/month) | Planned Phase 3 (spatial knowledge graph) |

**Verdict:** Notion is flat documents. Zylvex Mind Mapper is *spatial* (nodes positioned in 2D space) and *biometric* (focus scores reveal cognitive context). Different workflows — not directly competing for the same jobs-to-be-done.

---

## Zylvex vs Miro

### Similarities
- Visual canvases with drag-and-drop
- Team collaboration
- Real-time (or planned real-time) editing

### Key Differences

| Dimension | Miro | Zylvex Mind Mapper |
|-----------|------|-------------------|
| **Canvas type** | Freeform infinite whiteboard | Structured mind map tree |
| **BCI integration** | ❌ | ✅ |
| **Spatial anchoring** | ❌ No GPS/physical world | ✅ Maps can link to spatial anchors |
| **BCI session data** | ❌ | ✅ Focus timeline per session |
| **Template library** | ✅ 2,500+ | Planned Phase 3 |
| **Integrations** | ✅ 130+ (Jira, Slack, etc.) | Planned Phase 3 |
| **Pricing** | Team $8/user/month | Pro $12/month (per person) |

**Verdict:** Miro is a mature, deeply integrated product with 50M+ users. Zylvex's BCI integration creates a fundamentally different product — one Miro cannot replicate without a complete platform rethink.

---

## Zylvex vs LinkedIn

### Similarities
- Social graphs (follow/unfollow, feeds)
- Professional knowledge sharing
- Reactions and engagement

### Key Differences

| Dimension | LinkedIn | Zylvex |
|-----------|----------|--------|
| **Social graph focus** | Professional connections | Spatial-social (location-based) |
| **Content** | Text posts, articles, videos | Spatial anchors + mind maps |
| **Geographic discovery** | ❌ No location-based feed | ✅ Nearby feed (radius-based) |
| **Knowledge structure** | Flat posts | Hierarchical mind maps |
| **BCI** | ❌ | ✅ |
| **Real-time** | ❌ Polling-based | ✅ WebSocket |
| **Developer API** | Limited (profile data only) | Full platform API |

**Verdict:** LinkedIn is deeply entrenched in hiring (950M users). Zylvex is not competing for LinkedIn's core use case. The overlap is in *local knowledge discovery* and *collaborative thinking* — markets where LinkedIn has no product.

---

## Competitive Positioning

```mermaid
quadrantChart
    title Zylvex Competitive Positioning
    x-axis Low Spatial Awareness --> High Spatial Awareness
    y-axis Low Cognitive Enhancement --> High Cognitive Enhancement
    quadrant-1 Zylvex Target Zone
    quadrant-2 Niche BCI tools
    quadrant-3 Legacy productivity
    quadrant-4 Location-based gaming
    Zylvex: [0.9, 0.9]
    Niantic/Pokemon GO: [0.85, 0.05]
    Notion: [0.1, 0.1]
    Miro: [0.2, 0.15]
    LinkedIn: [0.05, 0.1]
    Google Maps: [0.9, 0.05]
    Neurosity (BCI only): [0.1, 0.8]
```

**Zylvex occupies a unique position:** high spatial awareness + high cognitive enhancement. No current competitor is in this quadrant.

---

## Competitive Moats

| Moat Type | Strength | Notes |
|-----------|----------|-------|
| Data network effects | 🟡 Medium | Anchor data becomes more valuable with more contributors |
| BCI data lock-in | 🟢 Strong | Users' cognitive histories are proprietary to the platform |
| Spatial social graph | 🟢 Strong | Hard to recreate "who follows me in physical space" elsewhere |
| Developer ecosystem | 🟡 Building | Open API from day 1; SDK and webhooks planned |
| Category definition | 🟢 Strong | "Spatial-social computing" is ours to define |
| BCI technical expertise | 🟡 Medium | Hardware adapters and focus algorithms take time to develop |
