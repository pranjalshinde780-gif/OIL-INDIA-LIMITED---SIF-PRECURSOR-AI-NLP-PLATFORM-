import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from engine.sif_classifier import SIFClassifier


# Load the 50 real-world reports
df = pd.read_csv(
    "data/SIF_real_world_review_set_50_completed.csv"
)

classifier = SIFClassifier()

actual = []
predicted = []

print("\n" + "=" * 70)
print("REAL-WORLD SIF EVALUATION")
print("=" * 70)

for _, row in df.iterrows():

    report_id = row["review_id"]
    description = row["Final Narrative"]

    # Run the existing model
    result = classifier.predict_one(description)

    actual_label = int(row["review_label"])
    predicted_label = result["is_sif"]

    actual.append(actual_label)
    predicted.append(predicted_label)

    print(f"\n{report_id}")
    print(f"Actual:       {actual_label}")
    print(f"Predicted:    {predicted_label}")
    print(f"ML Probability:    {result['ml_probability']:.2%}")
    print(f"Final Probability: {result['sif_probability']:.2%}")
    print(f"Risk Tier:     {result['risk_tier']}")


# Calculate evaluation metrics
accuracy = accuracy_score(actual, predicted)
precision = precision_score(actual, predicted, zero_division=0)
recall = recall_score(actual, predicted, zero_division=0)
f1 = f1_score(actual, predicted, zero_division=0)

cm = confusion_matrix(actual, predicted)


print("\n" + "=" * 70)
print("FINAL REAL-WORLD EVALUATION")
print("=" * 70)

print(f"\nAccuracy :  {accuracy:.2%}")
print(f"Precision:  {precision:.2%}")
print(f"Recall   :  {recall:.2%}")
print(f"F1 Score :  {f1:.2%}")

print("\nConfusion Matrix:")
print(cm)

print("\nDetailed Classification Report:")
print(
    classification_report(
        actual,
        predicted,
        target_names=["Non-SIF", "SIF"],
        zero_division=0
    )
)