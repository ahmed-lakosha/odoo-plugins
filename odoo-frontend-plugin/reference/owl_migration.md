# Owl Framework Version Migration Guide

## Owl Version Matrix

| Odoo Version | Owl Version | Status |
|--------------|-------------|--------|
| 14.0 | Experimental | Not recommended |
| 15.0 | Experimental | Not recommended |
| 16.0 | 1.x | Stable |
| 17.0 | 1.x | Stable |
| 18.0 | 2.x | Current |
| 19.0 | 2.x | Current |

## Owl v1 vs Owl v2 Breaking Changes

### 1. Component Template Definition

**Owl v1 (Odoo 16-17):**
```javascript
class MyComponent extends Component {
    // Template as class property
}
MyComponent.template = "module.template_id";
```

**Owl v2 (Odoo 18-19):**
```javascript
class MyComponent extends Component {
    // Template as static property
    static template = "module.template_id";
}
```

### 2. Props Definition

**Owl v1:**
```javascript
class MyComponent extends Component {
    // Optional props definition
}
MyComponent.props = {
    title: String,
    items: Array,
};
```

**Owl v2:**
```javascript
class MyComponent extends Component {
    // Required static props with validation
    static props = {
        title: { type: String, optional: true },
        items: { type: Array },
    };
}
```

### 3. Hooks and Lifecycle

**Owl v1:**
```javascript
import { Component, useState } from "@odoo/owl";

class MyComponent extends Component {
    setup() {
        this.state = useState({ count: 0 });
    }
}
```

**Owl v2:**
```javascript
import { Component, useState } from "@odoo/owl";

class MyComponent extends Component {
    setup() {
        // useState still works the same
        this.state = useState({ count: 0 });
    }
}
```

### 4. Template Syntax

**Slot Syntax Changes:**

**Owl v1:**
```xml
<!-- Parent -->
<t t-name="ParentTemplate">
    <div>
        <t t-slot="default"/>
    </div>
</t>

<!-- Child -->
<ParentComponent>
    <t t-set-slot="default">
        Content here
    </t>
</ParentComponent>
```

**Owl v2:**
```xml
<!-- Parent -->
<t t-name="ParentTemplate">
    <div>
        <t t-slot="default"/>
    </div>
</t>

<!-- Child -->
<ParentComponent>
    <t t-set-slot="default">
        Content here
    </t>
</ParentComponent>
```

*(Slot syntax largely unchanged, but validation is stricter)*

### 5. Event Handling

**Owl v1:**
```javascript
class MyComponent extends Component {
    onClick(ev) {
        // Handle click
    }
}
```

```xml
<button t-on-click="onClick">Click me</button>
```

**Owl v2:**
```javascript
class MyComponent extends Component {
    onClick(ev) {
        // Handle click - same as v1
    }
}
```

```xml
<button t-on-click="onClick">Click me</button>
```

*(Event handling unchanged)*

### 6. Component Registration

**Owl v1:**
```javascript
import { registry } from "@web/core/registry";

registry.category("public_components").add("MyComponent", MyComponent);
```

**Owl v2:**
```javascript
import { registry } from "@web/core/registry";

// Same registration method
registry.category("public_components").add("MyComponent", MyComponent);
```

## Migration Checklist

### Code Changes

- [ ] Convert `Component.template` to `static template`
- [ ] Convert `Component.props` to `static props`
- [ ] Add type validation to all props
- [ ] Mark optional props with `optional: true`
- [ ] Test all lifecycle hooks (setup, willStart, etc.)
- [ ] Verify event handlers still work
- [ ] Check slot usage (stricter validation)
- [ ] Update component imports if paths changed

### Testing

- [ ] Test component rendering
- [ ] Test props passing
- [ ] Test state updates (reactivity)
- [ ] Test event emissions
- [ ] Test lifecycle methods
- [ ] Check browser console for warnings
- [ ] Verify no deprecation notices

## Common Pitfalls

### 1. Missing Props Validation

**Problem:**
```javascript
// Owl v2 will throw error if props not defined
static props = {};  // Empty but required
```

**Solution:**
```javascript
static props = {
    title: { type: String },
    items: { type: Array, optional: true },
};
```

### 2. Template Not Static

**Problem:**
```javascript
class MyComponent extends Component {
    constructor() {
        this.template = "module.template";  // Wrong!
    }
}
```

