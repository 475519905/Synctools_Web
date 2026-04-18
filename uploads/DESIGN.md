# Design System Inspiration of SyncTools

## 1. Visual Theme & Atmosphere

SyncTools (`synctools.cn`) is a Chinese-market product site for a cross-platform 3D workflow conversion tool — a bridge between Cinema 4D, Blender, Maya, 3ds Max and other DCC applications that synchronizes geometry, animation, materials, and lighting between them. The site is built as a dark, cinematic product showcase that positions a technical developer utility with the polish of a consumer hardware launch page. Full-viewport black canvases, extreme-scale display typography, frosted-glass feature cards, and a single vibrant purple→indigo gradient accent give the product the visual weight of a flagship release rather than a utility.

The palette is overwhelmingly near-black. Layered dark gradients (`linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #050505 100%)`) carry every section, punctuated by pure white text, a soft indigo brand gradient (`#667eea → #764ba2`) reserved for emphasis and decorative moments, and an icy blue display gradient (`#ffffff → #64b5f6`) used on the version title. An almost-invisible PNG noise overlay (`opacity: 0.02`) sits across the whole page, softening gradients and giving the darkness a filmic grain. Animated grid backgrounds, floating particle dots, character-by-character typewriter headlines, and scroll-triggered fade-ups give the static interface a constant, low-key motion layer.

Typography leans into extreme contrast. The hero headline is set at **12.5rem / weight 900 / letter-spacing −2px** — a billboard-scale wordmark that behaves more like a logo lockup than a sentence. Everything below drops dramatically to a responsive body scale (`clamp(15px, 1.4vw, 16px)`) set in the default system sans-serif stack, with Chinese copy ("转换一切，从未如此简单") rendered without a dedicated CJK face — relying on the OS fallback. The effect is a highly compressed hierarchy: one giant wordmark, then calm, quiet functional text.

**Key Characteristics:**
- Dark-dominant canvas: layered black gradients (`#0a0a0a` → `#000000` → `#050505`) carry 95%+ of surfaces
- Extreme display typography: hero headline at `12.5rem` / weight `900` / letter-spacing `−2px`
- Inverted CTA logic: primary buttons are **white with black text** (not brand-colored), pill-shaped at `border-radius: 9999px`
- Single decorative gradient: purple→indigo `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` reserved for accent moments
- Display gradient: `linear-gradient(135deg, #ffffff 0%, #64b5f6 100%)` for version titles
- Frosted-glass feature cards: `rgba(255,255,255,0.02)` + `backdrop-filter: blur(10px)` + hairline white borders
- Universal `18px` card radius (`--radius: 18px`), `9999px` pill radius for all buttons
- Responsive spacing tokens: `--gap-sm 14px`, `--gap-md 22px`, `--gap-lg 40px`, `--gap-xl 56px`, `--section-gap 86px`
- Site-wide PNG noise overlay at `opacity: 0.02` gives a subtle filmic grain
- Bilingual content mixing Chinese marketing copy with Latin product names, both in the same system sans-serif stack

## 2. Color Palette & Roles

### Primary
- **Pure Black** (`#000000`): Dominant canvas — hero, sections, footer, nav background. The default surface.
- **Deep Black** (`#0a0a0a`): `--bg-1` — section background gradient start, slightly warmer than pure black.
- **Near Black** (`#050505`): Section gradient endpoint, used to create subtle vertical depth.
- **Pure White** (`#ffffff`): Primary text, primary CTA button backgrounds, logo wordmark.

### Brand Accent Gradients
- **Brand Gradient (Indigo)**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` — the one decorative color moment in the system. Used for accent CTAs, highlighted icons, feature emphasis. Not used for body text or large backgrounds.
- **Brand Indigo Start** (`#667eea`): Cool periwinkle, the lighter end of the brand gradient.
- **Brand Indigo End** (`#764ba2`): Deep amethyst purple, the darker end.
- **Display Gradient (Ice Blue)**: `linear-gradient(135deg, #ffffff 0%, #64b5f6 100%)` — applied as `-webkit-background-clip: text` on the version title ("Pro", "Ultra"). Reads as a soft chrome sheen.
- **Display Blue** (`#64b5f6`): Soft sky blue, endpoint of the display gradient.

