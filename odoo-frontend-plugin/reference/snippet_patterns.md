# Odoo Website Snippet Patterns

## Snippet Best Practices

### 1. Naming Conventions

- **Snippet IDs**: Use `s_<name>` prefix (e.g., `s_hero`, `s_testimonials`)
- **CSS Classes**: Match snippet ID for selector (e.g., `.s_hero`)
- **Options**: Use `s_<name>_options` for options template ID
- **JavaScript**: Register as `<Name>Options` (PascalCase)

### 2. Structure

```xml
<section class="s_<name>" data-name="<Snippet Name>">
    <div class="container">
        <div class="row">
            <div class="col-lg-12">
                <!-- Content -->
            </div>
        </div>
    </div>
</section>
```

### 3. Responsive Design

Always use Bootstrap's responsive classes:
- `col-lg-*` for large screens (≥992px)
- `col-md-*` for medium screens (≥768px)
- `col-sm-*` for small screens (≥576px)
- Default for mobile

Example:
```xml
<div class="row">
    <div class="col-lg-6 col-md-12">Content 1</div>
    <div class="col-lg-6 col-md-12">Content 2</div>
</div>
```

## Common Snippet Patterns

### Hero Section

```xml
<template id="s_hero" name="Hero Section">
    <section class="s_hero pt-5 pb-5" data-name="Hero">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6">
                    <h1 class="display-3 fw-bold">Headline Here</h1>
                    <p class="lead">Subheading text goes here</p>
                    <a href="#" class="btn btn-primary btn-lg">Call to Action</a>
                </div>
                <div class="col-lg-6">
                    <img src="/web/image/placeholder.png" class="img-fluid" alt="Hero Image"/>
                </div>
            </div>
        </div>
    </section>
</template>
```

### Feature Grid

```xml
<template id="s_features" name="Feature Grid">
    <section class="s_features pt-5 pb-5" data-name="Features">
        <div class="container">
            <div class="row text-center">
                <div class="col-lg-12 mb-4">
                    <h2>Our Features</h2>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-4 col-md-6 mb-4 feature-item" data-name="Feature Item">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fa fa-3x fa-rocket mb-3 text-primary"></i>
                            <h4 class="card-title">Fast</h4>
                            <p class="card-text">Lightning fast performance</p>
                        </div>
                    </div>
                </div>
                <!-- Repeat for more features -->
            </div>
        </div>
    </section>
</template>
```

### Testimonials Carousel

```xml
<template id="s_testimonials" name="Testimonials">
    <section class="s_testimonials pt-5 pb-5 bg-light" data-name="Testimonials">
        <div class="container">
            <div class="row">
                <div class="col-lg-12 text-center mb-4">
                    <h2>What Our Clients Say</h2>
                </div>
            </div>
            <div id="testimonialCarousel" class="carousel slide" data-bs-ride="carousel">
                <div class="carousel-inner">
                    <div class="carousel-item active testimonial-item" data-name="Testimonial">
                        <div class="row justify-content-center">
                            <div class="col-lg-8 text-center">
                                <p class="testimonial-text h5">"Amazing service and support!"</p>
                                <p class="testimonial-author mt-3">- John Doe, CEO</p>
                            </div>
                        </div>
                    </div>
                    <!-- More testimonial items -->
                </div>
                <button class="carousel-control-prev" type="button" data-bs-target="#testimonialCarousel" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon"></span>
                </button>
                <button class="carousel-control-next" type="button" data-bs-target="#testimonialCarousel" data-bs-slide="next">
                    <span class="carousel-control-next-icon"></span>
                </button>
            </div>
        </div>
    </section>
</template>
```

### Call to Action

```xml
<template id="s_cta" name="Call to Action">
    <section class="s_cta pt-5 pb-5 text-white" style="background-color: var(--o-color-1);" data-name="CTA">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <h2 class="mb-3">Ready to Get Started?</h2>
                    <p class="lead mb-0">Join thousands of satisfied customers today</p>
                </div>
                <div class="col-lg-4 text-lg-end">
                    <a href="/contactus" class="btn btn-light btn-lg">Contact Us</a>
                </div>
            </div>
        </div>
    </section>
</template>
```

