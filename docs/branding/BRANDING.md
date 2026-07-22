# Neuraforge — Branding Guide

**Version:** 1.0 · **Phase:** 1 · **Status:** Draft for review · **Date:** 2026-07-16

---

## 1. Name

### 1.1 Platform name: **Neuraforge**

**Neura** (neural networks, the subject matter) + **forge** (to build by hand, from raw material, with heat and effort).

The name encodes the platform's core pedagogical promise: learners do not consume AI content —
they **forge** every component of a large language model themselves, from matrix multiplication
to a production deployment. A forge is also a workshop: a place you return to daily, where skill
compounds through repetition.

- **Full program title:** *Neuraforge — Building Large Language Models From Scratch: A 12-Month Interactive AI Engineering Program*
- **Short name / app name:** Neuraforge
- **Motto / tagline:** **"Forge intelligence from first principles."**
- **Secondary taglines:**
  - "From `import numpy` to production GPT."
  - "12 months. One model. Yours."
- **Domain candidates:** `neuraforge.ai`, `neuraforge.dev`, `neuraforge.org` (open-source home)
- **Naming rules:** Always one word, capital N only ("Neuraforge", never "NeuraForge" or "neura-forge" in prose; the wordmark alone may render FORGE in the accent color).

### 1.2 Sub-brand vocabulary (used across the product)

| Product concept | Branded term | Rationale |
|---|---|---|
| Monthly capstone | **Forge Project** | The big thing you hammer out each month |
| Daily challenge | **Daily Spark** | Small, hot, fast |
| Streak system | **Forge Streak** 🔥 | Keep the fire lit |
| AI tutor | **Ember** | The always-warm assistant from the forge |
| Achievement tiers | **Iron → Bronze → Steel → Damascus → Mythril** | Smithing metals, ascending rarity |
| Completion certificate | **Forgemaster Certificate** | Terminal credential of the 12-month program |
| Learner community rank | **Apprentice → Journeyman → Smith → Forgemaster** | Guild progression matching curriculum quarters |

---

## 2. Logo

Files: [`logo.svg`](logo.svg) (horizontal lockup) · [`icon.svg`](icon.svg) (app icon, 512×512).

### 2.1 Concept — "The Forged Network"

The glyph is a **five-node neural graph arranged as an anvil silhouette**, crowned by a sixth
**spark node** in forge-orange at its apex. Reading bottom-to-top it is a learner's trajectory:
a broad, stable base (fundamentals) narrowing through hidden layers (skills) to a single glowing
output (the model you build). Reading as an image it is an anvil throwing a spark — the moment
of creation.

### 2.2 Variants

| Variant | Use |
|---|---|
| **Horizontal lockup** (glyph + wordmark + tagline) | Website header, documentation, certificates |
| **Glyph only** (badge) | App icon, favicon, avatars, loading screens |
| **Wordmark only** | Dense UI footers, legal pages |
| **Monochrome** (all `#0B0B12` on light / `#FAFAFA` on dark) | Print, embossing, single-color contexts |

### 2.3 Usage rules

- **Clear space:** ≥ the height of one graph node radius (glyph) / cap-height of "N" (wordmark) on all sides.
- **Minimum sizes:** glyph 24 px; horizontal lockup 140 px wide. Below that, use glyph only.
- **Never:** stretch, rotate, recolor outside the palette, add drop shadows, place the color version on mid-tone backgrounds (use monochrome), or detach the spark node from the graph.
- The spark node is **always orange** — it is the only element that never changes color.

---

## 3. Color system

Designed for a **dark-first** product (learners code at night) with a fully specified light theme.
All pairings below meet WCAG 2.1 AA contrast for their stated roles.

### 3.1 Brand palette

| Token | Hex | Role |
|---|---|---|
| `brand-indigo` | `#6366F1` | Primary brand, interactive elements, links, focus rings |
| `brand-violet` | `#8B5CF6` | Gradient midpoint, secondary accents, "theory" content |
| `brand-cyan` | `#22D3EE` | Gradient end, data-viz primary, "code" content |
| `forge-orange` | `#F97316` | The Spark: streaks, achievements, CTAs of celebration, AI tutor "Ember" |
| `forge-amber` | `#FBBF24` | Spark gradient end, warnings, XP |

**Signature gradient:** `linear-gradient(135deg, #6366F1 0%, #8B5CF6 55%, #22D3EE 100%)` —
used for hero surfaces, progress rings, and the logo stroke. Never used behind body text.

### 3.2 Neutrals (dark theme — default)

| Token | Hex | Role |
|---|---|---|
| `bg-base` | `#0B0B12` | App background |
| `bg-raised` | `#131320` | Cards, panels |
| `bg-glass` | `rgba(255,255,255,0.06)` + `backdrop-blur(16px)` + 1px `rgba(255,255,255,0.10)` border | Glassmorphism surfaces (modals, floating toolbars, stat chips) |
| `text-primary` | `#FAFAFA` | Headings, body |
| `text-secondary` | `#A1A1AA` | Captions, metadata |
| `border-subtle` | `#27273A` | Dividers, input borders |

