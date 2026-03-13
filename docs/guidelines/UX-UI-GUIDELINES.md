# UI/UX Implementation Guidelines

## Core Principle
**Users scan, don't read** - Every interface element must be instantly understandable through visual patterns alone.

## The 5 Fundamental Laws

### 1. **Don't Make Me Think** (Krug's Law)
- ✅ **DO**: Make every element self-evident within 5 seconds
- ✅ **DO**: Use universally recognized icons and patterns
- ❌ **DON'T**: Create novel interactions that need explanation
- **TEST**: Show screen to someone for 5 seconds - can they identify the primary action?

### 2. **Visual Hierarchy Rules All**
- ✅ **DO**: Make primary action largest and brightest element on screen
- ✅ **DO**: Follow F-pattern (content) or Z-pattern (landing pages) for layout
- ✅ **DO**: Use size ratios of 3:2:1 for headline:subhead:body text
- ❌ **DON'T**: Make all elements same size/weight
- **TEST**: Squint at screen - if primary action isn't obvious, fix hierarchy

### 3. **Touch/Click Targets Are Sacred**
```yaml
Mobile:
  minimum: 44pt × 44pt
  preferred: 60pt × 60pt (primary actions)
  spacing: 8pt between targets

Desktop:
  minimum: 32px × 32px
  preferred: 48px × 48px (primary actions)
  spacing: 8px between targets
```
- **TEST**: Can you tap accurately with your thumb while walking?

### 4. **Feedback Is Instant**
```yaml
0-100ms:    No indicator needed (feels instant)
100ms-1s:   Show spinner or skeleton screen
1-3s:       Show progress bar with percentage
>3s:        Add time estimate + cancel button
```
- ✅ **DO**: Provide immediate visual response to every interaction
- ❌ **DON'T**: Leave users wondering if their action registered

### 5. **Errors Are Design Failures**
- ✅ **DO**: Prevent errors with constraints (e.g., disable invalid actions)
- ✅ **DO**: Use inline validation on forms as user types
- ✅ **DO**: Provide undo for all destructive actions
- ❌ **DON'T**: Show technical error messages or blame users
- **FORMAT**: `[What happened] + [Why] + [How to fix] + [Action button]`

## Design System Implementation

### Component Architecture (Atomic Design)
```yaml
Atoms:       # Basic building blocks
  - Buttons, Icons, Input fields, Labels
  - Define once, reuse everywhere

Molecules:   # Simple combinations
  - Form fields (label + input + error)
  - Cards (image + text + button)

Organisms:   # Complex sections
  - Navigation bars, Forms, Hero sections
  - Combine molecules with consistent spacing

Templates:   # Page structures
  - Define grid and layout patterns
  - Ensure responsive behavior
```

### Design Tokens (Single Source of Truth)
```yaml
Colors:
  primary:      # Main brand color
  secondary:    # Accent color
  danger:       #ef4444  # Always red
  success:      #10b981  # Always green
  warning:      #f59e0b  # Always yellow
  neutral-100:  #f5f5f5  # Lightest gray
  neutral-500:  #737373  # Mid gray
  neutral-900:  #171717  # Darkest gray

Spacing:      # Use 8px grid system
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px

Typography:
  size-xs:  12px  # Minimum for mobile
  size-sm:  14px  # Minimum for desktop
  size-md:  16px  # Body text
  size-lg:  20px  # Subheadings
  size-xl:  24px  # Headings
  size-2xl: 32px  # Hero text

  line-height-tight: 1.2   # Headers
  line-height-base:  1.5   # Body text
  line-height-loose: 1.75  # Readable paragraphs
```

### Component Naming Convention
```yaml
Structure:    [type]-[variant]-[state]
Examples:
  - button-primary-active
  - input-error-focused
  - card-product-hover
```

## Visual Design Rules

### Typography Implementation
```yaml
Mobile:
  body-min:    12pt (never smaller)
  body-ideal:  14pt
  tap-labels:  16pt (prevent zoom on iOS)

Desktop:
  body-min:    14px
  body-ideal:  16px

Universal:
  max-width:   65ch (optimal reading)
  hierarchy:   3 sizes maximum per screen
```

### Color & Contrast
```yaml
Text:
  regular:     4.5:1 minimum contrast (WCAG AA)
  large:       3:1 minimum (18pt+ or 14pt+ bold)

Interactive:
  buttons:     3:1 minimum contrast
  hover:       Darken by 10% or add shadow
  disabled:    40% opacity

Status:
  error:       Red (#ef4444) + error icon
  success:     Green (#10b981) + checkmark
  warning:     Yellow (#f59e0b) + warning icon
  info:        Blue (#3b82f6) + info icon
```