## Snippet Options Patterns

### Layout Selection

```xml
<we-select string="Layout">
    <we-button data-select-class="">Default</we-button>
    <we-button data-select-class="s_<name>_centered">Centered</we-button>
    <we-button data-select-class="s_<name>_wide">Wide</we-button>
</we-select>
```

### Add/Remove Items

```xml
<we-row string="Items">
    <we-button data-add-item="true"
               data-selector=".feature-item"
               data-no-preview="true"
               class="o_we_bg_brand_primary">Add Item</we-button>
</we-row>
```

JavaScript handler:
```javascript
addItem: function(previewMode, widgetValue, params) {
    let $items = this.$target.find('.feature-item');
    let $lastItem = $items.last();
    if ($lastItem.length) {
        $lastItem.clone().appendTo($lastItem.parent());
    }
},
```

### Color Picker

```xml
<we-colorpicker string="Background Color"
                data-css-property="background-color"
                data-color-prefix="bg-"/>
```

### Image Selector

```xml
<we-row string="Background Image">
    <we-button data-select-image="true">Change Image</we-button>
</we-row>
```

### Toggle Option

```xml
<we-checkbox string="Show Shadow">
    <we-button data-toggle-class="shadow-lg"/>
</we-checkbox>
```

## Snippet Registration Patterns

### Odoo 17 and Earlier

```xml
<template id="s_<name>_insert" inherit_id="website.snippets">
    <xpath expr="//div[@id='snippet_effect']//t[@t-snippet][last()]" position="after">
        <t t-snippet="module.s_<name>"
           string="<Snippet Name>"
           t-thumbnail="/module/static/img/snippets/<name>.svg"/>
    </xpath>
</template>
```

### Odoo 18/19 with Groups

```xml
<!-- Create or use existing group -->
<template id="snippet_group_custom" inherit_id="website.snippets">
    <xpath expr="//div[@id='snippet_groups']" position="inside">
        <t snippet-group="custom"
           t-snippet="website.s_snippet_group"
           string="Custom"/>
    </xpath>
</template>

<!-- Register snippet -->
<template id="s_<name>_insert" inherit_id="website.snippets">
    <xpath expr="//div[@id='snippet_structure']/*[1]" position="before">
        <t t-snippet="module.s_<name>"
           string="<Snippet Name>"
           group="custom"
           t-thumbnail="/module/static/img/snippets/<name>.svg"/>
    </xpath>
</template>
```

## JavaScript Option Handler Patterns

### Basic Options Class

```javascript
/** @odoo-module **/

import options from "@web_editor/js/editor/snippets.options";

options.registry.SnippetName = options.Class.extend({
    /**
     * Lifecycle: When option panel is opened
     */
    start: function() {
        // Initialize options
        return this._super.apply(this, arguments);
    },

    /**
     * Add item handler
     */
    addItem: function(previewMode, widgetValue, params) {
        let $items = this.$target.find('.item-selector');
        let $lastItem = $items.last();

        if ($lastItem.length) {
            let $newItem = $lastItem.clone();
            $newItem.appendTo($lastItem.parent());
        }
    },

    /**
     * Custom select handler
     */
    selectLayout: function(previewMode, widgetValue, params) {
        let layout = params.optionsPossibleValues[widgetValue];
        this.$target.removeClass('layout-default layout-centered layout-wide');
        this.$target.addClass(layout);
    },
});
```

### Advanced: With State Management

