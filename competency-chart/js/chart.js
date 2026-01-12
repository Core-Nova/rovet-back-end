/**
 * Chart Renderer - Chart.js radar chart rendering
 */

const ChartRenderer = {
  chart: null,
  canvas: null,

  /**
   * Initialize the chart
   */
  init() {
    this.canvas = document.getElementById('radarChart');
    this.registerPlugins();
    this.update();
  },

  /**
   * Register custom Chart.js plugins
   */
  registerPlugins() {
    Chart.register(this.createLevelLabelsPlugin());
  },

  /**
   * Create the level labels plugin
   */
  createLevelLabelsPlugin() {
    return {
      id: 'levelLabels',
      afterDraw: (chart) => this.drawLevelLabels(chart)
    };
  },

  /**
   * Draw level labels along each axis
   */
  drawLevelLabels(chart) {
    const state = ChartConfig.state;
    
    if (!state.showLevelLabels) return;

    const ctx = chart.ctx;
    const scale = chart.scales.r;
    const centerX = scale.xCenter;
    const centerY = scale.yCenter;
    const maxRadius = scale.drawingArea;
    const axisCount = state.axes.length;
    const fontSize = document.getElementById('labelFontSize')?.value || '11';

    ctx.save();
    ctx.font = `${fontSize}px "DM Sans", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'rgba(100, 116, 139, 0.5)';

    state.axes.forEach((axis, axisIndex) => {
      this.drawAxisLabels(ctx, axis, axisIndex, {
        centerX,
        centerY,
        maxRadius,
        axisCount,
        maxValue: state.maxValue
      });
    });

    ctx.restore();
  },

  /**
   * Draw labels for a single axis
   */
  drawAxisLabels(ctx, axis, axisIndex, geometry) {
    const { centerX, centerY, maxRadius, axisCount, maxValue } = geometry;
    const levels = ChartConfig.state.levels[axis] || [];
    const angleRad = (Math.PI * 2 * axisIndex / axisCount) - Math.PI / 2;

    levels.forEach((levelText, levelIndex) => {
      const position = this.calculateLabelPosition(
        levelIndex + 1,
        maxValue,
        maxRadius,
        angleRad,
        centerX,
        centerY
      );

      ctx.fillText(levelText, position.x, position.y);
    });
  },

  /**
   * Calculate label position
   */
  calculateLabelPosition(levelValue, maxValue, maxRadius, angleRad, centerX, centerY) {
    const radius = (levelValue / maxValue) * maxRadius;
    const x = centerX + Math.cos(angleRad) * radius;
    const y = centerY + Math.sin(angleRad) * radius;

    // Offset perpendicular to axis for readability
    const perpAngle = angleRad + Math.PI / 2;
    const offsetDistance = 10;

    return {
      x: x + Math.cos(perpAngle) * offsetDistance,
      y: y + Math.sin(perpAngle) * offsetDistance
    };
  },

  /**
   * Update the entire chart (recreate)
   */
  update() {
    if (this.chart) {
      this.chart.destroy();
    }

    const ctx = this.canvas.getContext('2d');
    const datasets = this.buildDatasets();
    const options = this.buildOptions();

    this.chart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ChartConfig.state.axes,
        datasets
      },
      options
    });
  },

  /**
   * Update only chart data (no recreation)
   */
  updateData() {
    if (!this.chart) {
      this.update();
      return;
    }

    this.chart.data.datasets = this.buildDatasets();
    this.chart.update('none');
  },

  /**
   * Build datasets for Chart.js
   */
  buildDatasets() {
    return ChartConfig.state.datasets
      .filter(ds => ds.visible)
      .map(ds => this.createDatasetConfig(ds));
  },

  /**
   * Create Chart.js dataset configuration
   */
  createDatasetConfig(dataset) {
    return {
      label: dataset.name,
      data: dataset.values,
      backgroundColor: dataset.color + '40',
      borderColor: dataset.color,
      borderWidth: 2,
      pointBackgroundColor: dataset.color,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 8,
      pointHoverRadius: 12,
      pointHitRadius: 15
    };
  },

  /**
   * Build Chart.js options
   */
  buildOptions() {
    const state = ChartConfig.state;

    return {
      responsive: true,
      maintainAspectRatio: true,
      animation: false,
      transitions: {
        active: { animation: { duration: 0 } }
      },
      plugins: {
        legend: { display: false },
        tooltip: this.buildTooltipOptions()
      },
      scales: {
        r: this.buildScaleOptions(state)
      }
    };
  },

  /**
   * Build tooltip options
   */
  buildTooltipOptions() {
    return {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleFont: { size: 14, weight: 'bold' },
      bodyFont: { size: 12 },
      padding: 12,
      callbacks: {
        label: (context) => this.formatTooltipLabel(context)
      }
    };
  },

  /**
   * Format tooltip label
   */
  formatTooltipLabel(context) {
    const state = ChartConfig.state;
    const axis = state.axes[context.dataIndex];
    const value = context.raw;
    const levels = state.levels[axis] || [];
    const levelName = levels[value - 1] || `Level ${value}`;

    return `${context.dataset.label}: ${levelName} (${value}/${state.maxValue})`;
  },

  /**
   * Build scale options
   */
  buildScaleOptions(state) {
    return {
      min: 0,
      max: state.maxValue,
      beginAtZero: true,
      ticks: {
        stepSize: 1,
        display: !state.showLevelLabels,
        font: { size: 10 },
        color: '#94a3b8',
        backdropColor: 'transparent'
      },
      grid: {
        color: '#e2e8f0',
        circular: true
      },
      angleLines: {
        color: '#cbd5e1'
      },
      pointLabels: {
        font: { size: 13, weight: '600' },
        color: '#334155',
        padding: state.showLevelLabels ? 25 : 15
      }
    };
  },

  /**
   * Download chart as image
   */
  downloadImage(format) {
    const resolution = parseInt(document.getElementById('resolution')?.value || '2');
    const bgOption = document.getElementById('bgOption')?.value || 'white';

    const exportCanvas = this.createExportCanvas(resolution, bgOption);
    const filename = this.generateFilename(format);

    this.triggerDownload(exportCanvas, filename);
  },

  /**
   * Create export canvas with specified resolution
   */
  createExportCanvas(resolution, bgOption) {
    const exportCanvas = document.createElement('canvas');
    const ctx = exportCanvas.getContext('2d');

    exportCanvas.width = this.canvas.width * resolution;
    exportCanvas.height = this.canvas.height * resolution;

    // Draw background
    if (bgOption !== 'transparent') {
      ctx.fillStyle = bgOption;
      ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
    }

    // Scale and draw original canvas
    ctx.scale(resolution, resolution);
    ctx.drawImage(this.canvas, 0, 0);

    return exportCanvas;
  },

  /**
   * Generate filename for download
   */
  generateFilename(format) {
    const title = ChartConfig.state.title
      .replace(/\s+/g, '-')
      .toLowerCase();
    const extension = format === 'svg' ? '-hires.png' : '.png';
    
    return `${title}-chart${extension}`;
  },

  /**
   * Trigger file download
   */
  triggerDownload(canvas, filename) {
    const link = document.createElement('a');
    link.download = filename;
    link.href = canvas.toDataURL('image/png', 1.0);
    link.click();
  }
};

