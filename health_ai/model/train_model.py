import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

print("Loading dataset...")

df = pd.read_csv("../data/dataset.csv")

print("Dataset loaded")

# ----------------------------
# STEP A: Collect symptoms
# ----------------------------
print("Collecting symptoms...")

symptoms = set()

# skip first column (Disease)
for col in df.columns[1:]:
    symptoms.update(df[col].dropna().unique())

symptoms = sorted(symptoms)

print(f"Total unique symptoms: {len(symptoms)}")

# ----------------------------
# STEP B: Create binary dataset
# ----------------------------
print("Creating binary dataset...")

new_df = pd.DataFrame(0, index=range(len(df)), columns=symptoms)

for i in range(len(df)):
    for col in df.columns[1:]:   # skip Disease
        symptom = df.loc[i, col]
        if pd.notna(symptom):
            new_df.loc[i, symptom] = 1

# Add target column
new_df["prognosis"] = df["Disease"]

print("Binary dataset created")

# ----------------------------
# STEP C: Train model
# ----------------------------
print("Training model...")

X = new_df.drop("prognosis", axis=1)
y = new_df["prognosis"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

print("Model trained")

# ----------------------------
# STEP D: Save
# ----------------------------
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(list(X.columns), open("columns.pkl", "wb"))

print("Model saved successfully")