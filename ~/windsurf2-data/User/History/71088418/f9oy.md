---
trigger: model_decision
description: Apply when working on DataLoader modules for parsing CSV logs of vehicle position/state
---

# Cursor Context Rules: DataLoader Log Parsing (MVP)

## Goal
Guide the implementation of parsers within the `DataLoader` module for the MVP's critical log types: "Car Position" and "Vehicle State."

## Assumed Input Format
- For MVP, assume log files are text-based, likely CSV-like or a structured text format that can be parsed line by line.
- *(User Action: If a more specific format for "C swift files" is known, detail it here, e.g., "Files are comma-separated values (.csv) with a header row. Timestamps are Unix epoch in seconds with millisecond precision.")*

## Required Data Extraction (MVP)

1.  **Car Position Log:**
    * `timestamp` (or `frame_index`): Primary key for synchronization. Specify unit/format.
    * `x`: Global X coordinate (float).
    * `y`: Global Y coordinate (float).
    * `theta`: Global orientation (float, specify units e.g., radians or degrees).
2.  **Vehicle State Log:**
    * `timestamp` (or `frame_index`): Primary key for synchronization. Specify unit/format.
    * `speed`: Vehicle speed (float, specify units e.g., m/s).
    * `acceleration`: Vehicle acceleration (float, specify units e.g., m/s²).

## Parser Implementation Guidance
- **Robustness:** Parsers should gracefully handle potential minor issues like empty lines if possible, or clearly error on malformed critical lines.
- **Efficiency:** For large log files, consider efficient line-by-line processing or using Pandas' `read_csv` with appropriate chunking or type specification if applicable.
- **Output:** Each parser function (or method within `DataLoader`) should return a structured representation of the parsed data, preferably a Pandas DataFrame with clearly named columns matching the required data fields above.
- **Error Handling:** If a file cannot be parsed or is missing critical data, the parser should raise an informative exception.

## Example: Parsing a Line (Conceptual for AI Guidance)
```python
# Conceptual: Guiding AI on how a single line might be processed
# Assume a line from Car Position log: "1678886400.123,100.5,200.75,1.57" (timestamp,x,y,theta)

# def parse_car_position_line(line: str) -> Dict[str, Any] | None:
#     parts = line.strip().split(',')
#     if len(parts) == 4:
#         try:
#             return {
#                 'timestamp': float(parts[0]),
#                 'x': float(parts[1]),
#                 'y': float(parts[2]),
#                 'theta': float(parts[3])
#             }
#         except ValueError:
#             # Log error or handle malformed line
#             return None
#     return None

## Stream Support Note
- In future versions, logs may also arrive via online streaming protocols (e.g., Protobuf over gRPC or Kafka).
- Parsers should be modular so they can operate in both:
  - Batch (offline files)
  - Stream (realtime chunks)
