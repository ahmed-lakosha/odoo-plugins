# publicWidget JavaScript Patterns

## Basic Pattern

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.MyWidget = publicWidget.Widget.extend({
    selector: '.my-selector',
    disabledInEditableMode: false,  // Handle website builder mode

    events: {
        'click .button': '_onClick',
        'mouseenter .hover-element': '_onMouseEnter',
    },

    /**
     * @override
     */
    start: function () {
        if (!this.editableMode) {
            // Only run in read mode (not in website builder)
            this._initializeWidget();
        }
        return this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    destroy: function () {
        // Clean up event listeners and timers
        this._cleanup();
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private Methods
    //--------------------------------------------------------------------------

    _initializeWidget: function () {
        // Widget initialization logic
    },

    _cleanup: function () {
        // Cleanup logic
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _onClick: function (ev) {
        ev.preventDefault();
        // Handle click
    },

    _onMouseEnter: function (ev) {
        // Handle hover
    },
});

export default publicWidget.registry.MyWidget;
```

## editableMode Handling

The `editableMode` property is crucial for website builder compatibility:

```javascript
start: function () {
    if (this.editableMode) {
        // In website builder - show editing UI
        this._setupEditingMode();
    } else {
        // In read mode - show live functionality
        this._setupLiveMode();
    }
    return this._super.apply(this, arguments);
},
```

## Common Patterns

### 1. Animation Widget
```javascript
publicWidget.registry.AnimateOnScroll = publicWidget.Widget.extend({
    selector: '.animate-on-scroll',
    disabledInEditableMode: true,  // Disable in builder

    start: function () {
        this._setupIntersectionObserver();
        return this._super.apply(this, arguments);
    },

    _setupIntersectionObserver: function () {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, { threshold: 0.1 });

        observer.observe(this.el);
        this._observer = observer;
    },

    destroy: function () {
        if (this._observer) {
            this._observer.disconnect();
        }
        return this._super.apply(this, arguments);
    },
});
```

### 2. Counter Widget
```javascript
publicWidget.registry.CounterWidget = publicWidget.Widget.extend({
    selector: '.counter-widget',
    disabledInEditableMode: true,

    start: function () {
        this._animateCounters();
        return this._super.apply(this, arguments);
    },

    _animateCounters: function () {
        this.$('.counter').each((i, el) => {
            const target = parseInt(el.dataset.target, 10);
            this._countUp(el, target);
        });
    },

    _countUp: function (el, target) {
        let current = 0;
        const duration = 2000;
        const step = target / (duration / 16);

        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = Math.floor(current);
        }, 16);
    },
});
```

### 3. Lazy Load Images
```javascript
publicWidget.registry.LazyLoadImages = publicWidget.Widget.extend({
    selector: '.lazy-load-container',
    disabledInEditableMode: true,

    start: function () {
        this._setupLazyLoading();
        return this._super.apply(this, arguments);
    },

    _setupLazyLoading: function () {
        const images = this.$('img[data-src]');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });

        images.each((i, img) => observer.observe(img));
    },
});
```

### 4. Dark Mode Toggle
```javascript
publicWidget.registry.DarkModeToggle = publicWidget.Widget.extend({
    selector: 'body',
    disabledInEditableMode: true,

    events: {
        'click .dark-mode-toggle': '_onToggleDarkMode',
    },

    start: function () {
        // Restore saved preference
        const saved = localStorage.getItem('odoo-dark-mode');
        if (saved === 'true') {
            this.el.classList.add('dark-mode');
            this._updateToggleIcon(true);
        }
        return this._super.apply(this, arguments);
    },

    _onToggleDarkMode: function (ev) {
        ev.preventDefault();
        const isDark = this.el.classList.toggle('dark-mode');
        localStorage.setItem('odoo-dark-mode', isDark);
        this._updateToggleIcon(isDark);
    },

    _updateToggleIcon: function (isDark) {
        this.$('.dark-mode-toggle .toggle-icon')
            .toggleClass('fa-sun', isDark)
            .toggleClass('fa-moon', !isDark);
    },
});
```

**Required SCSS** (`static/src/scss/dark_mode.scss`):
```scss
/* Dark mode CSS variables — add to primary_variables.scss */
body.dark-mode {
    --dm-bg: #1a1a2e;
    --dm-surface: #16213e;
    --dm-text: #e0e0e0;
    --dm-text-muted: #a0a0a0;
    --dm-border: #333;
    --dm-shadow: rgba(0,0,0,0.5);

    background-color: var(--dm-bg);
    color: var(--dm-text);

    /* Override Bootstrap defaults */
    .navbar { background-color: var(--dm-surface) !important; }
    .card { background-color: var(--dm-surface); border-color: var(--dm-border); }
    .footer { background-color: var(--dm-surface); }
    p, h1, h2, h3, h4, h5, h6, span, a { color: var(--dm-text); }
    .text-muted { color: var(--dm-text-muted) !important; }
    input, textarea, select {
        background-color: var(--dm-surface);
        color: var(--dm-text);
        border-color: var(--dm-border);
    }
}
```

**HTML toggle button**:
```xml
<a class="dark-mode-toggle nav-link" href="#" role="button" aria-label="Toggle dark mode">
    <i class="fa fa-moon toggle-icon"/>
