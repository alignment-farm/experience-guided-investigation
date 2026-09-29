# Repair the checkpoint-1 normalization regression

The current CLI must normalize a rename from/to pair by trimming both field names, while preserving the existing select, map, and error behavior. Run the visible tests, inspect the affected source, make a narrow repair, and verify a targeted rename case.
