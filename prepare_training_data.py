import pandas as pd

# Original synthetic training data
original = pd.read_csv("data/oil_safety_reports.csv")

# Our manually reviewed real-world training data
real_world = pd.read_csv(
    "data/SIF_real_world_training_review_100_completed.csv"
)

# Keep only the columns required by the classifier
real_world = real_world[
    ["Final Narrative", "review_label"]
].rename(
    columns={
        "Final Narrative": "description",
        "review_label": "is_sif_precursor"
    }
)

# Combine both datasets
combined = pd.concat(
    [
        original[["description", "is_sif_precursor"]],
        real_world[["description", "is_sif_precursor"]]
    ],
    ignore_index=True
)

# Remove any rows without a label
combined = combined.dropna(
    subset=["description", "is_sif_precursor"]
)

# Make sure labels are integers
combined["is_sif_precursor"] = combined[
    "is_sif_precursor"
].astype(int)

# Save the new training dataset
combined.to_csv(
    "data/combined_training_data.csv",
    index=False
)

print("\n" + "=" * 60)
print("COMBINED TRAINING DATA")
print("=" * 60)

print(f"\nOriginal reports : {len(original)}")
print(f"Real-world reports: {len(real_world)}")
print(f"Total reports    : {len(combined)}")

print("\nLabel distribution:")
print(combined["is_sif_precursor"].value_counts())

print("\nSaved to:")
print("data/combined_training_data.csv")