</a>
```

---

### 5. RTL/LTR Dynamic Switcher
```javascript
publicWidget.registry.RtlLtrSwitcher = publicWidget.Widget.extend({
    selector: 'body',
    disabledInEditableMode: true,

    events: {
        'click .rtl-toggle': '_onToggleDirection',
        'click [data-lang]': '_onLanguageChange',
    },

    start: function () {
        // Detect current direction from HTML element
        this._currentDir = document.documentElement.getAttribute('dir') || 'ltr';
        this._isRtl = this._currentDir === 'rtl';

        if (this._isRtl) {
            this._applyRtl();
        }
        return this._super.apply(this, arguments);
    },

    _onToggleDirection: function (ev) {
        ev.preventDefault();
        this._isRtl = !this._isRtl;
        if (this._isRtl) {
            this._applyRtl();
        } else {
            this._applyLtr();
        }
    },

    _applyRtl: function () {
        document.documentElement.setAttribute('dir', 'rtl');
        document.documentElement.setAttribute('lang', 'ar');
        this.el.classList.add('rtl');
        // Load Bootstrap RTL CSS if not already loaded
        if (!document.querySelector('link[data-rtl]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.dataset.rtl = '1';
            link.href = '/web/static/lib/bootstrap/css/bootstrap.rtl.min.css';
            document.head.appendChild(link);
        }
    },

    _applyLtr: function () {
        document.documentElement.setAttribute('dir', 'ltr');
        document.documentElement.removeAttribute('lang');
        this.el.classList.remove('rtl');
        const rtlLink = document.querySelector('link[data-rtl]');
        if (rtlLink) rtlLink.remove();
    },

    _onLanguageChange: function (ev) {
        // When switching to Arabic — auto-apply RTL
        const lang = ev.currentTarget.dataset.lang;
        if (lang && lang.startsWith('ar')) {
            this._isRtl = true;
            this._applyRtl();
        } else {
            this._isRtl = false;
            this._applyLtr();
        }
    },
});
```

**SCSS for RTL overrides** (`static/src/scss/rtl_overrides.scss`):
```scss
/* RTL layout fixes — apply when dir="rtl" is set on <html> */
[dir="rtl"] {
    /* Text direction */
    .text-start { text-align: right !important; }
    .text-end   { text-align: left !important; }

    /* Flex direction */
    .d-flex { flex-direction: row-reverse; }
    .flex-row { flex-direction: row-reverse !important; }

    /* Navigation */
    .navbar-nav { margin-right: 0; margin-left: auto; }
    .dropdown-menu { right: 0; left: auto; text-align: right; }

    /* Icons alignment (Font Awesome) */
    .fa-chevron-right::before { content: "\f053"; }  /* swap left/right */
    .fa-chevron-left::before  { content: "\f054"; }

    /* Form labels */
    .form-label { text-align: right; width: 100%; }

    /* Card/content blocks */
    .card-body { text-align: right; }

    /* Use CSS logical properties where Bootstrap 5 supports them */
    .ms-auto { margin-inline-start: auto !important; margin-inline-end: unset !important; }
    .me-auto { margin-inline-end: auto !important; margin-inline-start: unset !important; }

    /* Footer columns */
    .footer .row { flex-direction: row-reverse; }
}
```

**Detecting RTL in JS** (helper pattern):
```javascript
// Check current document direction
const isRtl = () => document.documentElement.getAttribute('dir') === 'rtl';

// Use in any widget
start: function () {
    if (isRtl()) {
        this.$('.icon-arrow').addClass('fa-arrow-left').removeClass('fa-arrow-right');
    }
    return this._super.apply(this, arguments);
},
```

---

## DO NOT Use

- **Inline JavaScript** in templates
- **Owl components** for website themes (use publicWidget)
- **Direct DOM manipulation** without cleanup
- **Global event listeners** without proper removal

## Best Practices

1. Always use `disabledInEditableMode` appropriately
2. Clean up observers, timers, and event listeners in `destroy()`
3. Use `this.$()` for scoped jQuery selections
4. Handle both edit and read modes gracefully
5. Use proper JSDoc comments for methods
6. For dark mode: use CSS custom properties (`var(--dm-*)`) over hardcoded colors
7. For RTL: prefer CSS logical properties (`margin-inline-start`) over physical (`margin-left`)
