import random
from datetime import datetime, timedelta
import pandas as pd

class DataInterface:
    """Interface for obtaining FSM data."""

    def __init__(self):
        self.dataframe = None
        self.states = set()
        self.transitions = []

    def load_mock_data(self, k=4, m=3, n=10, self_loops=False):
        """Generates and stores mock FSM data with configurable states and signals."""
        states = [f"S{i+1}" for i in range(k)]
        signals = [f"Signal{j+1}" for j in range(m)]
        data = []
        start_time = datetime.now()

        current_state = random.choice(states)
        for i in range(n):
            next_state = random.choice(states)
            if not self_loops:
                while next_state == current_state:
                    next_state = random.choice(states)

            selected_signals = {f"signal{j+1}": random.choice(signals) for j in range(m)}
            timestamp = start_time + timedelta(seconds=i * 10)
            data.append([timestamp, current_state, next_state, *selected_signals.values()])

            # Store the transition as ((source_state, dest_state), signals)
            self.transitions.append(((current_state, next_state), selected_signals))
            self.states.update([current_state, next_state])

            current_state = next_state

        # Define column names dynamically for the DataFrame
        column_names = ["Timestamp", "Current State", "Next State"] + [f"Signal{j+1}" for j in range(m)]
        self.dataframe = pd.DataFrame(data, columns=column_names)

    def get_dataframe(self):
        """Returns the loaded data as a DataFrame."""
        return self.dataframe

    def get_states(self):
        """Returns the list of unique states."""
        return list(self.states)

    def get_transitions(self):
        """Returns the list of transitions with state pairs and signal data."""
        return self.transitions