### Surface & Background
- **Section Gradient**: `linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #050505 100%)` — primary dark section treatment, creates vertical depth.
- **Glass Surface** (`rgba(255, 255, 255, 0.02)`): Feature card and testimonial card fill — barely-visible on black, relies on the border to define the shape.
- **Glass Surface Hover** (`rgba(255, 255, 255, 0.04)`): Hover state for glass cards, doubling the opacity for subtle lift.
- **Social Chip** (`rgba(255, 255, 255, 0.05)`): Fill for circular footer social icon buttons.
- **Hero Overlay**: `linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.8) 100%)` — vignette that fades hero footage into the page.
- **Light Card Surface** (`#f8f9fa`): Alternate light card background used in the one inverted feature section.

### Borders
- **Hairline White** (`rgba(255, 255, 255, 0.05)`): Softest divider, barely visible on black.
- **Glass Border** (`rgba(255, 255, 255, 0.08)`): Feature card and testimonial border — the primary dark card edge.
- **Nav Border** (`rgba(255, 255, 255, 0.1)`): Fixed header bottom edge and moderate dividers.
- **Strong Border** (`rgba(255, 255, 255, 0.2)`): Secondary button outline and higher-contrast dividers.

### Neutrals & Text
- **White 100%** (`#ffffff`): Primary headlines, hero wordmark, button text on black CTAs.
- **Light Grey** (`#b0b0b0`): Lead paragraphs and lighter body text on dark surfaces.
- **Mid Grey** (`#999999`): Default nav link color and secondary body text.
- **Muted Grey** (`#666666`): Tertiary text, footer copy, metadata, disclaimers.
- **Link Grey** (`#cccccc`): Inline text link default state on dark.
- **Hover White** (`#f0f0f0`): Primary button background on hover (slightly off-white).

### Semantic
- **Success Green** (`#4ade80`): Checkmarks in pricing feature lists and positive confirmation states.
- **Danger Red** (`#ef4444`): Error states and critical warnings (used sparingly).
- **Warning Amber** (`#fbbf24`): Limited-availability notices and cautionary states.

