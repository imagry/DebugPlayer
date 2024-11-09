# Overview of Each File and Integration Points

## fsm_data_interface.py:

This file defines DataInterface, which generates and loads mock data for the FSM and is used to provide a DataFrame of transitions.
Key methods include load_mock_data for data generation, and get_dataframe, get_states, and get_transitions for data access​(fsm_data_interface).

## fsm_data_objects.py:

Contains the core FSM structure (FSM), as well as Node and Edge classes for graph representation.
Node represents a graph node, with a highlight feature, and Edge represents transitions between nodes, including a glow effect when highlighted.
These components interact directly with GraphVisualizer for graphical display​(fsm_data_objects)​(fsm_data_objects)​(fsm_data_objects).

## graph_visualizer.py:

This class visualizes the FSM graph using QGraphicsScene and QGraphicsView.
It includes methods for applying layouts, loading nodes and edges, and highlighting transitions.
load_graph uses FSM’s data to instantiate Node and Edge objects and map them to FSM states and transitions, while apply_layout arranges them on the scene using various NetworkX layouts​(graph_visualizer).

## fsm_main_window.py:

Defines MainWindow, setting up the main UI, including layout controls and a slider to simulate state traversal.
It connects UI elements to GraphVisualizer methods, such as changing layouts and updating FSM states through a slider. The slider calls update_fsm_state to track and highlight traversed edges​(fsm_main_window).

## fsm_main.py:

Entry point to initialize and run the application. This script sets up MainWindow and starts the Qt application loop​(fsm_main).