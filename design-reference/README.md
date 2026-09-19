# NCERT Study Companion — Design Reference Prototypes

**Phase 0 Visual Design Reference**
Created: 2026-09-12

## Purpose

These HTML/CSS prototypes serve as the **visual source of truth** for the NCERT Study Companion product redesign. They establish the exact visual language, spacing, typography, colors, and component hierarchy before implementation begins.

## Files

### Desktop Prototypes

**`desktop.html`** — Active conversation state
- Shows a complete conversation flow
- User message + AI response with sources
- Full sidebar navigation
- Composer at bottom
- Realistic NCERT content

**`desktop-empty.html`** — Empty/welcome state
- First-time user experience
- Suggested questions treatment
- Calm, focused empty state
- Composer prominence

### Mobile Prototype

**`mobile.html`** — Mobile conversation view
- 390×844 mobile viewport with device frame
- Compact header with menu
- Horizontal scrolling subject pills
- Touch-optimized conversation
- Mobile composer with safe-area spacing

## How to Use

### 1. View in Browser

Open each HTML file in a modern browser (Chrome, Safari, Firefox, Edge):

```bash
# Windows
start desktop.html
start desktop-empty.html
start mobile.html

# Mac
open desktop.html
open desktop-empty.html
open mobile.html

# Linux
xdg-open desktop.html
```

### 2. Screenshot for Reference

Take screenshots of each rendered view to use as implementation reference images.

### 3. Extract Design Tokens

All design tokens are defined in CSS custom properties at the top of each file:

```css
:root {
  --bg-canvas: #0A0A0B;
  --bg-surface: #18181B;
  --accent-primary: #10B981;
  /* ... */
}
```

### 4. Validate Visual Quality

Before proceeding to implementation, verify:

- ✅ Looks like a real premium product
- ✅ Does NOT look like a generic AI chatbot
- ✅ Does NOT look like a SaaS dashboard
- ✅ Does NOT look like Streamlit
- ✅ Conversation is clearly the hero
- ✅ Typography creates clear hierarchy
- ✅ NCERT identity is distinctive
- ✅ Sources feel trustworthy, not technical
- ✅ Interface has visual restraint
- ✅ Premium feel without gimmicks

## Design System Summary

### Colors

**Foundation (Dark Academic)**
- Canvas: `#0A0A0B` (near-black, warm)
- Surface: `#18181B` (elevated elements)
- Elevated: `#1F1F23` (user messages)
- Borders: `#2A2A2E` (subtle), `#3F3F46` (default)

**Text Hierarchy**
- Primary: `#F4F4F5` (high contrast)
- Secondary: `#A1A1AA` (supporting text)
- Muted: `#71717A` (metadata)

**Accent (Emerald Academic)**
- Primary: `#10B981` (emerald-500)
- Hover: `#34D399` (emerald-400)
- Subtle: `rgba(16, 185, 129, 0.1)` (backgrounds)
- Border: `rgba(16, 185, 129, 0.3)` (selected states)

### Typography

**Font Stack**
- Sans: Inter (via Google Fonts)
- Fallback: System fonts

**Scale**
- 11px: Labels (uppercase)
- 12px: Metadata, sources, timestamps
- 13px: Mobile pills
- 14px: UI elements, buttons, pills
- 15px: Input, mobile body, subtitle
- 16px: Message body (desktop)
- 24px: Empty state title
- 28px: Display/brand (if needed)

**Line Heights**
- 1.3: Compact (logo text)
- 1.5: Normal (UI, user messages)
- 1.6: Relaxed (mobile messages)
- 1.7: Editorial (AI responses)

### Spacing

- 4px: Micro (icon gaps)
- 8px: Small (between elements)
- 12px: Medium (padding, gaps)
- 16px: Base (standard padding)
- 20px: Large (message padding)
- 24px: Section (between messages on mobile)
- 32px: XL (between messages on desktop)

### Layout

**Desktop**
- Sidebar: 260px fixed
- Content max-width: 720px
- Total frame: 1440×900

**Mobile**
- Viewport: 390×844
- Full-width messages
- 16px horizontal padding
- Safe-area bottom padding

### Components

**Buttons**
- Border-radius: 8px (standard), 20px (pills)
- Padding: 8-12px vertical, 16-20px horizontal
- Hover: Subtle background shift
- Active: scale(0.95)