**Solution:**
```javascript
class MyComponent extends Component {
    static template = "module.template";  // Correct!
}
```

### 3. Props Type Mismatch

**Problem:**
```javascript
static props = {
    count: Number,  // Old syntax
};
```

**Solution:**
```javascript
static props = {
    count: { type: Number },  // New syntax
};
```

## Example: Complete Migration

### Owl v1 Component (Odoo 17)

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class TestimonialCarousel extends Component {
    setup() {
        this.state = useState({
            currentIndex: 0,
            testimonials: [],
        });
    }

    async willStart() {
        // Load testimonials
        this.state.testimonials = await this.loadTestimonials();
    }

    async loadTestimonials() {
        // RPC call
        return [];
    }

    nextSlide() {
        this.state.currentIndex = (this.state.currentIndex + 1) % this.state.testimonials.length;
    }

    prevSlide() {
        this.state.currentIndex = this.state.currentIndex > 0
            ? this.state.currentIndex - 1
            : this.state.testimonials.length - 1;
    }
}

TestimonialCarousel.template = "module.TestimonialCarousel";
TestimonialCarousel.props = {
    category: String,
    maxItems: Number,
};

registry.category("public_components").add("TestimonialCarousel", TestimonialCarousel);

export default TestimonialCarousel;
```

### Owl v2 Component (Odoo 18/19)

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class TestimonialCarousel extends Component {
    static template = "module.TestimonialCarousel";  // ← Static
    static props = {  // ← Static with validation
        category: { type: String, optional: true },
        maxItems: { type: Number, optional: true },
    };

    setup() {
        this.state = useState({
            currentIndex: 0,
            testimonials: [],
        });
    }

    async willStart() {
        // Load testimonials - same as v1
        this.state.testimonials = await this.loadTestimonials();
    }

    async loadTestimonials() {
        // RPC call - same as v1
        return [];
    }

    nextSlide() {
        // Logic unchanged
        this.state.currentIndex = (this.state.currentIndex + 1) % this.state.testimonials.length;
    }

    prevSlide() {
        // Logic unchanged
        this.state.currentIndex = this.state.currentIndex > 0
            ? this.state.currentIndex - 1
            : this.state.testimonials.length - 1;
    }
}

registry.category("public_components").add("TestimonialCarousel", TestimonialCarousel);

export default TestimonialCarousel;
```

### Template (Same for Both Versions)

```xml
<templates>
    <t t-name="module.TestimonialCarousel">
        <div class="testimonial-carousel">
            <button t-on-click="prevSlide" class="carousel-prev">‹</button>

            <div class="testimonial-content">
                <t t-if="state.testimonials.length > 0">
                    <div class="testimonial-item">
                        <t t-set="testimonial" t-value="state.testimonials[state.currentIndex]"/>
                        <p class="testimonial-text" t-esc="testimonial.text"/>
                        <p class="testimonial-author" t-esc="testimonial.author"/>
                    </div>
                </t>
            </div>

            <button t-on-click="nextSlide" class="carousel-next">›</button>
        </div>
    </t>
</templates>
```

## Performance Improvements in Owl v2

1. **Better Reactivity**
   - More efficient state updates
   - Optimized rendering

2. **Smaller Bundle Size**
   - Removed deprecated code
   - Tree-shaking improvements

3. **Better Developer Experience**
   - Clearer error messages
   - Better TypeScript support
   - Stricter validation catches bugs early

## Resources

- **Owl Documentation**: https://github.com/odoo/owl
- **Odoo 18 Release Notes**: Check website builder and Owl changes
- **Migration Examples**: See `odoo/addons/web/static/src/` for core examples

## Automated Detection

Use the version detector to identify Owl version:

```bash
python helpers/version_detector.py <module_path>
# Output includes: owl_version: "2.x"
```

## Best Practices

1. **Always Define Props**
   - Even if empty: `static props = {}`
   - Add proper types and validation

2. **Use Static Properties**
   - Template, props, components (if any)

3. **Test Thoroughly**
   - Owl v2 is stricter with validation
   - Catches more errors at dev time

4. **Check Console**
   - Look for deprecation warnings
   - Address all warnings before deployment

5. **Gradual Migration**
   - Migrate one component at a time
   - Test each component thoroughly
   - Keep detailed migration notes
