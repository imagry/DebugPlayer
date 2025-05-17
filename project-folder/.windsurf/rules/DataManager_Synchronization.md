---
trigger: model_decision
description: Apply when working on data synchronization logic or timeline-aligned data access
---

# Cursor Context Rules: DataManager Synchronization

## Goal
Ensure accurate and efficient synchronization of time-series data from various log sources (Car Position, Vehicle State for MVP) within the `DataManager` component.

## Core Principles
- **Primary Timeline:** All data should be aligned to a single, master timeline. This timeline will be derived from timestamps or frame indices present in the critical log files.
- **Timestamp Precision:** Be mindful of timestamp units (e.g., nanoseconds, milliseconds, seconds) and ensure consistency.
- **Data Structure:** Synchronized data for a given point in time should be easily accessible, likely as a dictionary where keys are signal names or categories (e.g., `{'car_position': {...}, 'vehicle_state': {...}}`).
- **Pandas Usage:** Leverage Pandas DataFrames for storing time-series data. Synchronization will often involve merging or re-indexing DataFrames.

## MVP Synchronization Strategy
- **Input:** Multiple Pandas DataFrames, each corresponding to a parsed log type, indexed by their original timestamps/frame indices.
- **Method:**
    1. Identify or create a master time index (e.g., from the highest frequency log or a synthesized regular interval if appropriate, though for MVP, using one log's index as primary is fine).
    2. For each DataFrame, re-index it to the master time index using a specified method.
    3. **For MVP, the primary method for handling misaligned timestamps is `method='nearest'` with `pandas.reindex()` or `pandas.merge_asof()`.**
    4. Ensure tolerance for `merge_asof` or `reindex` with `nearest` is considered if timestamps can be slightly off but still correspond.
- **Output:** A single structure (e.g., a multi-indexed DataFrame or a dictionary of aligned Series/DataFrames) that allows querying all relevant data for any point on the master timeline.

## Key `DataManager` Methods
- `synchronize_data(raw_data_frames: Dict[str, pd.DataFrame]) -> pd.DataFrame:` (Or similar, to produce the master synchronized DataFrame).
- `get_data_at_time(timestamp: float) -> Dict[str, Any]:` (Should retrieve data from the synchronized structure).

## Example Snippet (Conceptual for AI Guidance)
```python
# Conceptual: Guiding AI on re-indexing with nearest neighbor
# master_time_index = ... # Derived from one of the logs or synthesized
# synchronized_dfs = {}
# for log_name, df in raw_data_frames.items():
#     df_aligned = df.reindex(master_time_index, method='nearest', tolerance=pd.Timedelta('10ms')) # Example tolerance
#     synchronized_dfs[log_name] = df_aligned
#
# # Or using merge_asof if there's a clear primary log stream to merge onto
# primary_df = raw_data_frames['car_position'].sort_index()
# secondary_df = raw_data_frames['vehicle_state'].sort_index()
# merged_df = pd.merge_asof(primary_df, secondary_df, on='timestamp', direction='nearest', tolerance=pd.Timedelta('10ms'))