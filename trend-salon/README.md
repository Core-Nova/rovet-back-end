# TREND - Luxury Hairdressing Studio

A beautiful, static single-page website for TREND hairdressing studio with a baroque-inspired gold and white color palette.

## Features

- **Responsive Design** - Works beautifully on all devices (desktop, tablet, mobile)
- **Bilingual Support** - Toggle between English and Bulgarian
- **Automatic Gallery Slideshow** - Touch-enabled with swipe support
- **Smooth Scroll Navigation** - With active section highlighting
- **Google Maps Integration** - Embedded map for location
- **Google Reviews Link** - Direct link to leave reviews
- **Instagram Integration** - Social media link
- **No Dependencies** - Pure HTML, CSS, and vanilla JavaScript

## Pages/Sections

1. **Home** - Hero section with branding
2. **About** - Studio introduction and features
3. **Services** - Hair services offered
4. **Gallery** - Image slideshow (auto-rotating)
5. **Prices** - Detailed price list in BGN (лв.)
6. **Reviews** - Client testimonials with Google Reviews link
7. **Contact** - Address, phone, email, hours, and embedded Google Map

## How to Use

Simply open `index.html` in any modern web browser. No server required!

```bash
# Option 1: Double-click index.html

# Option 2: Open from terminal
open index.html        # macOS
start index.html       # Windows
xdg-open index.html    # Linux
```

## Customization

### To change the address/location:
1. Go to [Google Maps](https://maps.google.com)
2. Find your location
3. Click "Share" → "Embed a map"
4. Copy the iframe src URL
5. Replace the `src` in the `<iframe>` in the contact section

### To add real images:
1. Add images to the `images/` folder
2. Update the `.slide-image` elements in `index.html`:
```html
<div class="slide-image" style="background-image: url('images/your-image.jpg');"></div>
```

### To change colors:
Edit the CSS variables at the top of `styles.css`:
```css
:root {
    --gold-primary: #C9A227;
    --gold-light: #D4AF37;
    --burgundy: #722F37;
    /* etc. */
}
```

### To update contact info:
Edit the contact section in `index.html`:
- Address
- Phone number
- Email
- Working hours
- Social media links

### To add more languages:
Add `data-{langcode}` attributes to translatable elements and update the JavaScript.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## File Structure

```
trend-salon/
├── index.html      # Main HTML file
├── styles.css      # All styling
├── script.js       # JavaScript functionality
├── images/         # Place your images here
└── README.md       # This file
```

## Color Palette (Baroque Gold & White)

| Color | Hex | Usage |
|-------|-----|-------|
| Gold Primary | `#C9A227` | Accents, headings, buttons |
| Gold Light | `#D4AF37` | Hover states |
| Burgundy | `#722F37` | Baroque accent |
| White | `#FFFFFF` | Backgrounds |
| Cream | `#FAF8F0` | Section backgrounds |
| Charcoal | `#2C2C2C` | Text |
| Black | `#1A1A1A` | Dark sections, footer |

## License

Free to use and modify for your business.

---

✨ *TREND - Where elegance meets artistry* ✨