### Spacing & Layout
```yaml
Grid:        8px base unit everywhere
Gutters:     16px minimum (mobile), 24px (desktop)
Margins:     Equal top/bottom for balance

Related:     8px between related items
Unrelated:   24px+ between sections
Cards:       16px internal padding
```

## Platform-Specific Implementation

### iOS (Follow HIG)
```yaml
Navigation:
  - Tab bar at bottom (5 items max)
  - Back button top-left or swipe-right
  - Primary action top-right

Components:
  - Action sheets slide from bottom
  - Modals: full screen or page sheet
  - Use SF Symbols for icons
  - Respect safe areas (notch/home indicator)
```

### Android (Follow Material Design)
```yaml
Navigation:
  - Bottom navigation or navigation drawer
  - Back button in app bar (top-left)
  - FAB for primary action (bottom-right)

Components:
  - Bottom sheets for actions
  - Snackbars for brief messages (3-10s)
  - Use Material Icons
  - Ripple effect on all taps
```

### Web Responsive
```yaml
Breakpoints:
  mobile:     320-767px   (single column)
  tablet:     768-1023px  (2 columns max)
  desktop:    1024-1439px (multi-column)
  wide:       1440px+     (max-width: 1280px centered)

Navigation:
  - Logo top-left → home
  - Horizontal menu (desktop) or hamburger (mobile)
  - Sticky header for long pages
  - Footer for secondary links
```

## Interaction Patterns

### Form Design
```yaml
Structure:
  - One column layout (faster completion)
  - Label above input (better scanning)
  - Group related fields with spacing

Validation:
  - Inline validation on blur
  - Success indicators (green check)
  - Error below field with solution
  - Disable submit until valid

Input Enhancement:
  - Auto-capitalize names/addresses
  - Input masks for phones/dates
  - Show password toggle
  - Autofill support
```

### Loading States
```yaml
Skeleton Screens:   # For initial page loads
  - Show layout structure
  - Animate subtle shimmer
  - Match actual content placement

Spinners:          # For actions
  - Centered in action area
  - With descriptive text for >3s

Progress Bars:     # For file uploads/downloads
  - Show percentage
  - Time remaining if calculable
  - Cancel button always visible
```

### Micro-interactions
```yaml
Hover States:
  - Cursor: pointer for clickable
  - Transform: scale(1.02) or translateY(-2px)
  - Transition: 200ms ease-out

Active States:
  - Transform: scale(0.98)
  - Slightly darker background
  - Instant feedback (no delay)

Focus States:
  - 2px outline offset 2px
  - High contrast color
  - Never remove, only style
```

## Mobile-First Requirements

### Touch Optimization
```yaml
Thumb Zone Map:
  green:   Easy reach (bottom 60%)
  yellow:  Stretch (middle 20%)
  red:     Hard (top 20%)

Place in Green Zone:
  - Primary actions
  - Navigation tabs
  - Frequently used features

Place in Red Zone:
  - Destructive actions (delete)
  - Rarely used settings
  - Status information only
```

### Gesture Support
```yaml
Standard Gestures:
  swipe-right:     Go back
  swipe-down:      Refresh (lists)
  swipe-left:      Delete (list items)
  pinch:           Zoom images/maps
  long-press:      Context menu

Implementation:
  - Always provide UI alternative
  - Add visual hints for discovery
  - Respect platform conventions
```

## Accessibility Checklist

### Visual Accessibility
- [ ] All text has 4.5:1 contrast minimum
- [ ] Focus indicators visible on all interactive elements
- [ ] Color never sole indicator (add icons/patterns)
- [ ] All images have descriptive alt text
- [ ] Text remains readable at 200% zoom

### Keyboard Navigation
- [ ] Tab order matches visual hierarchy
- [ ] All interactive elements keyboard accessible
- [ ] No keyboard traps (can always escape)
- [ ] Skip links for repetitive content
- [ ] Keyboard shortcuts documented

### Screen Reader Support
- [ ] Semantic HTML (proper headings, landmarks)
- [ ] ARIA labels for icon-only buttons
- [ ] Form inputs properly labeled
- [ ] Error messages associated with fields
- [ ] Dynamic content announces changes

