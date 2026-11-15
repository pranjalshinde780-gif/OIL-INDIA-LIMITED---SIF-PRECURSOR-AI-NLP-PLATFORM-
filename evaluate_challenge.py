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


# Load independent challenge reports
df = pd.read_csv("data/challenge_reports.csv")


# Reference labels
# 1 = SIF Precursor
# 0 = Non-SIF
reference_labels = {
    "C001": 1,
    "C002": 0,
    "C003": 1,
    "C004": 0,
    "C005": 1,
    "C006": 0,
    "C007": 1,
    "C008": 0,
    "C009": 1,
    "C010": 0,
    "C011": 1,
    "C012": 0,
    "C013": 1,
    "C014": 0,
    "C015": 1,
    "C016": 0,
    "C017": 1,
    "C018": 0,
    "C019": 1,
    "C020": 0
}


# Load the trained classifier
classifier = SIFClassifier()


actual = []
predicted = []


print("\n" + "=" * 70)
print("INDEPENDENT SIF CHALLENGE TEST")
print("=" * 70)


for _, row in df.iterrows():

    report_id = row["report_id"]
    description = row["description"]

    result = classifier.predict_one(description)

    actual_label = reference_labels[report_id]
    predicted_label = result["is_sif"]

    actual.append(actual_label)
    predicted.append(predicted_label)

    print(f"\n{report_id}")
    print(f"Report: {description}")
    print(f"Actual:    {actual_label}")
    print(f"Predicted: {predicted_label}")
    print(f"ML Probability: {result['ml_probability']:.2%}")
    print(f"Final Probability: {result['sif_probability']:.2%}")
    print(f"Risk Tier: {result['risk_tier']}")


# Calculate evaluation metrics
accuracy = accuracy_score(actual, predicted)
precision = precision_score(actual, predicted, zero_division=0)
recall = recall_score(actual, predicted, zero_division=0)
f1 = f1_score(actual, predicted, zero_division=0)

cm = confusion_matrix(actual, predicted)


print("\n" + "=" * 70)
print("FINAL EVALUATION")
print("=" * 70)

print(f"\nAccuracy :  {accuracy:.2%}")
print(f"Precision:  {precision:.2%}")
print(f"Recall   :  {recall:.2%}")
print(f"F1 Score :  {f1:.2%}")

print("\nConfusion Matrix:")
print(cm)

print("\nDetailed Classification Report:")
print(classification_report(
    actual,
    predicted,
    target_names=["Non-SIF", "SIF"],
    zero_division=0
))