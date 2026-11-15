from engine.sif_classifier import SIFClassifier

# Load the trained model
classifier = SIFClassifier()

# Report we want to investigate
text = "A corridor light in the control room was flickering and the issue was reported to maintenance."

# Preprocess exactly the same way as the real prediction
clean_text = classifier.preprocessor.clean_text(text)
prep_text = classifier.preprocessor.preprocess_for_model(clean_text)

# Get the trained TF-IDF vectorizer and classifier
vectorizer = classifier.pipeline.named_steps["tfidf"]
calibrated_model = classifier.pipeline.named_steps["clf"]

# Convert text into TF-IDF features
X = vectorizer.transform([prep_text])

# Get the underlying Logistic Regression model
logistic_model = calibrated_model.calibrated_classifiers_[0].estimator

# Get feature names and coefficients
feature_names = vectorizer.get_feature_names_out()
coefficients = logistic_model.coef_[0]

# Find words/features present in this report
feature_indices = X.nonzero()[1]

# Show their contribution
contributions = []

for index in feature_indices:
    contribution = X[0, index] * coefficients[index]
    contributions.append(
        (feature_names[index], contribution)
    )

# Sort by strongest SIF contribution
contributions.sort(key=lambda x: x[1], reverse=True)

print("\n" + "=" * 60)
print("MODEL FEATURE DIAGNOSTIC")
print("=" * 60)

print("\nProcessed report:")
print(prep_text)

print("\nFeatures pushing toward SIF:")
for word, contribution in contributions[:15]:
    if contribution > 0:
        print(f"{word:30} {contribution:.4f}")

print("\nFeatures pushing away from SIF:")
for word, contribution in reversed(contributions[-15:]):
    if contribution < 0:
        print(f"{word:30} {contribution:.4f}")