### Interaction Accessibility
- [ ] Touch targets meet minimums (44pt)
- [ ] Sufficient spacing between targets (8pt)
- [ ] Time limits adjustable or removable
- [ ] Animations can be paused/disabled
- [ ] No seizure-inducing flashing (less than 3Hz)

## Performance Requirements

### Speed Targets
```yaml
Critical Metrics:
  First Paint:        < 1 second
  Interactive:        < 3 seconds
  Complete Load:      < 5 seconds

Optimization:
  - Lazy load below-fold images
  - Compress all images (WebP preferred)
  - Minify CSS/JS
  - Enable caching headers
  - Use CDN for static assets
```

### Animation Performance
```yaml
Requirements:
  - 60fps minimum (16ms per frame)
  - Use transform/opacity only
  - Avoid layout triggers
  - Hardware acceleration for complex animations

Duration:
  micro:    100-200ms (hover, focus)
  standard: 200-300ms (page transitions)
  complex:  300-500ms (elaborate reveals)
```

## Quality Assurance Tests

### The 5-Second Test
```bash
# Show screen for 5 seconds, then ask:
✓ What is this screen for?
✓ What can you do here?
✓ What should you click first?
✓ Where are you in the app?
# Pass rate should be >90%
```

### The Thumb Test (Mobile)
```bash
# Hold phone in one hand:
✓ Can reach primary action with thumb?
✓ Can complete main task one-handed?
✓ Destructive actions out of accidental reach?
✓ Can navigate back easily?
```

### The Grandmother Test
```bash
# Would a non-technical user understand:
✓ What to do without instructions?
✓ How to recover from mistakes?
✓ What each button does?
✓ How to get help if stuck?
```

## Common Pitfalls to Avoid

### Critical Failures (Fix Immediately)
```yaml
🚨 Touch targets < 44pt:
   FIX: Increase to minimum 44pt × 44pt

🚨 Text < 12pt effective size:
   FIX: Increase to 12pt mobile, 14px desktop minimum

🚨 No loading feedback after 100ms:
   FIX: Add spinner or skeleton screen

🚨 Technical error messages:
   FIX: "Something went wrong. Please try again."

🚨 Hidden primary action:
   FIX: Make largest, brightest element

🚨 Form without validation:
   FIX: Add inline validation on blur

🚨 No undo for destructive actions:
   FIX: Add confirmation or undo option

🚨 Mystery meat navigation:
   FIX: Use standard patterns and labels
```

## Implementation Priority Matrix

### 🔴 Critical (Before Launch)
1. **Visual Hierarchy**: Primary action obvious within 5 seconds
2. **Touch Targets**: All meet 44pt minimum with 8pt spacing
3. **Feedback**: Every interaction has immediate response
4. **Error Handling**: Validation, prevention, and recovery
5. **Mobile Response**: Works on smallest supported device

### 🟡 Important (Week 1)
1. **Loading States**: Skeleton screens and progress indicators
2. **Consistency**: Design system applied throughout
3. **Keyboard Nav**: Full keyboard accessibility
4. **Contrast**: WCAG AA compliance (4.5:1)
5. **Animations**: Smooth transitions at 60fps

### 🟢 Enhancement (Month 1)
1. **Micro-interactions**: Delight without distraction
2. **Gestures**: Platform-specific enhancements
3. **Offline**: Graceful degradation
4. **Personalization**: User preferences
5. **Polish**: Refined animations and transitions

## Success Metrics

### Quantitative Targets
```yaml
Task Completion:    > 90% success rate
Error Rate:         < 5% on critical paths
Time to Action:     < 10 seconds for new users
Load Performance:   < 3 seconds average
Accessibility:      100% WCAG AA compliant
```

### Qualitative Indicators
- Users complete tasks without help documentation
- Navigation feels intuitive without training
- Errors are rare and easily recoverable
- Interface feels fast and responsive
- Experience is consistent across platforms

## Final Validation

Before marking any UI task complete, verify:

```checklist
□ Primary action identifiable in 5 seconds
□ All touch targets ≥ 44pt with proper spacing
□ Loading states for all async operations
□ Error messages helpful and actionable
□ Keyboard fully navigable
□ Color contrast passes WCAG AA
□ Mobile-first responsive design
□ Platform conventions followed
□ Performance targets met
□ Accessibility checklist complete
```

**Remember**: The best interface is invisible - users achieve their goals without noticing the UI.

---

*For AI Implementation: Follow these guidelines exactly. When in doubt, prioritize clarity and usability over aesthetics. Test each implementation against the validation checklist before completion.*