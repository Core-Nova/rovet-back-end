/**
 * Storage management - localStorage persistence and file export/import
 */

const Storage = {
  STORAGE_KEY: 'competency-chart-config',

  /**
   * Save current configuration to localStorage
   */
  saveToLocalStorage() {
    try {
      const saveData = {
        config: ChartConfig.state,
        settings: this.getUISettings()
      };
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(saveData));
    } catch (error) {
      console.warn('Could not save to localStorage:', error);
    }
  },

  /**
   * Load configuration from localStorage
   * @returns {boolean} Whether data was loaded successfully
   */
  loadFromLocalStorage() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      
      if (!saved) {
        return false;
      }

      const saveData = JSON.parse(saved);
      Object.assign(ChartConfig.state, saveData.config);

      // Restore UI settings after DOM is ready
      setTimeout(() => this.applyUISettings(saveData.settings), 0);

      return true;
    } catch (error) {
      console.warn('Could not load from localStorage:', error);
      return false;
    }
  },

  /**
   * Clear saved data from localStorage
   */
  clearLocalStorage() {
    localStorage.removeItem(this.STORAGE_KEY);
  },

  /**
   * Get current UI settings
   */
  getUISettings() {
    return {
      labelMode: document.getElementById('labelMode')?.value || 'text',
      labelFontSize: document.getElementById('labelFontSize')?.value || '11',
      chartZoom: document.getElementById('chartZoom')?.value || '1'
    };
  },

  /**
   * Apply UI settings to form elements
   */
  applyUISettings(settings) {
    if (!settings) return;

    const elements = {
      labelMode: document.getElementById('labelMode'),
      labelFontSize: document.getElementById('labelFontSize'),
      chartZoom: document.getElementById('chartZoom')
    };

    if (settings.labelMode && elements.labelMode) {
      elements.labelMode.value = settings.labelMode;
    }
    if (settings.labelFontSize && elements.labelFontSize) {
      elements.labelFontSize.value = settings.labelFontSize;
    }
    if (settings.chartZoom && elements.chartZoom) {
      elements.chartZoom.value = settings.chartZoom;
      Controls.setChartZoom();
    }
  },

  /**
   * Export configuration as JSON file
   */
  exportConfig() {
    const exportData = {
      version: 1,
      title: ChartConfig.state.title,
      axes: ChartConfig.state.axes,
      levels: ChartConfig.state.levels,
      datasets: ChartConfig.state.datasets.map(ds => ({
        name: ds.name,
        color: ds.color,
        values: ds.values,
        visible: ds.visible
      })),
      maxValue: ChartConfig.state.maxValue,
      showLevelLabels: ChartConfig.state.showLevelLabels,
      settings: this.getUISettings(),
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob(
      [JSON.stringify(exportData, null, 2)],
      { type: 'application/json' }
    );
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const filename = ChartConfig.state.title
      .replace(/\s+/g, '-')
      .toLowerCase();
    
    link.download = `${filename}-config.json`;
    link.href = url;
    link.click();
    
    URL.revokeObjectURL(url);
  },

  /**
   * Import configuration from JSON file
   */
  importConfig(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const importData = JSON.parse(e.target.result);
        this.validateAndApplyImport(importData);
      } catch (error) {
        alert('Error loading config: ' + error.message);
      }
    };

    reader.readAsText(file);

    // Reset file input so same file can be loaded again
    event.target.value = '';
  },

  /**
   * Validate imported data and apply it
   */
  validateAndApplyImport(importData) {
    // Validate axes
    if (!importData.axes || !Array.isArray(importData.axes)) {
      throw new Error('Missing or invalid axes');
    }

    // Validate datasets
    if (!importData.datasets || !Array.isArray(importData.datasets)) {
      throw new Error('Missing or invalid datasets');
    }

    // Validate dataset values match axes count
    for (const dataset of importData.datasets) {
      if (!dataset.values || dataset.values.length !== importData.axes.length) {
        throw new Error(`Dataset "${dataset.name}" has wrong number of values`);
      }
    }

    // Apply imported config
    this.applyImportedConfig(importData);

    // Update UI
    this.updateUIAfterImport();

    // Save and render
    Controls.renderAll();
    ChartRenderer.update();
    this.saveToLocalStorage();

    const summary = `${ChartConfig.state.axes.length} axes, ` +
                    `${ChartConfig.state.datasets.length} datasets`;
    alert(`Config loaded successfully!\n\n${summary}`);
  },

  /**
   * Apply imported configuration to state
   */
  applyImportedConfig(importData) {
    const state = ChartConfig.state;

    state.title = importData.title || 'Competency Review Chart';
    state.axes = [...importData.axes];
    state.levels = JSON.parse(JSON.stringify(importData.levels || {}));
    state.maxValue = importData.maxValue || 7;
    state.showLevelLabels = importData.showLevelLabels !== false;

    state.datasets = importData.datasets.map(ds => ({
      name: ds.name || 'Dataset',
      color: ds.color || '#3b82f6',
      values: [...ds.values],
      visible: ds.visible !== false
    }));

    // Ensure all axes have levels defined
    state.axes.forEach(axis => {
      if (!state.levels[axis]) {
        state.levels[axis] = ['Level 1', 'Level 2', 'Level 3'];
      }
    });
  },

  /**
   * Update UI elements after import
   */
  updateUIAfterImport() {
    const titleInput = document.getElementById('chartTitle');
    const titleDisplay = document.getElementById('chartTitleDisplay');

    if (titleInput) {
      titleInput.value = ChartConfig.state.title;
    }
    if (titleDisplay) {
      titleDisplay.textContent = ChartConfig.state.title;
    }
  }
};

