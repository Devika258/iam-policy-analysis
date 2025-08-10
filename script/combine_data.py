import pandas as pd

# MIT data
mit_events = pd.read_csv("data/athena_events_filtered.csv")
mit_counts = pd.read_csv("data/athena_event_counts.csv")

# Custom data
custom_events = pd.read_csv("data/custom/athena_events_custom.csv")

# Combined data
combined = pd.read_csv("data/combined/combined_events.csv")

print("MIT events loaded:", mit_events.shape)
print("MIT counts loaded:", mit_counts.shape)
print("Custom events loaded:", custom_events.shape)
print("Combined events loaded:", combined.shape)

#Output: python script/combine_data.py