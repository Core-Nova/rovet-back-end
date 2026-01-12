/**
 * Main Application Entry Point
 */

const App = {
  /**
   * Initialize the application
   */
  init() {
    this.loadSavedState();
    this.renderUI();
    this.initializeChart();
    this.setupEventListeners();
    this.updateTitleDisplay();
  },

  /**
   * Load saved state from localStorage
   */
  loadSavedState() {
    this.hasStoredConfig = Storage.loadFromLocalStorage();
  },

  /**
   * Render all UI controls
   */
  renderUI() {
    Controls.renderAll();
  },

  /**
   * Initialize Chart.js chart and drag handling
   */
  initializeChart() {
    ChartRenderer.init();
    DragHandler.init();
  },

  /**
   * Setup global event listeners
   */
  setupEventListeners() {
    // File input for import
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
      fileInput.addEventListener('change', (e) => Storage.importConfig(e));
    }
  },

  /**
   * Update title display if loaded from storage
   */
  updateTitleDisplay() {
    if (!this.hasStoredConfig) return;

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

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => App.init());

