# UI/UX Review Checklist

Concise, actionable checklist for UI/UX reviews and validation.

---

## Pre-Review
- [ ] Identify screens/components to review
- [ ] Capture screenshots across target devices and orientations (mobile, tablet, desktop)
- [ ] Capture all relevant states (idle, active, loading, error, empty)
- [ ] Compare against design specs/baseline if available

---

## Visual Quality & Layout

### Layout Integrity
- [ ] No overlapping elements or broken layouts
- [ ] Consistent spacing follows 8px grid system
- [ ] Proper alignment (left/center/right justification)
- [ ] Respects safe areas (notch, system bars, navigation)
- [ ] Visual stability (no unexpected shifts during interactions)

### Typography
- [ ] Minimum sizes met (12pt mobile, 14px desktop)
- [ ] Clear hierarchy (max 3 sizes per screen)
- [ ] No text truncation blocking functionality
- [ ] Line height appropriate (1.2 headers, 1.5 body)
- [ ] Readable content width (≤65ch)

### Color & Contrast
- [ ] Text contrast ≥4.5:1 (WCAG AA)
- [ ] Large text contrast ≥3:1 (18pt+ or 14pt+ bold)
- [ ] Interactive elements contrast ≥3:1
- [ ] Color not sole indicator (icons/patterns used)
- [ ] Status colors correct (red=error, green=success, yellow=warning)

### Responsive Behavior
- [ ] Content reflows gracefully at all breakpoints
- [ ] Mobile: 320-767px (single column)
- [ ] Tablet: 768-1023px (2 columns max)
- [ ] Desktop: 1024px+ (multi-column)
- [ ] Images scale appropriately
- [ ] No horizontal scroll (unless intentional)

## Usability Excellence

### 5-Second Clarity Test
- [ ] Screen purpose obvious within 5 seconds
- [ ] Primary action immediately identifiable
- [ ] Current location clear (breadcrumbs, active nav)
- [ ] Visual hierarchy guides attention correctly

### Touch/Click Targets
- [ ] Mobile minimum: 44pt × 44pt
- [ ] Desktop minimum: 32px × 32px
- [ ] Primary actions: 60pt/48px preferred
- [ ] Spacing between targets: ≥8pt/px
- [ ] Thumb-zone optimization (primary actions in bottom 60%)

### Cognitive Load
- [ ] ≤7 simultaneous choices per screen
- [ ] Clear visual hierarchy reduces mental effort
- [ ] Related items grouped with whitespace
- [ ] Progressive disclosure for complex features
- [ ] No "mystery meat" navigation (labels clear)

### Task Efficiency
- [ ] Primary flows achievable in ≤3 taps/clicks
- [ ] Minimal scrolling for core actions
- [ ] Smart defaults and auto-fill where possible
- [ ] Clear path to task completion
- [ ] No unnecessary steps or friction

### Error Prevention & Recovery
- [ ] Clear defaults prevent common errors
- [ ] Inline validation as user types
- [ ] Constraints disable invalid actions
- [ ] Undo available for destructive actions
- [ ] Recovery paths obvious and easy

### System Feedback
- [ ] Immediate response to all interactions (<100ms visual)
- [ ] Loading states for 100ms-1s (spinner/skeleton)
- [ ] Progress bars for 1-3s operations
- [ ] Time estimates + cancel for >3s operations
- [ ] Success/error messages clear and actionable

## Platform Conventions

### iOS (HIG Compliance)
- [ ] Tab bar at bottom (≤5 items)
- [ ] Back button top-left or swipe-right
- [ ] Primary action top-right
- [ ] Action sheets slide from bottom
- [ ] Respects safe areas (notch, home indicator)
- [ ] Uses SF Symbols or platform-appropriate icons

### Android (Material Design)
- [ ] Bottom navigation or drawer
- [ ] Back button in app bar (top-left)
- [ ] FAB for primary action (bottom-right)
- [ ] Bottom sheets for actions
- [ ] Ripple effect on taps
- [ ] Material Icons used

### Web
- [ ] Logo top-left links to home
- [ ] Horizontal menu (desktop) or hamburger (mobile)
- [ ] Sticky header for long pages
- [ ] Footer for secondary links
- [ ] Standard web conventions followed

