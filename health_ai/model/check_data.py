import pandas as pd

print("Running file...")
df = pd.read_csv("../data/dataset.csv")

print("Columns:\n", df.columns)
print("\nSample data:\n", df.head())