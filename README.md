# 🩺 Symptomate HealthAI — Clinical Intelligence Suite

An AI-powered healthcare assistant that analyzes **user symptoms + medical reports** to predict possible diseases and provide clinical insights using Machine Learning.

---

## Features

* Symptom-based disease prediction (ML-based - RandomForest Classifier)
* OCR-based medical report scanning
* Lab marker extraction (Blood / Urine reports)
* Top 3 disease predictions with confidence
* Health metrics calculation (BMI, BMR, TDEE)
* PyQt5 UI dashboard
* AI chatbot-style symptom consultation (Fuzzy extraction and NLP)

---
## Preview
---
<p align="center">
  <img src="sample outputs/A.png" width="100%">
  <img src="sample outputs/1.png" width="100%">
  <img src="sample outputs/2.png" width="100%">
  <img src="sample outputs/3.png" width="100%">
  <img src="sample outputs/4.png" width="100%">
</p>
---

## 🧠 Tech Stack

* **Frontend:** PyQt5 (Desktop UI)
* **Backend:** Python
* **ML Model:** Random Forest Classifier
* **Libraries Used:**

  * pandas, numpy
  * scikit-learn
  * pytesseract (OCR)
  * PIL (Image processing)

---

## 📂 Project Structure

```
HealthAI/
│
├── data/
│   ├── dataset.csv
│   ├── symptom_Description.csv
│   ├── Symptom-severity.csv
│
├── model/
│   ├── model.pkl
│   ├── columns.pkl
│   ├── train_model.py
│   ├── predict.py
│
├── app/
│   ├── main_app.py
│
├── utils/
│   ├── dev_launcher.py
│
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/HealthAI.git
cd HealthAI
```

---

### 2️⃣ Install Dependencies

```bash
pip install pandas numpy scikit-learn pytesseract pillow PyQt5 watchdog
```

---

### 3️⃣ Install Tesseract OCR

* Download from: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
* Set path in code:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

(Already configured in code )

---

### 4️⃣ Train the Model

```bash
cd model
python train_model.py
```
---

### 5️⃣ Run the Application

```bash
cd app
python main_app.py
```
---

## 🧪 How It Works

### Step 1: Symptom Input

* User selects symptoms from UI or types them
* System converts symptoms → binary vector

---

### Step 2: Model Prediction

* Random Forest predicts probabilities
* Top 3 diseases are selected

---

### Step 3: Output

Example:

```
1. Fungal Infection (82%)
2. Allergy (65%)
3. Dermatitis (40%)
```

Also includes:

* Description
* Evidence symptoms

---

### Step 4: OCR Report Analysis

* Upload medical report image
* OCR extracts text
* Regex and whitelist identifies markers

Example output:

```
Hemoglobin: 13.5 g/dL
WBC: 8000 cells/cumm
```

(Extraction handled in engine)

---

### Step 5: Health Metrics

Calculated:

* BMI, BMR, TDEE and Ideal Body Weight

---

## ⚠️ Limitations

* Not a replacement for medical professionals
* Depends on dataset quality
* OCR accuracy varies with image quality

---

## 🔮 Future Improvements

* Deep learning integration
* Real-time hospital API integration
* Mobile app version

---

## Disclaimer

This system is for **educational purposes only** and should not be used for real medical diagnosis.

---
