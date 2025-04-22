# Debug Player Roadmap

## Overview

This roadmap outlines the development plan for the Playback Debug Tool, a framework designed to visualize and debug data from recording sessions. The tool uses plugins to load and process different data types, then visualizes them through customizable plot widgets.

## Current Architecture

The framework has a modular architecture with these key components:

1. **Core Components**
   - `PlotManager`: Central coordinator managing plugins, signals, and plots
   - `data_loader`: Handles parsing command-line arguments and loading data

2. **Plugin System**
   - Dynamically loaded from the plugins directory
   - Each plugin provides specific data signals (e.g., CarPosePlugin provides car_pose, route, etc.)
   - Plugins advertise their signals with metadata (type, access function)

3. **GUI Components**
   - Main window with dockable widgets
   - Temporal plots for time-series data
   - Spatial plots for 2D visualizations
   - Timestamp slider for navigating through the recording

4. **Data Flow**
   - PlotManager coordinates data requests from user interactions
   - Plugins provide data for specific timestamps
   - Plot widgets visualize the data

## Development Roadmap

### Phase 1: Foundation Strengthening (Current Focus)

**Objectives:**
- Stabilize the existing codebase
- Fix dependencies and environment issues
- Complete unfinished components
- Add comprehensive documentation and tests

**Tasks:**
1. **Environment Setup**
   - Fix QT dependencies (particularly QtCharts)
   - Ensure consistent environment configuration
   - Document installation process

2. **Core Stabilization**
   - Complete the plugin interface implementation
   - Add proper error handling to the data loading process
   - Implement proper signal type validation

3. **Testing Framework**
   - Implement unit tests for core components
   - Add integration tests for plugin system
   - Create test data for consistent testing

4. **Documentation**
   - Create comprehensive API documentation
   - Add inline code comments
   - Update README with setup and usage instructions

**Testing Criteria:**
- All core components have unit tests with >80% coverage
- System can load and visualize test data without errors
- Environment setup is reproducible on different machines

### Phase 2: Core Features Enhancement

**Objectives:**
- Enhance signal management
- Improve UI navigation and interaction
- Develop more flexible view system

**Tasks:**
1. **Signal Management**
   - Refactor signal registration to support hierarchical signal structure
   - Add signal metadata (units, description, valid ranges)
   - Implement signal filtering capabilities

2. **View System Improvements**
   - Create a view manager similar to the plot manager
   - Support multiple view types beyond plots (tables, text, custom visualizations)
   - Implement view templates for common visualization patterns

3. **UI Enhancements**
   - Implement bookmarking of interesting timestamps
   - Add a minimap for quick navigation through large datasets
   - Support for filtering and searching within signals

4. **Plugin System Enhancements**
   - Improve plugin discovery and validation
   - Add plugin versioning support
   - Create a plugin development guide

**Testing Criteria:**
- UI interactions are tested with automated UI testing
- Signal management is verified with comprehensive tests
- Plugin loading handles edge cases gracefully

### Phase 3: LLM Integration

**Objectives:**
- Add LLM-powered analysis capabilities
- Implement intelligent visualization suggestions
- Create interactive documentation

**Tasks:**
1. **Query Interface**
   - Implement natural language query interface for data analysis
   - Add automatic anomaly detection in signals
   - Generate natural language summaries of interesting data patterns

2. **Intelligent Visualization**
   - Add automatic suggestion of relevant visualizations
   - Implement smart correlation of signals across plugins
   - Create customized views based on detected patterns

3. **Interactive Documentation**
   - Build LLM-powered help system for explaining signals
   - Add context-aware tooltips and explanations
   - Implement tutorial mode for new users

4. **Analysis Tools**
   - Create pattern recognition for common issues
   - Implement automatic labeling of interesting timestamps
   - Add predictive insights based on historical data

**Testing Criteria:**
- LLM queries return relevant and accurate information
- Documentation is contextually appropriate
- Visualization suggestions improve user workflow

### Phase 4: Advanced Features

**Objectives:**
- Implement multi-view coordination
- Add annotation and collaboration tools
- Optimize performance for large datasets

**Tasks:**
1. **Multi-View Coordination**
   - Implement synchronized views with linked interactions
   - Add split-screen comparisons of different timestamps
   - Support custom layouts and saved configurations

2. **Collaboration Tools**
   - Add annotation capabilities for data points
   - Implement sharing of insights and findings
   - Create export functionality for reports

3. **Performance Optimizations**
   - Implement lazy loading for large datasets
   - Add caching mechanisms for frequently accessed data
   - Optimize plotting for large datasets

4. **Extended Plugin Ecosystem**
   - Create template plugins for common data types
   - Implement plugin marketplace or sharing mechanism
   - Add support for remote data sources

**Testing Criteria:**
- Performance benchmarks meet targets for large datasets
- Collaboration features work across different instances
- Plugin ecosystem is robust and extensible

## Development Practices

### Testing Strategy

1. **Unit Testing**
   - All core components must have unit tests
   - New features require tests before merging
   - Test coverage should be maintained above 80%

2. **Integration Testing**
   - Plugin system tested with mock plugins
   - UI functionality verified with automated tests
   - Data flow tested end-to-end

3. **Manual Testing**
   - Regular testing with real-world data
   - User interface testing for usability
   - Edge case validation

### Git Workflow

1. **Branching Strategy**
   - `main` branch contains stable releases
   - `develop` branch for integration
   - Feature branches for new development

2. **Commit Guidelines**
   - Atomic commits with descriptive messages
   - Reference issue numbers in commit messages
   - Commits should pass all tests

3. **Milestone Commits**
   - Major milestones tagged with version numbers
   - Changelog maintained for each milestone
   - Regular commits between milestones to track progress

## Success Criteria

- Tool successfully loads and visualizes diverse data types
- Users can efficiently navigate and analyze complex datasets
- Plugin system supports easy extension for new data sources
- Performance remains responsive with large datasets
- LLM integration provides valuable insights and assistance

## Timeline

- **Phase 1**: 4-6 weeks
- **Phase 2**: 6-8 weeks
- **Phase 3**: 8-10 weeks
- **Phase 4**: Ongoing development

*Note: This roadmap is a living document and may be adjusted as development progresses and priorities evolve.*
