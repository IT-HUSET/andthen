# Web Development Guidelines

These guidelines apply to any web project that uses a browser for its UI (static sites, single-page applications, or server-rendered apps). They focus on core web standards (HTML, CSS, JS) and best practices, without framework-specific details. Follow these principles to build accessible, maintainable, and efficient web applications.

> **Note:** For detailed UI/UX specifications (touch targets, visual hierarchy, interaction patterns, accessibility checklists), see `UX-UI-GUIDELINES.md`.

## HTML and Semantics

- **Use semantic HTML:** Structure content with appropriate HTML5 elements (e.g. use `<header>`, `<nav>`, `<main>`, `<article>`, `<section>` for layout, and headings `<h1>`–`<h6>` for titles).
- **Provide text alternatives:** Always include descriptive **`alt` text for images**, or use empty `alt=""` for purely decorative images.
- **Organize content logically:** Use headings in a logical order and group related content with semantic containers.
- **Separation of concerns:** Keep content (HTML), presentation (CSS), and behavior (JS) separate.
- **Validate and adhere to standards:** Write clean, standards-compliant markup. Use tools like the W3C validator.

## CSS and Styling

- **Keep styles in CSS:** Maintain style rules in external stylesheets, not inline.
- **Consistent CSS architecture:** Use a naming convention (BEM, utility-first) for maintainability.
- **Modern layout techniques:** Use Flexbox and Grid instead of floats/tables.
- **Responsive design:** Develop mobile-first, use relative units and media queries.
- **Cross-browser compatibility:** Test in multiple browsers, use progressive enhancement and fallbacks.
- **Accessible design:** Ensure color contrast, respect user zoom, and prefer CSS animations.

## JavaScript and Behavior

- **Unobtrusive scripting:** Keep JS separate from HTML, use `defer/async` to avoid blocking.
- **Use modern JS features:** Prefer ES6+ (`let`, `const`, arrow functions, modules).
- **Minimize global scope usage:** Encapsulate code, avoid global variables.
- **Efficient DOM interaction:** Cache elements, batch updates, debounce/throttle events.
- **Async and compatibility:** Use Promises/`async`–`await`, provide fallbacks/polyfills.
- **Client-side state:** Use storage carefully, manage state cleanly, clean up listeners.

## Responsive Design and Compatibility

- **Mobile-first layouts:** Start with small screens, enhance for larger.
- **Flexible media and typography:** Use `srcset`, relative units, test orientations.
- **Cross-browser testing:** Verify on Chrome, Firefox, Safari, Edge, mobile.
- **Progressive enhancement:** Core functionality works everywhere, enhance where supported.

## Accessibility

- **Follow WCAG guidelines:** Semantic HTML, alt text, keyboard support.
- **Keyboard navigation:** Ensure focus visibility, logical tab order.
- **Use ARIA appropriately:** Only when native HTML isn’t enough.
- **Provide captions/alternatives:** For media and non-text content.
- **Test accessibility:** Use tools (axe, WAVE), try screen readers/keyboard-only.

## Performance Optimization

- **Optimize assets:** Minify CSS/JS, compress images, use modern formats.
- **Caching and CDNs:** Cache static assets, serve via CDN.
- **Lazy load:** Use `loading="lazy"`, split code into chunks.
- **Efficient code:** Avoid blocking JS, use Web Workers for heavy tasks.
- **Monitor metrics:** Track Core Web Vitals (LCP, INP, CLS).

## Security Best Practices

- **Use HTTPS everywhere.**
- **Validate and sanitize inputs:** Prevent XSS, SQLi.
- **Content Security Policy:** Restrict resource origins.
- **Secure cookies:** Use HttpOnly, Secure, SameSite.
- **Keep dependencies updated.**
- **Secrets management:** Never commit API keys, tokens, or credentials. Use environment variables and `.env` files (gitignored). Never log sensitive data.

## Reusability and Component Design

- **Component-based UI:** Reuse self-contained components.
- **Atomic Design:** Atoms → Molecules → Organisms → Templates → Pages.
- **Consistency:** Use shared design tokens/themes.
- **Document components:** Provide usage guidelines.

## Code Quality and Testing

- **Clean, readable code:** Use consistent style guides, meaningful names.
- **Modularity and DRY:** Reuse logic, avoid repetition.
- **Comments and docs:** Explain “why”, not obvious “what”.
- **Version control:** Use git, write clear commit messages.
- **Testing:** Add unit and end-to-end tests, test across devices.
- **Continuous improvement:** Review code, refactor when needed.

---
By following these guidelines, you build web projects that are accessible, performant, secure, and maintainable.
