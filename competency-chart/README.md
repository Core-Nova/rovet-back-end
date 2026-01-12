# Competency Review Chart Generator

A standalone tool to generate customizable radar/spider charts for skills assessment and competency reviews. Perfect for performance reviews, 1:1s, and team evaluations.

## Quick Start

Simply open the HTML file in your browser:

```bash
open local/tools/competency-chart/index.html
```

No server or installation required - it loads Chart.js from CDN and works entirely in the browser.

## Project Structure

```
competency-chart/
├── index.html              # Main HTML entry point
├── css/
│   ├── variables.css       # CSS custom properties (colors, spacing, etc.)
│   ├── base.css           # Reset and base styles
│   ├── components.css     # Reusable UI components (buttons, forms, cards)
│   └── layout.css         # Page layout and section styles
├── js/
│   ├── config.js          # Configuration state and presets
│   ├── storage.js         # localStorage and JSON export/import
│   ├── controls.js        # UI control rendering and event handlers
│   ├── chart.js           # Chart.js rendering and configuration
│   ├── drag.js            # Drag-to-adjust functionality
│   └── main.js            # Application initialization
└── README.md              # This file
```

## Features

### Chart Customization
- **6 axes by default** (People, Process, Product, System, Technology, Influence)
- **Multiple datasets** (Self-Evaluation, Manager, Goal) with different colors
- **Customizable level labels** for each axis
- **Drag-to-adjust** values directly on the chart

### Presets
- **Engineering** - Technical competency axes
- **Leadership** - Management competencies
- **Product** - Product management skills
- **Design** - Design competencies
- **Blank** - Start from scratch

### Export & Persistence
- **PNG Export** - Multiple resolutions (1x, 2x, 3x)
- **JSON Export** - Save configuration to file
- **JSON Import** - Load saved configurations
- **Auto-save** - Persists to localStorage on every change

### Display Options
- Chart size (80% - 150%)
- Label mode (Text or Numbers)
- Font size (9px - 15px)
- Background color

## Usage

### Basic Workflow

1. **Open** `index.html` in your browser
2. **Select a preset** or customize from scratch
3. **Edit axes** - Add, remove, rename competencies
4. **Edit levels** - Define level labels for each axis
5. **Adjust values** - Drag points or use number inputs
6. **Export** - Download as PNG or save as JSON

### Adding to Confluence

1. Click **⬇ PNG** to download the chart
2. In Confluence, click **Insert → Image**
3. Upload the downloaded PNG file

### Saving Your Configuration

1. Click **⬇ Save** to download a JSON file
2. Store the file for future use
3. Click **⬆ Load** to restore the configuration

## Architecture

### CSS Architecture

The CSS follows a component-based architecture with CSS custom properties:

- **variables.css** - Design tokens (colors, spacing, typography)
- **base.css** - Reset and foundational styles
- **components.css** - Reusable UI patterns (BEM-like naming)
- **layout.css** - Page structure and responsive design

### JavaScript Architecture

The JavaScript is organized into focused modules:

| Module | Responsibility |
|--------|---------------|
| `config.js` | State management and preset definitions |
| `storage.js` | Persistence (localStorage, file export/import) |
| `controls.js` | UI rendering and user interactions |
| `chart.js` | Chart.js configuration and rendering |
| `drag.js` | Drag interaction handling |
| `main.js` | Application initialization |

### Data Flow

```
User Action → Controls.js → ChartConfig.state → ChartRenderer.update()
                         ↓
                    Storage.saveToLocalStorage()
```

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Any modern browser with ES6+ support

## Dependencies

- [Chart.js 4.4.1](https://www.chartjs.org/) - Loaded from CDN
- [DM Sans](https://fonts.google.com/specimen/DM+Sans) - Google Fonts

## Customization

### Adding New Presets

Edit `js/config.js` and add to the `presets` object:

```javascript
myPreset: {
  axes: ['Axis 1', 'Axis 2', 'Axis 3'],
  levels: {
    'Axis 1': ['Level 1', 'Level 2', 'Level 3'],
    // ...
  },
  maxValue: 5
}
```

### Changing Colors

Edit `css/variables.css` to modify the color palette:

```css
:root {
  --color-primary: #your-color;
  /* ... */
}
```

### Adding Dataset Colors

Edit `js/config.js` and modify the `datasetColors` array.

## Code Review Notes

### Strengths
- Clean separation of concerns across modules
- Consistent naming conventions (BEM for CSS, descriptive for JS)
- Functions kept under 80 lines
- Meaningful variable names
- Good use of CSS custom properties for theming

### Potential Improvements
- Could add TypeScript for better type safety
- Consider using ES modules with import/export
- Could add unit tests for core functions
- Consider extracting HTML templates to separate files