## Interaction Patterns

### Forms
- [ ] One column layout
- [ ] Labels above inputs
- [ ] Inline validation on blur
- [ ] Success indicators (green check)
- [ ] Errors below field with solution
- [ ] Auto-capitalize, input masks, autofill supported
- [ ] Submit disabled until valid

### Loading States
- [ ] Skeleton screens for initial loads (match content placement)
- [ ] Spinners for actions (centered, with text if >3s)
- [ ] Progress bars for uploads/downloads (%, time, cancel)
- [ ] Smooth transitions (no jarring appearance)

### Micro-interactions
- [ ] Hover states: cursor pointer, scale/translateY, 200ms transition
- [ ] Active states: scale(0.98), darker background
- [ ] Focus states: 2px outline, high contrast, never removed
- [ ] Animations: 100-200ms micro, 200-300ms standard, 60fps

### Gestures (Mobile)
- [ ] Swipe-right: back
- [ ] Swipe-down: refresh
- [ ] Swipe-left: delete
- [ ] Long-press: context menu
- [ ] UI alternative always provided

## Accessibility (WCAG 2.2)

### Visual
- [ ] All text ≥4.5:1 contrast
- [ ] Focus indicators visible on all interactive elements
- [ ] Color never sole indicator
- [ ] All images have descriptive alt text
- [ ] Text readable at 200% zoom

### Keyboard Navigation
- [ ] Tab order matches visual hierarchy
- [ ] All interactive elements keyboard accessible
- [ ] No keyboard traps
- [ ] Skip links for repetitive content
- [ ] Keyboard shortcuts documented

### Screen Reader
- [ ] Semantic HTML (proper headings, landmarks)
- [ ] ARIA labels for icon-only buttons
- [ ] Form inputs properly labeled
- [ ] Error messages associated with fields
- [ ] Dynamic content announces changes

### Interaction
- [ ] Touch targets meet minimums
- [ ] Sufficient spacing between targets
- [ ] Time limits adjustable/removable
- [ ] Animations can be paused/disabled
- [ ] No flashing >3Hz

## Performance

### Speed
- [ ] First Paint: <1 second
- [ ] Interactive: <3 seconds
- [ ] Complete Load: <5 seconds
- [ ] Images lazy-loaded below fold
- [ ] Images compressed (WebP preferred)

### Animation Performance
- [ ] 60fps minimum (16ms per frame)
- [ ] Uses transform/opacity only
- [ ] No layout-triggering properties
- [ ] Hardware acceleration for complex animations
- [ ] Durations appropriate (100-500ms)

## Quality Tests

### The 5-Second Test
Show screen for 5 seconds, verify:
- [ ] User knows what screen is for
- [ ] User knows what they can do
- [ ] User knows what to click first
- [ ] User knows where they are in app

### The Thumb Test (Mobile)
Hold phone in one hand:
- [ ] Can reach primary action with thumb
- [ ] Can complete main task one-handed
- [ ] Destructive actions out of accidental reach
- [ ] Can navigate back easily

### The Grandmother Test
Non-technical user can:
- [ ] Understand what to do without instructions
- [ ] Recover from mistakes
- [ ] Understand what each button does
- [ ] Get help if stuck

---

## Issue Classification

### 🔴 IMMEDIATE (Blocks Release)
- Text truncation preventing task completion
- Elements outside safe areas
- Touch targets below minimum (44pt/32px)
- Broken layouts blocking functionality
- Critical accessibility violations (contrast, keyboard traps)
- No loading feedback for >100ms operations
- Technical error messages shown to users

### ⚠️ HIGH PRIORITY (Fix Soon)
- Inconsistent spacing affecting hierarchy
- Minor alignment issues
- Suboptimal task paths (>3 steps)
- Missing state feedback
- Performance issues (>3s load)
- Minor accessibility issues
- Primary action not obvious within 5 seconds

### 💡 ENHANCEMENT (Nice to Have)
- Minor visual refinements
- Micro-interaction improvements
- Advanced accessibility features
- Animation polish
- Gestural enhancements
