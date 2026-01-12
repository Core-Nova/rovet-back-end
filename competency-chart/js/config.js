/**
 * Chart configuration and state management
 */

const ChartConfig = {
  // Current chart state
  state: {
    title: 'Competency Review Chart',
    axes: ['People', 'Process', 'Product', 'System', 'Technology', 'Influence'],
    levels: {
      'People': ['Supports', 'Learns', 'Follows', 'Mentors', 'Coordinates', 'Manages'],
      'Process': ['Explores', 'Adopts', 'Designs', 'Enforces', 'Challenges', 'Adjusts', 'Defines'],
      'Product': ['Validates', 'Iterates', 'Scales', 'Innovates'],
      'System': ['Owns', 'Evolves', 'Leads'],
      'Technology': ['Specializes', 'Evangelizes', 'Masters', 'Creates'],
      'Influence': ['Team', 'Multiple Teams', 'Company', 'Community']
    },
    datasets: [
      {
        name: 'Self-Evaluation',
        color: '#3b82f6',
        values: [4, 5, 3, 2, 4, 3],
        visible: true
      },
      {
        name: 'Manager',
        color: '#10b981',
        values: [5, 4, 4, 3, 3, 2],
        visible: true
      },
      {
        name: 'Goal',
        color: '#f59e0b',
        values: [6, 6, 5, 4, 5, 4],
        visible: true
      }
    ],
    maxValue: 7,
    showLevelLabels: true
  },

  // Available color palette for datasets
  datasetColors: [
    '#3b82f6', // Blue
    '#10b981', // Green
    '#f59e0b', // Orange
    '#ef4444', // Red
    '#8b5cf6', // Purple
    '#ec4899'  // Pink
  ],

  // Preset configurations
  presets: {
    engineering: {
      axes: ['People', 'Process', 'Product', 'System', 'Technology', 'Influence'],
      levels: {
        'People': ['Supports', 'Learns', 'Follows', 'Mentors', 'Coordinates', 'Manages'],
        'Process': ['Explores', 'Adopts', 'Follows', 'Enforces', 'Challenges', 'Adjusts', 'Defines'],
        'Product': ['Validates', 'Iterates', 'Scales', 'Innovates'],
        'System': ['Subsystem', 'Owns', 'Evolves', 'Leads'],
        'Technology': ['Specializes', 'Evangelizes', 'Masters', 'Creates'],
        'Influence': ['Team', 'Multiple Teams', 'Company', 'Community']
      },
      maxValue: 7
    },

    leadership: {
      axes: ['Vision', 'Strategy', 'Execution', 'People', 'Communication', 'Impact'],
      levels: {
        'Vision': ['Follows', 'Contributes', 'Shapes', 'Defines', 'Inspires'],
        'Strategy': ['Executes', 'Plans', 'Designs', 'Drives'],
        'Execution': ['Delivers', 'Coordinates', 'Leads', 'Scales'],
        'People': ['Supports', 'Mentors', 'Develops', 'Builds Teams'],
        'Communication': ['Informs', 'Influences', 'Aligns', 'Inspires'],
        'Impact': ['Team', 'Department', 'Organization', 'Industry']
      },
      maxValue: 5
    },

    product: {
      axes: ['Discovery', 'Strategy', 'Execution', 'Analytics', 'Stakeholders', 'Technical'],
      levels: {
        'Discovery': ['Learns', 'Researches', 'Validates', 'Innovates'],
        'Strategy': ['Understands', 'Contributes', 'Owns', 'Defines'],
        'Execution': ['Ships', 'Leads', 'Scales', 'Transforms'],
        'Analytics': ['Tracks', 'Analyzes', 'Predicts', 'Optimizes'],
        'Stakeholders': ['Updates', 'Aligns', 'Influences', 'Leads'],
        'Technical': ['Understands', 'Collaborates', 'Guides', 'Architects']
      },
      maxValue: 5
    },

    design: {
      axes: ['Craft', 'Process', 'Research', 'Systems', 'Influence', 'Leadership'],
      levels: {
        'Craft': ['Learning', 'Practicing', 'Expert', 'Master'],
        'Process': ['Follows', 'Adapts', 'Improves', 'Defines'],
        'Research': ['Observes', 'Analyzes', 'Leads', 'Innovates'],
        'Systems': ['Uses', 'Contributes', 'Owns', 'Architects'],
        'Influence': ['Team', 'Product', 'Organization', 'Industry'],
        'Leadership': ['Self', 'Others', 'Team', 'Organization']
      },
      maxValue: 5
    },

    custom: {
      axes: ['Axis 1', 'Axis 2', 'Axis 3', 'Axis 4', 'Axis 5', 'Axis 6'],
      levels: {
        'Axis 1': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
        'Axis 2': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
        'Axis 3': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
        'Axis 4': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
        'Axis 5': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
        'Axis 6': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']
      },
      maxValue: 5
    }
  },

  /**
   * Get a color for a new dataset
   */
  getNextColor() {
    const usedColors = this.state.datasets.map(ds => ds.color);
    const availableColor = this.datasetColors.find(c => !usedColors.includes(c));
    return availableColor || this.datasetColors[this.state.datasets.length % this.datasetColors.length];
  },

  /**
   * Generate a unique axis name
   */
  generateUniqueAxisName() {
    let counter = this.state.axes.length + 1;
    let name = `Axis ${counter}`;
    
    while (this.state.axes.includes(name)) {
      counter++;
      name = `Axis ${counter}`;
    }
    
    return name;
  },

  /**
   * Calculate max levels across all axes
   */
  calculateMaxLevels() {
    return Math.max(
      ...this.state.axes.map(axis => (this.state.levels[axis] || []).length)
    );
  },

  /**
   * Update max value if levels exceed it
   */
  updateMaxValueIfNeeded() {
    const maxLevels = this.calculateMaxLevels();
    if (maxLevels > this.state.maxValue) {
      this.state.maxValue = maxLevels;
    }
  }
};

