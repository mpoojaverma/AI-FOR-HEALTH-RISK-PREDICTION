from predict import *

# Try some symptoms from your dataset
symptoms = ["itching", "skin_rash"]

disease, prob = predict_disease(symptoms)
risk = get_risk_level(prob)

desc = get_description(disease)
prec = get_precautions(disease)

print("\n===== RESULT =====")
print("Disease:", disease)
print("Probability:", round(prob * 100, 2), "%")
print("Risk Level:", risk)

print("\nDescription:")
print(desc)

print("\nPrecautions:")
for p in prec:
    print("-", p)