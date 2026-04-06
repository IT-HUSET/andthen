# Web Development Guidelines

Web-platform-specific standards. For architecture and coding practices, see `DEVELOPMENT-ARCHITECTURE-GUIDELINES.md`. For UI/UX patterns, see `UX-UI-GUIDELINES.md`.


## HTML & Semantics
- Use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`) — not generic `<div>` soup
- Headings in logical order (`<h1>`–`<h6>`). Group related content with semantic containers
- Descriptive `alt` text for images; `alt=""` for purely decorative ones
- Keep content (HTML), presentation (CSS), and behavior (JS) separate


## CSS & Styling
- Styles in external stylesheets, not inline. Use a consistent methodology (BEM, utility-first)
- Modern layout: Flexbox and Grid, not floats or tables
- Mobile-first: start with small screens, enhance with media queries and relative units
- Prefer CSS animations over JS-driven animations. Respect `prefers-reduced-motion`


## JavaScript
- Load scripts with `defer` or `async` to avoid blocking render
- Use ES6+ features (`const`/`let`, arrow functions, modules, async/await)
- Cache DOM references, batch updates, debounce/throttle event handlers
- Clean up event listeners and intervals. Manage state explicitly


## Security
- **HTTPS everywhere**
- Validate and sanitize all inputs — prevent XSS and injection attacks
- Set Content-Security-Policy headers to restrict resource origins
- Secure cookies: `HttpOnly`, `Secure`, `SameSite`
- Never commit secrets (API keys, tokens, credentials). Use `.env` files (gitignored)
- Keep dependencies updated to mitigate known vulnerabilities


## Performance
- Minify CSS/JS. Compress images (prefer WebP/AVIF). Use CDN for static assets
- Lazy-load below-fold images (`loading="lazy"`). Code-split into chunks
- Monitor Core Web Vitals: LCP, INP, CLS
- Use Web Workers for CPU-intensive tasks
