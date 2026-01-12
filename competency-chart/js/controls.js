/**
 * UI Controls - Rendering and handling of sidebar controls
 */

const Controls = {
  /**
   * Render all control sections
   */
  renderAll() {
    this.renderAxes();
    this.renderLevels();
    this.renderDatasets();
    this.renderDatasetToggles();
    this.renderLegend();
  },

  // =================== AXES ===================

  /**
   * Render axes list
   */
  renderAxes() {
    const container = document.getElementById('axesList');
    if (!container) return;

    container.innerHTML = ChartConfig.state.axes
      .map((axis, index) => this.createAxisItemHTML(axis, index))
      .join('');
  },

  /**
   * Create HTML for a single axis item
   */
  createAxisItemHTML(axis, index) {
    return `
      <div class="axis-item">
        <input 
          type="text" 
          class="form-input" 
          value="${axis}" 
          onchange="Controls.updateAxisName(${index}, this.value)"
        >
        <button 
          class="btn btn--danger btn--small" 
          onclick="Controls.removeAxis(${index})"
        >✕</button>
      </div>
    `;
  },

  /**
   * Add a new axis
   */
  addAxis() {
    const state = ChartConfig.state;
    const newAxisName = ChartConfig.generateUniqueAxisName();

    state.axes.push(newAxisName);
    state.levels[newAxisName] = ['Level 1', 'Level 2', 'Level 3'];
    state.datasets.forEach(ds => ds.values.push(0));

    ChartConfig.updateMaxValueIfNeeded();

    this.renderAll();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Remove an axis by index
   */
  removeAxis(index) {
    const state = ChartConfig.state;

    if (state.axes.length <= 3) {
      alert('Minimum 3 axes required');
      return;
    }

    const axisName = state.axes[index];

    state.axes.splice(index, 1);
    delete state.levels[axisName];
    state.datasets.forEach(ds => ds.values.splice(index, 1));

    this.renderAll();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Update axis name
   */
  updateAxisName(index, newName) {
    const state = ChartConfig.state;
    const trimmedName = newName.trim();

    if (!trimmedName) {
      this.renderAxes();
      return;
    }

    const oldName = state.axes[index];
    state.axes[index] = trimmedName;

    if (state.levels[oldName]) {
      state.levels[trimmedName] = state.levels[oldName];
      delete state.levels[oldName];
    }

    // Update selector if it was showing the old name
    const selector = document.getElementById('selectedAxis');
    if (selector && selector.value === oldName) {
      selector.value = trimmedName;
    }

    this.renderLevels();
    this.renderDatasets();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  // =================== LEVELS ===================

  /**
   * Render levels editor
   */
  renderLevels() {
    const selector = document.getElementById('selectedAxis');
    const container = document.getElementById('levelsList');
    
    if (!selector || !container) return;

    const selectedAxis = this.getValidSelectedAxis(selector);
    this.updateAxisSelector(selector, selectedAxis);
    this.renderLevelsList(container, selectedAxis);
  },

  /**
   * Get a valid selected axis (current or first available)
   */
  getValidSelectedAxis(selector) {
    const currentSelection = selector.value;
    const axes = ChartConfig.state.axes;

    return axes.includes(currentSelection) ? currentSelection : axes[0];
  },

  /**
   * Update the axis selector dropdown
   */
  updateAxisSelector(selector, selectedAxis) {
    selector.innerHTML = ChartConfig.state.axes
      .map(axis => {
        const isSelected = axis === selectedAxis ? 'selected' : '';
        return `<option value="${axis}" ${isSelected}>${axis}</option>`;
      })
      .join('');
  },

  /**
   * Render the levels list for selected axis
   */
  renderLevelsList(container, selectedAxis) {
    const levels = ChartConfig.state.levels[selectedAxis] || [];

    if (levels.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          No levels defined. Click "+ Add Level" to add.
        </div>
      `;
      return;
    }

    container.innerHTML = levels
      .map((level, index) => this.createLevelItemHTML(selectedAxis, level, index))
      .join('');
  },

  /**
   * Create HTML for a single level item
   */
  createLevelItemHTML(axis, level, index) {
    return `
      <div class="level-item">
        <span class="level-item__number">${index + 1}</span>
        <input 
          type="text" 
          class="form-input form-input--small" 
          value="${level}" 
          onchange="Controls.updateLevelName('${axis}', ${index}, this.value)"
        >
      </div>
    `;
  },

  /**
   * Update a level name
   */
  updateLevelName(axis, index, value) {
    ChartConfig.state.levels[axis][index] = value;
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Add a new level to selected axis
   */
  addLevel() {
    const selector = document.getElementById('selectedAxis');
    const selectedAxis = selector?.value;

    if (!selectedAxis) return;

    const state = ChartConfig.state;

    if (!state.levels[selectedAxis]) {
      state.levels[selectedAxis] = [];
    }

    const levelNum = state.levels[selectedAxis].length + 1;
    state.levels[selectedAxis].push(`Level ${levelNum}`);

    ChartConfig.updateMaxValueIfNeeded();

    this.renderLevels();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Remove last level from selected axis
   */
  removeLevel() {
    const selector = document.getElementById('selectedAxis');
    const selectedAxis = selector?.value;

    if (!selectedAxis) return;

    const levels = ChartConfig.state.levels[selectedAxis];

    if (levels && levels.length > 1) {
      levels.pop();
      this.renderLevels();
      ChartRenderer.update();
      Storage.saveToLocalStorage();
    }
  },

  // =================== DATASETS ===================

  /**
   * Render dataset cards
   */
  renderDatasets() {
    const container = document.getElementById('datasetsContainer');
    if (!container) return;

    container.innerHTML = ChartConfig.state.datasets
      .map((dataset, index) => this.createDatasetCardHTML(dataset, index))
      .join('');
  },

  /**
   * Create HTML for a dataset card
   */
  createDatasetCardHTML(dataset, datasetIndex) {
    const hiddenClass = dataset.visible ? '' : 'is-hidden';
    const valuesHTML = this.createDatasetValuesHTML(dataset, datasetIndex);
    const removeBtn = ChartConfig.state.datasets.length > 1
      ? `<button class="btn btn--danger btn--small" onclick="Controls.removeDataset(${datasetIndex})">✕</button>`
      : '';

    return `
      <div class="dataset-card ${hiddenClass}">
        <div class="dataset-card__header">
          <div class="dataset-card__name">
            <span class="color-dot" style="background: ${dataset.color}"></span>
            <input 
              type="text" 
              class="dataset-card__name-input" 
              value="${dataset.name}" 
              onchange="Controls.updateDatasetName(${datasetIndex}, this.value)"
            >
          </div>
          <div class="dataset-card__actions">
            <input 
              type="color" 
              class="color-picker" 
              value="${dataset.color}" 
              onchange="Controls.updateDatasetColor(${datasetIndex}, this.value)"
            >
            ${removeBtn}
          </div>
        </div>
        <div class="dataset-card__values">
          ${valuesHTML}
        </div>
      </div>
    `;
  },

  /**
   * Create HTML for dataset value inputs
   */
  createDatasetValuesHTML(dataset, datasetIndex) {
    return ChartConfig.state.axes
      .map((axis, axisIndex) => `
        <div class="value-input">
          <label class="value-input__label">${axis}</label>
          <input 
            type="number" 
            class="form-input form-input--small"
            min="0" 
            max="${ChartConfig.state.maxValue}" 
            value="${dataset.values[axisIndex] || 0}" 
            onchange="Controls.updateDatasetValue(${datasetIndex}, ${axisIndex}, this.value)"
          >
        </div>
      `)
      .join('');
  },

  /**
   * Add a new dataset
   */
  addDataset() {
    const state = ChartConfig.state;
    const newDataset = {
      name: `Dataset ${state.datasets.length + 1}`,
      color: ChartConfig.getNextColor(),
      values: state.axes.map(() => 0),
      visible: true
    };

    state.datasets.push(newDataset);

    this.renderAll();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Remove a dataset by index
   */
  removeDataset(index) {
    ChartConfig.state.datasets.splice(index, 1);

    this.renderAll();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Update dataset name
   */
  updateDatasetName(index, name) {
    ChartConfig.state.datasets[index].name = name;
    this.renderDatasetToggles();
    this.renderLegend();
    Storage.saveToLocalStorage();
  },

  /**
   * Update dataset color
   */
  updateDatasetColor(index, color) {
    ChartConfig.state.datasets[index].color = color;
    this.renderDatasetToggles();
    this.renderLegend();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Update a dataset value
   */
  updateDatasetValue(datasetIndex, axisIndex, value) {
    ChartConfig.state.datasets[datasetIndex].values[axisIndex] = parseInt(value) || 0;
    ChartRenderer.updateData();
    Storage.saveToLocalStorage();
  },

  /**
   * Toggle dataset visibility
   */
  toggleDataset(index) {
    ChartConfig.state.datasets[index].visible = !ChartConfig.state.datasets[index].visible;

    this.renderDatasetToggles();
    this.renderDatasets();
    this.renderLegend();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Render dataset toggle buttons
   */
  renderDatasetToggles() {
    const container = document.getElementById('datasetToggles');
    if (!container) return;

    container.innerHTML = ChartConfig.state.datasets
      .map((ds, index) => {
        const activeClass = ds.visible ? 'is-active' : '';
        return `
          <button 
            class="toggle-btn ${activeClass}" 
            onclick="Controls.toggleDataset(${index})"
            style="border-left: 3px solid ${ds.color}"
          >
            ${ds.name}
          </button>
        `;
      })
      .join('');
  },

  /**
   * Render legend
   */
  renderLegend() {
    const container = document.getElementById('legendPreview');
    if (!container) return;

    container.innerHTML = ChartConfig.state.datasets
      .filter(ds => ds.visible)
      .map(ds => `
        <div class="legend__item">
          <span class="legend__line" style="background: ${ds.color}"></span>
          ${ds.name}
        </div>
      `)
      .join('');
  },

  // =================== GENERAL CONTROLS ===================

  /**
   * Update chart title
   */
  updateTitle() {
    const input = document.getElementById('chartTitle');
    const display = document.getElementById('chartTitleDisplay');

    if (input) {
      ChartConfig.state.title = input.value;
    }
    if (display) {
      display.textContent = ChartConfig.state.title;
    }

    Storage.saveToLocalStorage();
  },

  /**
   * Toggle label display mode
   */
  toggleLabelMode() {
    const mode = document.getElementById('labelMode')?.value;
    ChartConfig.state.showLevelLabels = mode === 'text';
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Set chart zoom level
   */
  setChartZoom() {
    const zoom = document.getElementById('chartZoom')?.value || '1';
    const container = document.querySelector('.chart-container');
    
    if (container) {
      container.style.transform = `scale(${zoom})`;
    }
  },

  /**
   * Load a preset configuration
   */
  loadPreset(presetName) {
    const preset = ChartConfig.presets[presetName];
    if (!preset) return;

    const state = ChartConfig.state;

    state.axes = [...preset.axes];
    state.levels = JSON.parse(JSON.stringify(preset.levels));
    state.maxValue = preset.maxValue;

    // Generate varied values for each dataset
    state.datasets = [
      {
        name: 'Self-Evaluation',
        color: '#3b82f6',
        values: preset.axes.map(() => this.randomValue(2, preset.maxValue - 2)),
        visible: true
      },
      {
        name: 'Manager',
        color: '#10b981',
        values: preset.axes.map(() => this.randomValue(2, preset.maxValue - 2)),
        visible: true
      },
      {
        name: 'Goal',
        color: '#f59e0b',
        values: preset.axes.map(() => this.randomValue(preset.maxValue - 2, preset.maxValue)),
        visible: true
      }
    ];

    this.renderAll();
    ChartRenderer.update();
    Storage.saveToLocalStorage();
  },

  /**
   * Generate random value in range
   */
  randomValue(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  },

  /**
   * Reset chart to default
   */
  resetChart() {
    Storage.clearLocalStorage();

    this.loadPreset('engineering');

    // Reset UI elements
    const elements = {
      chartTitle: document.getElementById('chartTitle'),
      labelMode: document.getElementById('labelMode'),
      labelFontSize: document.getElementById('labelFontSize'),
      chartZoom: document.getElementById('chartZoom')
    };

    if (elements.chartTitle) elements.chartTitle.value = 'Competency Review Chart';
    if (elements.labelMode) elements.labelMode.value = 'text';
    if (elements.labelFontSize) elements.labelFontSize.value = '11';
    if (elements.chartZoom) elements.chartZoom.value = '1';

    ChartConfig.state.showLevelLabels = true;
    this.setChartZoom();
    this.updateTitle();
  }
};