### 3.3 Neutrals (light theme)

| Token | Hex | Role |
|---|---|---|
| `bg-base` | `#FAFAFC` | App background |
| `bg-raised` | `#FFFFFF` | Cards |
| `bg-glass` | `rgba(255,255,255,0.65)` + blur + `rgba(11,11,18,0.08)` border | Glass surfaces |
| `text-primary` | `#0B0B12` | Headings, body |
| `text-secondary` | `#52525B` | Captions |
| `border-subtle` | `#E4E4EB` | Dividers |

### 3.4 Semantic colors

| Token | Dark | Light | Role |
|---|---|---|---|
| `success` | `#34D399` | `#059669` | Passed tests, completed lessons |
| `warning` | `#FBBF24` | `#B45309` | Due revisions, expiring streaks |
| `danger` | `#F87171` | `#DC2626` | Failed runs, destructive actions |
| `info` | `#22D3EE` | `#0891B2` | Hints, callouts |

### 3.5 Data-visualization palette (categorical)

`#6366F1 · #22D3EE · #F97316 · #34D399 · #8B5CF6 · #FBBF24 · #F472B6 · #A3E635`
(Attention-head visualizers and embedding plots use continuous scales: `viridis` for magnitude, indigo↔orange diverging for signed values.)

---

## 4. Typography

| Role | Typeface | Weights | Notes |
|---|---|---|---|
| **Display / headings** | **Space Grotesk** | 500, 700 | Geometric, technical personality; used in wordmark |
| **Body / UI** | **Inter** | 400, 500, 600 | Variable font; `font-feature-settings: "cv11"` for open digits |
| **Code** | **JetBrains Mono** | 400, 700 | Editor, inline code, terminal output; ligatures ON in editor, OFF in prose |
| **Mathematics** | KaTeX default (Computer Modern) | — | Never substitute; math must look like math |

**Type scale (rem, 1.25 ratio):** 0.75 / 0.875 / 1 / 1.25 / 1.5625 / 1.953 / 2.441 / 3.052
**Body:** 1rem/1.65 · **Lesson prose max-width:** 72ch · **Headings:** tracking −0.02em.

---

## 5. Voice & tone

**Personality:** a brilliant professor who still writes code every day. Rigorous, warm, direct,
allergic to hand-waving.

| Principle | Do | Don't |
|---|---|---|
| **Intuition before formalism** | "Attention is a soft dictionary lookup. Now let's prove it." | Open with the equation |
| **Respect the learner** | "This is hard. Here's the path through it." | "It's easy!" / "Simply…" |
| **Precision** | "The gradient *of the loss with respect to* W" | Vague pronouns: "it flows back" |
| **Celebrate building** | "You just implemented backprop. PyTorch does exactly this." | Gamification hype without substance |
| **Errors are data** | "NaN loss? Great — let's read the stack trace together." | Shame or alarm |

**Microcopy examples:** Run button: "Run ▸" · Success: "All tests passed — forged. 🔨" ·
Failure: "2 of 5 tests failed. Want Ember to explain the first one?" · Streak: "Day 14 — the fire's still lit."

---

## 6. Iconography, motion & imagery

- **Icons:** [Lucide](https://lucide.dev) (open-source, consistent 1.5px stroke), 20/24 px grid. Custom icons (tensor, attention-head, anvil) drawn to the same grid and stroke.
- **Motion (Framer Motion):** durations 150 ms (micro) / 250 ms (panel) / 400 ms (page); easing `cubic-bezier(0.22, 1, 0.36, 1)`. Educational animations (e.g., matrix multiply) are **step-controllable, never autoplay-only**, and respect `prefers-reduced-motion`.
- **Imagery:** no stock photos. All visuals are generated diagrams, plots, or 3D scenes (Three.js loss landscapes) in the brand palette on `bg-base`.
- **Diagrams:** Mermaid with a custom theme (indigo nodes, cyan edges, dark background) — defined in Phase 4.

---

## 7. Accessibility commitments

- WCAG 2.1 AA minimum across both themes (verified in CI with axe-core).
- All interactive visualizations keyboard-operable with textual equivalents.
- Color never the sole carrier of meaning (icons + labels accompany all states).
- Reduced-motion and high-contrast modes are first-class.

---

## 8. Asset inventory

| Asset | File | Status |
|---|---|---|
| Horizontal logo | `docs/branding/logo.svg` | ✅ v1 |
| App icon 512 (squircle) | `docs/branding/icon.svg` | ✅ v1 |
| Favicon set (16/32/180/512 PNG + ICO) | generated from `icon.svg` in Phase 5 build | ⬜ |
| Social card (1200×630) | Phase 4 | ⬜ |
| Certificate template | Phase 4 | ⬜ |
| Mermaid theme JSON | Phase 4 | ⬜ |
| Tailwind token file (`tokens.css` / `tailwind.config.ts`) | Phase 5 | ⬜ |
