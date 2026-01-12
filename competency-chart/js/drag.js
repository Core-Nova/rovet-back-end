/**
 * Drag Handler - Handles drag interactions on chart data points
 */

const DragHandler = {
  // Drag state
  isDragging: false,
  activeDatasetIndex: null,
  activePointIndex: null,
  activeDatasetName: null,

  /**
   * Initialize drag event listeners
   */
  init() {
    const canvas = document.getElementById('radarChart');
    if (!canvas) return;

    this.setupMouseEvents(canvas);
    this.setupTouchEvents(canvas);
  },

  /**
   * Setup mouse event listeners
   */
  setupMouseEvents(canvas) {
    canvas.addEventListener('mousedown', (e) => this.handleDragStart(e));
    canvas.addEventListener('mousemove', (e) => this.handleDragMove(e));
    canvas.addEventListener('mouseup', (e) => this.handleDragEnd(e));
    canvas.addEventListener('mouseleave', (e) => this.handleDragEnd(e));
  },

  /**
   * Setup touch event listeners
   */
  setupTouchEvents(canvas) {
    const options = { passive: false };
    
    canvas.addEventListener('touchstart', (e) => this.handleDragStart(e), options);
    canvas.addEventListener('touchmove', (e) => this.handleDragMove(e), options);
    canvas.addEventListener('touchend', (e) => this.handleDragEnd(e));
    canvas.addEventListener('touchcancel', (e) => this.handleDragEnd(e));
  },

  /**
   * Handle drag start
   */
  handleDragStart(event) {
    const point = this.findPointAtEvent(event);
    
    if (!point) return;

    this.isDragging = true;
    this.activeDatasetIndex = point.originalDatasetIndex;
    this.activePointIndex = point.pointIndex;
    this.activeDatasetName = ChartConfig.state.datasets[point.originalDatasetIndex].name;

    event.preventDefault();
    ChartRenderer.chart.canvas.style.cursor = 'grabbing';
  },

  /**
   * Handle drag move
   */
  handleDragMove(event) {
    const canvas = ChartRenderer.chart?.canvas;
    if (!canvas) return;

    if (!this.isDragging) {
      this.updateHoverCursor(event, canvas);
      return;
    }

    event.preventDefault();

    const position = this.getEventPosition(event, canvas);
    const newValue = this.calculateValueFromPosition(position);

    this.updateDatasetValue(newValue);
    this.updateTooltip(event, canvas, newValue);
  },

  /**
   * Handle drag end
   */
  handleDragEnd(event) {
    if (!this.isDragging) return;

    this.isDragging = false;
    this.activeDatasetIndex = null;
    this.activePointIndex = null;
    this.activeDatasetName = null;

    ChartRenderer.chart.canvas.style.cursor = 'default';
    this.hideTooltip();

    Controls.renderDatasets();
    Storage.saveToLocalStorage();
  },

  /**
   * Find chart point at event position
   */
  findPointAtEvent(event) {
    const chart = ChartRenderer.chart;
    if (!chart) return null;

    const canvas = chart.canvas;
    const rect = canvas.getBoundingClientRect();
    const position = this.getEventPosition(event, canvas);

    return this.findNearestPoint(position, chart);
  },

  /**
   * Find the nearest point to a position
   */
  findNearestPoint(position, chart) {
    const visibleDatasets = ChartConfig.state.datasets
      .map((ds, index) => ({ ...ds, originalIndex: index }))
      .filter(ds => ds.visible);

    const hitRadius = 15;

    for (let di = 0; di < visibleDatasets.length; di++) {
      const dataset = visibleDatasets[di];

      for (let pi = 0; pi < ChartConfig.state.axes.length; pi++) {
        const meta = chart.getDatasetMeta(di);
        const point = meta.data[pi];

        if (!point) continue;

        const distance = Math.sqrt(
          Math.pow(position.x - point.x, 2) + 
          Math.pow(position.y - point.y, 2)
        );

        if (distance < hitRadius) {
          return {
            datasetIndex: di,
            originalDatasetIndex: dataset.originalIndex,
            pointIndex: pi
          };
        }
      }
    }

    return null;
  },

  /**
   * Get event position relative to canvas
   */
  getEventPosition(event, canvas) {
    const rect = canvas.getBoundingClientRect();
    const clientX = event.clientX || event.touches?.[0]?.clientX;
    const clientY = event.clientY || event.touches?.[0]?.clientY;

    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  },

  /**
   * Calculate value from drag position
   */
  calculateValueFromPosition(position) {
    const chart = ChartRenderer.chart;
    const scale = chart.scales.r;
    const centerX = scale.xCenter;
    const centerY = scale.yCenter;
    const maxRadius = scale.drawingArea;
    const maxValue = ChartConfig.state.maxValue;

    const distanceFromCenter = Math.sqrt(
      Math.pow(position.x - centerX, 2) + 
      Math.pow(position.y - centerY, 2)
    );

    let newValue = Math.round((distanceFromCenter / maxRadius) * maxValue);
    return Math.max(0, Math.min(maxValue, newValue));
  },

  /**
   * Update dataset value during drag
   */
  updateDatasetValue(newValue) {
    const state = ChartConfig.state;
    
    state.datasets[this.activeDatasetIndex].values[this.activePointIndex] = newValue;

    // Find chart dataset by name (handles sorting)
    const chartDatasetIndex = ChartRenderer.chart.data.datasets
      .findIndex(ds => ds.label === this.activeDatasetName);

    if (chartDatasetIndex !== -1) {
      ChartRenderer.chart.data.datasets[chartDatasetIndex].data[this.activePointIndex] = newValue;
      ChartRenderer.chart.update('none');
    }
  },

  /**
   * Update hover cursor when not dragging
   */
  updateHoverCursor(event, canvas) {
    const point = this.findPointAtEvent(event);
    canvas.style.cursor = point ? 'grab' : 'default';
    
    if (!point) {
      this.hideTooltip();
    }
  },

  /**
   * Update tooltip during drag
   */
  updateTooltip(event, canvas, value) {
    const tooltip = document.getElementById('dragTooltip');
    if (!tooltip) return;

    const position = this.getEventPosition(event, canvas);
    const axis = ChartConfig.state.axes[this.activePointIndex];
    const levels = ChartConfig.state.levels[axis] || [];
    const levelName = levels[value - 1] || `Level ${value}`;

    tooltip.innerHTML = `<strong>${axis}</strong>: ${levelName} (${value})`;
    tooltip.style.left = `${position.x}px`;
    tooltip.style.top = `${position.y - 15}px`;
    tooltip.classList.add('is-visible');
  },

  /**
   * Hide the drag tooltip
   */
  hideTooltip() {
    const tooltip = document.getElementById('dragTooltip');
    if (tooltip) {
      tooltip.classList.remove('is-visible');
    }
  }
};

