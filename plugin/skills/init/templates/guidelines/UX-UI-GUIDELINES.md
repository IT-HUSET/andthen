# UI/UX Guidelines

## Core Principle
**Users scan, don't read.** Every interface element must be instantly understandable through visual patterns alone.


## The 5 Fundamental Laws

### 1. Don't Make Me Think
Every element should be self-evident within 5 seconds. Use universally recognized icons and patterns. Never create novel interactions that need explanation.

### 2. Visual Hierarchy Rules All
Primary action must be the largest, brightest element. Follow F-pattern (content) or Z-pattern (landing pages). Use size ratios of 3:2:1 for headline:subhead:body. **Test**: squint at screen — if primary action isn't obvious, fix hierarchy.

### 3. Touch/Click Targets Are Sacred

| | Minimum | Preferred | Spacing |
|---|---|---|---|
| Mobile | 44pt × 44pt | 60pt × 60pt | 8pt |
| Desktop | 32px × 32px | 48px × 48px | 8px |

### 4. Feedback Timing

| Duration | Response |
|---|---|
| 0–100ms | None needed (feels instant) |
| 100ms–1s | Spinner or skeleton screen |
| 1–3s | Progress bar with percentage |
| >3s | Time estimate + cancel button |

### 5. Errors Are Design Failures
Prevent errors with constraints (disable invalid actions). Use inline validation on blur. Provide undo for destructive actions. Error format: `[What happened] + [Why] + [How to fix] + [Action button]`


## Visual Standards

### Typography
- Mobile body minimum: 12pt (never smaller); labels on tap targets: 16pt (prevents iOS zoom)
- Desktop body minimum: 14px, ideal: 16px
- Maximum line width: 65ch for readability
- Limit to 3 type sizes per screen

### Color & Contrast
- Regular text: 4.5:1 minimum contrast (WCAG AA)
- Large text (18pt+ or 14pt+ bold): 3:1 minimum
- Interactive elements: 3:1 minimum; hover darkens 10% or adds shadow
- Color must never be the sole indicator — always pair with icons or patterns

### Spacing
Use an 8px base grid. Related items: 8px apart. Unrelated sections: 24px+. Card padding: 16px. Gutters: 16px mobile, 24px desktop.


## Interaction Patterns

### Forms
- Single column layout, label above input, group related fields
- Inline validation on blur with success/error indicators
- Disable submit until valid
- Support autofill, input masks, show/hide password

### Loading States
- **Skeleton screens** for initial page loads (match actual content layout, subtle shimmer)
- **Spinners** for user-initiated actions (centered, descriptive text after 3s)
- **Progress bars** for uploads/downloads (percentage, time remaining, cancel button)

### Micro-interactions
- Hover: `pointer` cursor, subtle `scale(1.02)` or `translateY(-2px)`, 200ms ease-out
- Active: `scale(0.98)`, slightly darker, instant feedback
- Focus: 2px outline with 2px offset, high contrast — never remove focus indicators


## Mobile-First Design

### Thumb Zone Placement
- **Bottom 60%** (easy reach): primary actions, navigation tabs, frequent features
- **Top 20%** (hard reach): destructive actions, rarely used settings, status-only info

### Standard Gestures
Swipe-right: back. Swipe-down: refresh. Swipe-left: delete. Pinch: zoom. Long-press: context menu. Always provide a UI alternative for every gesture.

### Responsive Breakpoints

| Range | Layout |
|---|---|
| 320–767px | Single column (mobile) |
| 768–1023px | 2 columns max (tablet) |
| 1024–1439px | Multi-column (desktop) |
| 1440px+ | Centered, max-width 1280px |

For platform-specific patterns (iOS HIG, Material Design), consult the platform's current documentation.


## Accessibility Essentials

- All text: 4.5:1 contrast minimum. Focus indicators on every interactive element
- Tab order matches visual hierarchy. No keyboard traps. Skip links for repetitive content
- Semantic HTML with proper headings and landmarks. ARIA labels for icon-only buttons
- Form inputs properly labeled. Error messages associated with fields
- Touch targets ≥ 44pt with ≥ 8pt spacing
- Animations pausable/disableable. No flashing above 3Hz
- Dynamic content announces changes to screen readers


## Animation Performance
- Target 60fps (16ms per frame). Use only `transform` and `opacity` — avoid layout triggers
- Micro: 100–200ms. Standard: 200–300ms. Complex: 300–500ms


## Validation Checklist

Before marking UI work complete:
- [ ] Primary action identifiable in 5 seconds
- [ ] All touch targets ≥ 44pt with proper spacing
- [ ] Loading states for all async operations
- [ ] Error messages helpful and actionable
- [ ] Keyboard fully navigable
- [ ] Color contrast passes WCAG AA
- [ ] Responsive across all target breakpoints
- [ ] Platform conventions followed

**The best interface is invisible — users achieve their goals without noticing the UI.**