```javascript
options.registry.AdvancedSnippet = options.Class.extend({
    start: function() {
        this.activeIndex = 0;
        this.$items = this.$target.find('.carousel-item');
        return this._super.apply(this, arguments);
    },

    addItem: function(previewMode, widgetValue, params) {
        let $lastItem = this.$items.last();
        let $newItem = $lastItem.clone();

        // Remove active class
        $newItem.removeClass('active');

        // Append to carousel
        $newItem.appendTo(this.$target.find('.carousel-inner'));

        // Update items cache
        this.$items = this.$target.find('.carousel-item');
    },

    removeItem: function(previewMode, widgetValue, params) {
        if (this.$items.length > 1) {
            this.$items.last().remove();
            this.$items = this.$target.find('.carousel-item');
        }
    },
});
```

## Dynamic Snippets with RPC

### Pattern: Load Data from Server

```javascript
/** @odoo-module **/

import PublicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

const DynamicSnippet = PublicWidget.Widget.extend({
    selector: '.s_dynamic_snippet',

    async willStart() {
        // Fetch data before rendering
        this.data = await this._fetchData();
        return this._super(...arguments);
    },

    start() {
        // Render with fetched data
        this._renderContent();
        return this._super(...arguments);
    },

    async _fetchData() {
        return await jsonrpc('/my/api/route', {
            limit: 10,
            category: this.$el.data('category'),
        });
    },

    _renderContent() {
        // Use QWeb or jQuery to render
        this.data.items.forEach(item => {
            let $item = $('<div>').text(item.name);
            this.$el.find('.items-container').append($item);
        });
    },
});

PublicWidget.registry.DynamicSnippet = DynamicSnippet;
```

## Accessibility Patterns

### ARIA Labels

```xml
<section class="s_features" role="region" aria-label="Features">
    <div class="container">
        <h2 id="features-heading">Our Features</h2>
        <div class="row" role="list" aria-labelledby="features-heading">
            <div class="col-lg-4" role="listitem">
                <!-- Feature content -->
            </div>
        </div>
    </div>
</section>
```

### Keyboard Navigation

```xml
<button class="carousel-control-prev"
        type="button"
        data-bs-target="#carousel"
        data-bs-slide="prev"
        aria-label="Previous slide">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
</button>
```

### Alt Text for Images

```xml
<img src="/web/image/product.jpg"
     class="img-fluid"
     alt="Product demonstration showing key features"/>
```

## Performance Patterns

### Lazy Loading Images

```xml
<img src="/web/image/placeholder.jpg"
     data-src="/web/image/actual-image.jpg"
     class="img-fluid lazy"
     loading="lazy"
     alt="Description"/>
```

### Optimized Image URLs

```xml
<!-- Use Odoo's image route with size -->
<img src="/website/image/product.template/123/image_1024"
     class="img-fluid"
     alt="Product"/>
```

### Defer Non-Critical Scripts

```javascript
// In snippet options JS
async willStart() {
    // Only load heavy library when needed
    if (this.$target.hasClass('needs-chart')) {
        await this._loadChartLibrary();
    }
    return this._super(...arguments);
}
```

## SEO Patterns

### Semantic HTML

```xml
<article class="s_blog_post">
    <header>
        <h1>Article Title</h1>
        <time datetime="2024-01-01">January 1, 2024</time>
    </header>

    <section>
        <h2>Section Heading</h2>
        <p>Content</p>
    </section>

    <footer>
        <p>Author information</p>
    </footer>
</article>
```

### Structured Data

```xml
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Product Name",
    "image": "/web/image/product.jpg",
    "description": "Product description"
}
</script>
```

## Testing Checklist

- [ ] Snippet appears in correct category
- [ ] Drag-and-drop works
- [ ] All options function correctly
- [ ] Responsive on all breakpoints
- [ ] Accessible (keyboard navigation, screen readers)
- [ ] No console errors
- [ ] Images load correctly
- [ ] Links work as expected
- [ ] Text is editable in website builder
- [ ] Can be duplicated
- [ ] Can be deleted
- [ ] Styling doesn't conflict with theme
- [ ] Works with different color schemes
- [ ] Performs well (no lag)