**Messages**
- User: Elevated background, subtle border
- Assistant: Surface background, emerald left border
- Border-radius: 12px
- Padding: 16-20px

**Composer**
- Border-radius: 12px
- Min-height: 52px (desktop), 44px (mobile)
- Focus: Emerald border
- Send button: 36×36px (desktop), 32×32px (mobile)

## Key Design Decisions

### 1. Single Premium Sans-Serif
Using Inter (via CDN) for all typography. No serif needed — hierarchy achieved through weight, size, and spacing.

### 2. Emerald Academic Accent
Chosen over blue (corporate), purple (AI cliché), or orange (too playful). Emerald conveys: academic, trustworthy, natural, distinctive.

### 3. Open Canvas, Not Card Grid
Assistant responses are elevated surfaces with subtle left accent, NOT heavy card containers. Emphasis on editorial reading experience.

### 4. Restrained Sidebar (260px)
Slightly wider than initial 240px spec to give breathing room. Contains only: logo, new chat, subject selector. No metrics, no tech stack.

### 5. Lightweight Suggested Questions
Text rows with subtle arrow prefix and hover states. No cards, no emojis, no heavy borders. Calm and premium.

### 6. Sources as Attribution, Not Metadata
Clear Subject > Chapter > Section hierarchy. No FAISS scores, no chunk IDs, no technical details. Feels like curriculum reference.

### 7. Composer as Hero
Fixed bottom position, clear focus state, prominent send button. Designed to feel like the primary interaction point.

### 8. Mobile: Horizontal Subject Pills
Scrolling pills preserve desktop pattern but adapt to narrow viewport. Touch targets 44px minimum.

## What Changed from Initial Spec

### Color Refinements
- Slightly warmer blacks (`#0A0A0B` instead of `#09090B`)
- Added distinct elevated surface (`#1F1F23`) for user messages
- Refined border colors for better visual hierarchy

### Typography
- Confirmed single sans-serif (Inter via CDN, later Geist Sans in production)
- Adjusted sizes based on visual rendering
- 16px body for desktop, 15px for mobile

### Layout
- Sidebar: 260px (was 240px) — tested visually, feels better
- Content max-width: 720px (confirmed from spec)
- Mobile header: 44px top padding for notch

### Components
- Assistant responses: Open surface with left accent, not full card
- Suggested questions: Text rows, not cards
- Subject pills: Vertical stack (desktop), horizontal scroll (mobile)

## Quality Gate — Visual Inspection Results

### ✅ Approved Characteristics

1. **Premium Feel** — Typography and spacing create quality, not effects
2. **Distinctive Identity** — Emerald accent + NCERT branding recognizable
3. **Conversation-First** — Chat occupies 80%+ of screen
4. **Academic Credibility** — Sources feel educational, not technical
5. **Not Generic AI** — No purple, no cyan glow, no AI aesthetics
6. **Not SaaS Dashboard** — No metrics, no analytics, no tech showcase
7. **Not Streamlit** — Custom design system, polished interactions
8. **Restrained Sidebar** — Minimal, functional, no clutter
9. **Calm Empty State** — Lightweight suggestions, focused on composer
10. **Mobile-Native** — Genuine mobile adaptation, not shrunk desktop

## Next Steps

### Phase 0 Approval Gate
1. Open prototypes in browser
2. Review rendered visuals
3. Validate against quality bar
4. Approve design direction

### After Approval → Phase 1
1. Create FastAPI backend wrapper
2. Implement streaming endpoint
3. Test API independently

### Phase 3 (Frontend)
1. Translate these exact visuals to Next.js components
2. Use design tokens from CSS custom properties
3. Match spacing, colors, typography exactly
4. Preserve visual hierarchy

## Important Notes

⚠️ **These are design prototypes ONLY**

- Do NOT use this HTML in production
- Do NOT modify app.py based on these files
- Do NOT modify rag_engine.py
- Do NOT install Next.js dependencies yet
- Do NOT commit these to the main codebase

✅ **These ARE the source of truth for:**

- Visual design direction
- Color palette
- Typography hierarchy
- Component styling
- Spacing system
- Layout proportions
- Interaction patterns

---

**Status: Awaiting Phase 0 approval before proceeding to Phase 1 (Backend API)**