### Gradient System
- **Brand Indigo Gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` — the signature accent. Reserved for icon fills, accent borders, and emphasis moments. Never used on body text.
- **Display Ice Gradient**: `linear-gradient(135deg, #ffffff 0%, #64b5f6 100%)` — applied with `background-clip: text` on version titles for a soft chrome effect.
- **Section Vertical Gradient**: `linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #050505 100%)` — the primary section background.
- **Hero Vignette**: `linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.8) 100%)` — fades hero content into the next section.
- No gradients on primary buttons — they stay flat white or flat black.

## 3. Typography Rules

### Font Family
- **Primary**: `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `Roboto`, `"Helvetica Neue"`, `Arial`, `sans-serif` — the default system stack. No custom webfonts are loaded; the site relies on each OS's native UI face.
- **CJK handling**: Chinese characters (`转换一切，从未如此简单`) inherit the same stack and render with whichever CJK fallback the OS provides (PingFang SC on macOS, Microsoft YaHei on Windows, Noto Sans CJK on Linux/Android). No dedicated CJK font-family declaration.
- **No serif or monospace** variants — the entire site is a single sans-serif voice.

### Hierarchy

| Role | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|--------|-------------|----------------|-------|
| Hero Display | 12.5rem (200px) | 900 | 1.0 | -2px | `SyncTools Pro` wordmark, behaves as a lockup |
| Section Heading (H2) | 3rem (48px) | 800 | 1.15 | -0.5px | Major feature section titles |
| Feature Heading (H3) | 2rem (32px) | 700 | 1.2 | -0.3px | Sub-section titles, card headings |
| Card Title | 1.5rem (24px) | 600 | 1.3 | normal | Feature card and pricing card titles |
| Sub-heading | 1.25rem (20px) | 500 | 1.4 | normal | Supporting headlines, tagline |
| Lead Body | 1.125rem (18px) | 400 | 1.68 (`--lh-loose`) | normal | Feature descriptions, intro paragraphs |
| Body | clamp(15px, 1.4vw, 16px) (`--fs-body`) | 400 | 1.6 (`--lh-normal`) | normal | Standard body text |
| Small Body | 0.9rem (14.4px) | 400 | 1.5 | normal | Metadata, specs, list items |
| Nav / Link | 0.9rem (14.4px) | 500 | 1.0 | 0.5px | Navigation items, menu links |
| Caption | 0.8rem (12.8px) | 400 | 1.4 | normal | Footnotes, legal text |
| Button Label | 1rem (16px) | 500-600 | 1.0 | 0.3px | Primary/secondary CTA text |

### Principles
- **Extreme hero scale**: The hero display (`12.5rem`) is not a headline — it is a wordmark. It sits alone on its line with heavy negative tracking (`-2px`) to behave like a logo.
- **Heaviest weights for display only**: Weight `900` is reserved for the hero wordmark, `800` for section titles, `700` for feature headings. Body stays at `400`.
- **Responsive body type**: Body text uses `clamp(15px, 1.4vw, 16px)` so paragraphs scale gently with viewport width rather than jumping at breakpoints.
- **Generous body line-height**: `--lh-loose: 1.68` for lead paragraphs and `--lh-normal: 1.6` for body — open, comfortable reading on dark surfaces.
- **Tight display line-height**: Hero sits at `line-height: 1.0` so the enormous wordmark does not push vertical space unnecessarily.
- **Letter-spacing as emphasis**: Nav links and button labels get a tiny positive letter-spacing (`0.5px`, `0.3px`) to feel crisp at small sizes; display headlines get negative tracking for density.
- **No italic, no decorative styling**: Every character is upright sans-serif. Emphasis comes from weight, scale, and the brand gradient — never from italics or script faces.

## 4. Component Stylings

### Buttons

**Primary CTA** — The main action button (inverted: white on dark):
- Default: bg `#ffffff`, text `#000000`, fontSize 16px, fontWeight 500-600, padding 15px 40px, borderRadius 9999px (full pill), no border
- Hover: bg `#f0f0f0`, `transform: translateY(-3px)`, `box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2)`
- Active: `transform: translateY(-1px)`, reduced shadow
- Transition: `all 0.3s ease`
- Use: "Get Pro", "Get Ultra", "立即下载" (Download Now), hero primary CTA

**Secondary CTA** — The alternate action button (outline on dark):
- Default: bg transparent, text `#ffffff`, border `2px solid #ffffff`, same padding (15px 40px), borderRadius 9999px
- Hover: bg `rgba(255, 255, 255, 0.1)`, `transform: translateY(-3px)`, subtle white-glow shadow
- Transition: `all 0.3s ease`
- Use: "Learn More", "Watch Demo" alongside the primary CTA

**Gradient Accent Button** — Used for emphasis / special actions:
- Default: bg `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`, text `#ffffff`, padding 15px 40px, borderRadius 9999px
- Hover: `transform: translateY(-3px)`, `box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3)`
- Use: Highlighted CTA moments, "Upgrade to Ultra"

**Pricing CTA** — The buy-button variant:
- Default: bg `#ffffff`, text `#000000`, padding 16px 32px, borderRadius 50px (pill), fontWeight 600
- Hover: same white-lift treatment as Primary CTA
- Use: "Get Pro ¥98", "Get Ultra ¥298" on pricing cards

**Text Link** — Inline interactive text:
- Default: text `#cccccc`, no underline
- Hover: text `#ffffff`, underline via `::after` pseudo-element that grows `width: 0 → 100%` over 0.3s
- Use: Footer links, inline references, "Learn more →" CTAs

**Nav Link** — Top-nav items:
- Default: text `#999999`, fontSize 0.9rem, fontWeight 500, letter-spacing 0.5px
- Hover: text `#ffffff` + animated underline (`::after` bar, `height: 1px`, `background: #ffffff`, `width: 0 → 100%`, `transition: width 0.3s ease`)
- Active section: text `#ffffff` with persistent underline

### Cards & Containers

**Feature Card (Dark / Glass)**:
- Background: `rgba(255, 255, 255, 0.02)` with `backdrop-filter: blur(10px)`
- Border: `1px solid rgba(255, 255, 255, 0.08)`
- BorderRadius: 18px (`--radius`)
- Padding: 30-40px
- Shadow: none (relies on border for edge definition)
- Hover: background brightens to `rgba(255, 255, 255, 0.04)`, `transform: translateY(-2px) scale(1.02)`, subtle shadow `0 8px 25px rgba(0, 0, 0, 0.3)`
- Transition: `all 0.3s ease`
- Content: icon (often gradient-filled) + heading (24px weight 600) + description (16px `#b0b0b0`)

**Feature Card (Light Invert)**:
- Background: `#f8f9fa`
- Border: `1px solid rgba(0, 0, 0, 0.05)`
- BorderRadius: 18px
- Shadow: `0 8px 25px rgba(0, 0, 0, 0.08)`
- Hover: `transform: translateY(-2px)`, shadow deepens to `0 20px 40px rgba(0, 0, 0, 0.12)`
- Use: The one light-inverted feature section for visual contrast

**Testimonial Card**:
- Background: `rgba(255, 255, 255, 0.02)` + `backdrop-filter: blur(10px)`
- Border: `1px solid rgba(255, 255, 255, 0.08)`
- BorderRadius: 18px
- Padding: 40px
- Hover: `transform: scale(1.02)`, background → `rgba(255, 255, 255, 0.04)`
- Content: quote text (18px `#b0b0b0` line-height 1.68), author name + role (14px `#999999`)

**Pricing Card**:
- Background: `rgba(255, 255, 255, 0.02)` + `backdrop-filter: blur(10px)`
- Border: `1px solid rgba(255, 255, 255, 0.08)` (Ultra tier gets `rgba(255, 255, 255, 0.2)` or the brand gradient as border)
- BorderRadius: 18px
- Padding: 48px
- Content: tier name, price in white at 3rem weight 800, feature list with green `#4ade80` checkmarks, white pill CTA at bottom
- Ultra tier: subtle indigo gradient glow behind the card, slightly larger scale

**Feature Image Container**:
- BorderRadius: 18px
- Shadow: `0 30px 60px rgba(255, 255, 255, 0.1)` — inverted white glow instead of black shadow, creating a soft rim-light effect around screenshots
- Hover: `transform: scale(1.02)`, transition `0.4s ease`

### Inputs & Forms
- Background: `rgba(255, 255, 255, 0.05)`
- Text: `#ffffff`
- Placeholder: `#666666`
- Border: `1px solid rgba(255, 255, 255, 0.1)`
- BorderRadius: 18px or 9999px (pill for search/email)
- Padding: 14px 20px
- Focus: border-color transitions to `rgba(255, 255, 255, 0.3)` or the brand indigo `#667eea`
- Height: 48-52px

### Navigation
- **Desktop**: Fixed top, height `60px` (desktop), `55px` (tablet), `50px` (mobile)
- **Background**: `rgba(0, 0, 0, 0.9)` with `backdrop-filter: blur(10px)`
- **Border**: `1px solid rgba(255, 255, 255, 0.1)` on the bottom edge
- **Shadow**: `0 10px 30px rgba(0, 0, 0, 0.5)` (drop-shadow below nav)
- **Padding**: `0 20px` (desktop), `0 15px` (tablet), `0 12px` (mobile)
- **Z-index**: `1001`
- **Layout**: Flexbox row, `justify-content: space-between`, logo left, nav links center, CTA right
- **Logo**: "SyncTools" wordmark in white, weight 700, letter-spacing 0.5px
- **Links**: `#999999` at 0.9rem weight 500, letter-spacing 0.5px, horizontal with ~32px gap
- **Hover**: text brightens to `#ffffff` + animated underline bar grows below
- **Nav CTA**: small white pill button ("Download" / "下载"), `#ffffff` background, `#000000` text, `border-radius: 9999px`, padding `8px 20px`

### Footer
- Background: `#000000`
- Text: `#666666` for copy, `#cccccc` for link defaults, `#ffffff` on hover
- Layout: centered multi-column, generous top padding (~80px)
- **Social icon chips**: 50×50px circles, `background: rgba(255, 255, 255, 0.05)`, `border-radius: 50%`, icon color `#cccccc`
- Social hover: `transform: translateY(-5px)`, background → `rgba(255, 255, 255, 0.1)`, icon → `#ffffff`
- Copyright line: `#666666` at 14px, centered at the bottom

### Image Treatment
- **Hero**: Full-viewport (`min-height: 100vh`, `padding-top: 120px`) with animated grid background pattern (20s cycle loop) and floating particle dots
- **Product screenshots**: Rounded at 18px, framed with a soft white-glow shadow (`0 30px 60px rgba(255, 255, 255, 0.1)`) so they appear to float on the black canvas
- **Feature illustrations**: Flat line-art icons or gradient-filled glyphs, monochrome or indigo-gradient
- **Noise overlay**: Site-wide PNG grain at `opacity: 0.02` via a fixed pseudo-element — gives the whole page a subtle filmic texture

### Distinctive Components

**Extreme-Scale Hero Wordmark**:
- `font-size: 12.5rem`, `font-weight: 900`, `letter-spacing: -2px`
- Character-by-character typewriter animation on load
- Positioned with heavy top padding (`padding-top: 120px`) to sit below the fixed nav
- Tagline ("转换一切，从未如此简单") below at 20-24px in `#b0b0b0`

**Version Title with Ice Gradient**:
- Used for "Pro" / "Ultra" labels on pricing tiers
- `background: linear-gradient(135deg, #ffffff 0%, #64b5f6 100%)`, `-webkit-background-clip: text`, `-webkit-text-fill-color: transparent`
- Font size ~3rem, weight 800

**Animated Grid Background**:
- Decorative CSS grid pattern on the hero, animating horizontally over a 20s infinite loop
- Line color: `rgba(255, 255, 255, 0.03)`
- Sits behind content at `z-index: 0`

**Floating Particles**:
- Small white dots (2-4px) with staggered keyframe animations
- Positioned absolutely across the hero, each with its own animation delay
- Suggest motion without competing with the wordmark

**Shimmer Placeholder**:
- `::before` pseudo-element with a diagonal white-gradient sweep that loops across image placeholders while content loads
- 2-3s linear infinite

**Scroll-triggered Fade-up**:
- Cards and sections enter via `opacity: 0 → 1` + `transform: translateY(30px) → 0`
- Triggered by `IntersectionObserver` as elements enter viewport

**Pricing Comparison Block**:
- Two cards side-by-side (Pro ¥98, Ultra ¥298)
- Ultra is visually elevated: slightly larger, indigo glow backdrop, "Recommended" badge in brand gradient
- Feature lists use green `#4ade80` check icons, cross-outs for unavailable features use muted `#666666`

## 5. Layout Principles

### Spacing System
- **Base unit**: ~8px, expressed through semantic tokens rather than raw values
- **CSS custom properties**:
  - `--gap-sm: 14px`
  - `--gap-md: 22px`
  - `--gap-lg: 40px`
  - `--gap-xl: 56px`
  - `--section-gap: 86px`
  - `--section-gap-sm: 56px`
- **Section vertical padding**: 100px desktop, 80px tablet, 60px mobile
- **Card internal padding**: 30-40px for feature cards, 48px for pricing cards
- **Button padding**: 15px 40px (primary/secondary), 16px 32px (pricing)

### Grid & Container
- **Max width**: 1200-1400px, centered with auto margins
- **Horizontal padding**: 20px desktop, 15px tablet, 12px mobile
- **Hero**: Full-bleed, `min-height: 100vh`, `padding-top: 120px`
- **Feature grids**: 3-column desktop → 2-column tablet → 1-column mobile
- **Pricing**: 2-column centered on desktop, stacks on mobile
- **Testimonials**: 2-3 column responsive grid
- **Section gap**: `--section-gap: 86px` between major blocks, reducing to `--section-gap-sm: 56px` on tablet

### Whitespace Philosophy
SyncTools uses darkness as negative space — vast expanses of near-black give each feature block its own theater. The extreme-scale hero wordmark sits on a mostly empty page, surrounded by hundreds of pixels of black breathing room, then the page transitions to tightly-grouped feature cards and finally opens up again for testimonials. The rhythm alternates between density (3-column feature grids, dense pricing lists) and emptiness (full-viewport hero, isolated CTAs). The site-wide noise overlay prevents the black from feeling flat — it gives the darkness a subtle physical texture.

### Border Radius Scale
| Value | Context |
|-------|---------|
| 0px | Full-bleed sections, nav bar bottom |
| 8px | Small chips, tags, tooltips |
| 12px | Secondary cards, smaller containers |
| 18px | Primary system radius — feature cards, pricing cards, images, testimonials (`--radius: 18px`) |
| 50px | Pricing CTA pills |
| 9999px | Buttons, nav CTAs, fully rounded pills |
| 50% | Circular — social icons, avatars, status dots |

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Level 0 (Flat) | No shadow, gradient dark background | Default for all sections, hero, footer |
| Level 1 (Glass Card) | `rgba(255,255,255,0.02)` + `backdrop-filter: blur(10px)` + `1px solid rgba(255,255,255,0.08)` | Feature cards, testimonials, pricing cards |
| Level 2 (Nav Glass) | `rgba(0,0,0,0.9)` + `backdrop-filter: blur(10px)` + `0 10px 30px rgba(0,0,0,0.5)` | Fixed top navigation |
| Level 3 (Card Lift) | `0 8px 25px rgba(0, 0, 0, 0.08)` (on light) or soft scale (`1.02`) + background brighten (on dark) | Hovered cards |
| Level 4 (Image Float) | `0 30px 60px rgba(255, 255, 255, 0.1)` | Product screenshots (inverted white glow, not black shadow) |
| Level 5 (Modal) | `0 20px 60px rgba(0, 0, 0, 0.5)` + full-screen backdrop `rgba(0,0,0,0.8)` | Modal dialogs and video overlays |

### Shadow Philosophy
SyncTools inverts the standard shadow logic for its signature product screenshots: instead of black shadows casting downward, screenshots are framed with a **white glow** (`0 30px 60px rgba(255, 255, 255, 0.1)`), making them appear to radiate on the black canvas like backlit displays. Elsewhere on dark surfaces, shadows are largely absent — cards rely on hairline white borders and `backdrop-filter: blur` to define edges. On the one light-inverted section, standard soft black shadows return (`0 8px 25px rgba(0, 0, 0, 0.08)`).

### Decorative Depth
- **White-glow shadows on screenshots**: Inverted shadow logic creates a "backlit screen" effect
- **Backdrop-filter blur**: Nav and cards both use `blur(10px)` to create layered glass planes floating over the hero
- **Animated grid background**: Subtle motion at low opacity gives depth to the hero without a static texture
- **Noise overlay**: Site-wide PNG grain at `opacity: 0.02` adds tactile surface to the darkness
- **Brand gradient glows**: Indigo gradient shadows (`rgba(102, 126, 234, 0.3)`) used sparingly on accent buttons
- **Hero vignette**: Bottom-fade gradient creates a natural transition from hero to first section

## 7. Do's and Don'ts

### Do
- Use pure / near-black (`#000000` / `#0a0a0a` / `#050505`) as the default canvas — the dark identity is non-negotiable
- Make primary CTAs **white with black text** and fully pill-shaped (`border-radius: 9999px`) — this is the signature SyncTools button
- Reserve the indigo gradient (`#667eea → #764ba2`) for accent moments only — never body text, never section backgrounds
- Use the ice gradient (`#ffffff → #64b5f6`) on version titles and tier labels with `background-clip: text`
- Apply the `18px` radius consistently to feature cards, testimonials, pricing cards, and image frames
- Keep feature cards as glass: `rgba(255,255,255,0.02)` + `backdrop-filter: blur(10px)` + hairline white border
- Use `#b0b0b0` and `#999999` for body / secondary text — not pure white for everything
- Let the hero wordmark breathe at `12.5rem` / weight `900` — it is the product signature, not a sentence
- Use white-glow shadows (`rgba(255,255,255,0.1)`) on product screenshots to make them feel backlit
- Add the site-wide noise overlay at `opacity: 0.02` to prevent the black from feeling plastic
- Mix Chinese and Latin text freely in the same stack — the system sans-serif handles both

### Don't
- Don't use colored backgrounds or colorful sections — the black canvas must carry 95%+ of the page
- Don't make primary CTAs indigo or gradient — primary is **white**, accent buttons get the gradient
- Don't use small radius values (2-4px) on cards — the `18px` / `9999px` pairing is the signature shape language
- Don't use bold 900 weight outside the hero wordmark — it is the one place that extreme weight lives
- Don't apply black drop-shadows to product screenshots — use the inverted white glow instead
- Don't use body weight `700+` — body text is `400`, UI labels are `500-600`
- Don't break the pill button shape — buttons are `border-radius: 9999px`, not `8px` or `16px`
- Don't use italics or script faces — the site is 100% upright sans-serif
- Don't crowd the hero with multiple CTAs or chrome — the wordmark should own the first viewport
- Don't forget the hover animations: buttons lift `translateY(-3px)` + glow; cards lift `translateY(-2px) scale(1.02)`
- Don't use dedicated CJK fonts — inherit the system stack so Chinese matches the Latin voice

## 8. Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile | <640px | Single-column layout, hamburger nav, hero wordmark scales down dramatically (~5-6rem), CTAs stack vertically full-width, section padding 60px, nav height 50px |
| Tablet | 640-1024px | 2-column grids for features, hero wordmark ~8-10rem, horizontal nav collapses to hamburger, section padding 80px, nav height 55px, `--section-gap-sm: 56px` |
| Desktop | 1024-1400px | Full 3-column feature grids, hero at `12.5rem`, horizontal nav visible, section padding 100px, nav height 60px, `--section-gap: 86px` |
| Large Desktop | >1400px | Content centered at 1200-1400px max-width, generous side gutters, hero may scale up slightly |

### Touch Targets
- Primary CTA buttons: 48-52px minimum height (padding 15px 40px ensures touch-friendly area)
- Pricing CTAs: 52-56px tall (padding 16px 32px)
- Nav links: full 60px header height provides adequate touch area on tablet/mobile
- Social icons in footer: 50×50px circles, well above 44px minimum
- Card interactions: entire card surface is tappable on mobile

### Collapsing Strategy
- **Navigation**: Full horizontal links → hamburger icon → full-screen dark overlay menu with vertically-stacked links
- **Hero wordmark**: Scales from `12.5rem` → ~`8rem` → ~`5-6rem` via clamp or media queries
- **CTA pair**: Side-by-side → stacked vertically, each full-width
- **Feature grids**: 3-column → 2-column → 1-column
- **Pricing cards**: Side-by-side → stacked vertically, Ultra tier stays visually prominent
- **Testimonials**: 3-column → 2-column → 1-column carousel or stack
- **Section spacing**: `--section-gap` scales down from 86px → 56px → 40px
- **Body font**: `clamp(15px, 1.4vw, 16px)` scales automatically without breakpoints

### Image Behavior
- Hero animated grid background maintains full-bleed at all breakpoints
- Product screenshots scale proportionally with viewport, maintaining the 18px radius and white-glow shadow
- Feature illustrations scale with their cards
- Noise overlay covers the full viewport at every size
- Floating particles reduce in count or disable entirely on mobile to preserve battery

## 9. Agent Prompt Guide

### Quick Color Reference
- Background (primary): Pure Black (`#000000`)
- Background (section gradient): `linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #050505 100%)`
- Primary CTA: White (`#ffffff` bg, `#000000` text, `border-radius: 9999px`)
- Secondary CTA: Transparent bg, white text, `2px solid #ffffff` border, `border-radius: 9999px`
- Accent gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Display gradient (titles): `linear-gradient(135deg, #ffffff 0%, #64b5f6 100%)`
- Heading text: `#ffffff`
- Body text: `#b0b0b0`
- Secondary text: `#999999`
- Muted text: `#666666`
- Glass card surface: `rgba(255, 255, 255, 0.02)` + `backdrop-filter: blur(10px)`
- Glass card border: `1px solid rgba(255, 255, 255, 0.08)`
- Success: `#4ade80`
- System radius: `18px` for cards, `9999px` for buttons
- Grid width: `1200-1400px`
- Header height: `60px`
- Section gap: `86px`
- Font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`

### Example Component Prompts
- "Create a SyncTools-style hero section: full-viewport (min-height 100vh, padding-top 120px) on pure black `#000000` with a subtle animated grid background pattern at `rgba(255,255,255,0.03)`. Center an enormous wordmark 'SyncTools Pro' at `font-size: 12.5rem`, `font-weight: 900`, `letter-spacing: -2px`, color `#ffffff`, line-height 1.0. Below it a tagline '转换一切，从未如此简单' at 20px color `#b0b0b0`. Two buttons centered below: primary pill (`#ffffff` bg, `#000000` text, `border-radius: 9999px`, padding 15px 40px) and secondary pill (transparent bg, white text, `2px solid #ffffff` border, same padding). Add a faint PNG noise overlay at `opacity: 0.02` across the whole section."

- "Design a SyncTools navigation bar: fixed top, 60px height, background `rgba(0, 0, 0, 0.9)` with `backdrop-filter: blur(10px)`, bottom border `1px solid rgba(255, 255, 255, 0.1)`, shadow `0 10px 30px rgba(0, 0, 0, 0.5)`. Logo 'SyncTools' left in white weight 700. Horizontal nav links center at 0.9rem, color `#999999`, letter-spacing 0.5px, with an animated underline on hover that grows width 0→100% in 0.3s and text brightening to `#ffffff`. Small white pill 'Download' button on the right (`#ffffff` bg, `#000000` text, padding 8px 20px, `border-radius: 9999px`)."

- "Build a SyncTools feature card grid: 3 columns on desktop, 18px border-radius, background `rgba(255, 255, 255, 0.02)` with `backdrop-filter: blur(10px)`, border `1px solid rgba(255, 255, 255, 0.08)`, padding 40px. Each card contains a gradient-filled icon (use `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`), a heading at 24px weight 600 in white, and description text at 16px color `#b0b0b0` line-height 1.68. On hover: background brightens to `rgba(255, 255, 255, 0.04)`, `transform: translateY(-2px) scale(1.02)`, transition `all 0.3s ease`."

- "Create a SyncTools pricing section: two glass cards side-by-side on black `#000000`, each with 18px radius, `rgba(255, 255, 255, 0.02)` background + blur(10px), 48px padding. Tier title 'Pro' / 'Ultra' at 3rem weight 800 using `background: linear-gradient(135deg, #ffffff 0%, #64b5f6 100%)` with `background-clip: text`. Price '¥98' / '¥298' in white at 4rem weight 900. Feature list with green `#4ade80` checkmark icons, text in `#b0b0b0`. Bottom CTA: white pill button (`#ffffff` bg, `#000000` text, padding 16px 32px, `border-radius: 50px`, weight 600). Ultra tier gets a subtle indigo glow backdrop and a 'Recommended' badge in the brand gradient."

- "Design a SyncTools product screenshot showcase: full-width container on black with a centered app screenshot framed at 18px border-radius and a soft white-glow shadow `0 30px 60px rgba(255, 255, 255, 0.1)` — no black drop-shadow. On hover `transform: scale(1.02)` over 0.4s. The image should feel backlit rather than cast downward."

- "Build a SyncTools testimonial card: `rgba(255, 255, 255, 0.02)` background with `backdrop-filter: blur(10px)`, `1px solid rgba(255, 255, 255, 0.08)` border, 18px radius, 40px padding. Quote text at 18px color `#b0b0b0` line-height 1.68. Below, author name in white at 14px weight 600 and role below at 14px color `#999999`. Hover scales to 1.02 and background brightens to `rgba(255, 255, 255, 0.04)`."

### Iteration Guide
When refining existing screens generated with this design system:
1. **Background check**: If a section feels off, confirm the background is pure or near-black (`#000000` / `#0a0a0a`) — SyncTools never uses mid-grey or colored section backgrounds.
2. **CTA inversion**: Primary buttons must be **white on black**, not indigo or gradient. The indigo gradient is reserved for accent buttons and icons only.
3. **Pill shape**: All buttons must be `border-radius: 9999px` (full pill). Any rectangular or slightly-rounded button breaks the signature shape.
4. **Card radius**: Feature cards, testimonials, pricing cards, and images should all use `18px` — not `12px`, not `16px`.
5. **Glass effect**: Cards on dark backgrounds must use `backdrop-filter: blur(10px)` + `rgba(255, 255, 255, 0.02)` + a hairline white border. Solid-color cards break the atmosphere.
6. **Inverted shadows on screenshots**: Product screenshots use a **white glow** (`rgba(255, 255, 255, 0.1)`) — not a black drop-shadow. This is a signature move.
7. **Hero scale**: If the hero wordmark feels small, push it to `12.5rem` with `font-weight: 900` and `letter-spacing: -2px`. It should behave like a logo lockup, not a headline.
8. **Text hierarchy**: Use `#ffffff` / `#b0b0b0` / `#999999` / `#666666` for the four levels of dark-background text. Avoid arbitrary grey hex values.
9. **Noise overlay**: If the darkness feels plastic, add the PNG grain overlay at `opacity: 0.02` — it gives the whole page a filmic surface.
10. **Hover animations**: Every interactive element lifts on hover. Buttons: `translateY(-3px)` + glow shadow. Cards: `translateY(-2px) scale(1.02)` + background brighten. Social icons: `translateY(-5px)`. Skip these and the page feels static.
11. **Version titles**: Use the ice gradient (`#ffffff → #64b5f6`) with `background-clip: text` for tier labels ("Pro", "Ultra") — it is the one place this specific gradient appears.
12. **Bilingual handling**: Let Chinese and Latin text share the same system font stack. Don't declare a separate CJK family — the OS fallback is part of the aesthetic.
