import pickle
import pandas as pd
import os
import difflib
import numpy as np
import random
import re
import pytesseract
from PIL import Image, ImageOps, ImageEnhance

# --- 1. DYNAMIC PATHING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")

# --- 2. TESSERACT CONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ClinicalEngine:
    def __init__(self):
        self.model = None
        self.columns = []
        self.clean_columns = []
        self.severity_map = {}
        self.disease_map = {}
        self.desc_df = pd.DataFrame()
        
        # STRENGTHENED: Whitelist including Blood and Urine markers
        self.medical_whitelist = [
            "wbc", "rbc", "hemoglobin", "hgb", "platelets", "glucose", "sugar", 
            "cholesterol", "creatinine", "urea", "bilirubin", "protein", "albumin",
            "thyroid", "tsh", "calcium", "vitamin", "iron", "neutrophils", "lymphocytes",
            "volume", "colour", "color", "appearance", "gravity", "ph", "reaction", 
            "nitrite", "leukocytes", "ketone", "eravi" # Added 'eravi' to catch the typo
        ]
        
        # NEW: Alias Mapper (Fixes OCR names automatically)
        self.name_aliases = {
            "specific eravi": "Specific Gravity",
            "hacmoglobia": "Hemoglobin",
            "paco nnur": "PH Value",
            "color": "Colour"
        }

        self.unit_fixes = {
            "cellveumm": "cells/cumm",
            "ms": "mg/dL",
            "gm": "g/dL"
        }

        try:
            model_path = os.path.join(BASE_DIR, "model.pkl")
            cols_path = os.path.join(BASE_DIR, "columns.pkl")
            if os.path.exists(model_path):
                self.model = pickle.load(open(model_path, "rb"))
            if os.path.exists(cols_path):
                self.columns = [c.strip() for c in pickle.load(open(cols_path, "rb"))]
                self.clean_columns = [c.replace("_", " ") for c in self.columns]
            
            if os.path.exists(DATA_DIR):
                self.desc_df = pd.read_csv(os.path.join(DATA_DIR, "symptom_Description.csv"))
                self.dataset = pd.read_csv(os.path.join(DATA_DIR, "dataset.csv"))
                sev_df = pd.read_csv(os.path.join(DATA_DIR, "Symptom-severity.csv"))
                sev_df['Symptom'] = sev_df['Symptom'].str.strip().str.replace(" ", "_")
                self.severity_map = dict(zip(sev_df['Symptom'], sev_df['weight']))
                for _, row in self.dataset.drop_duplicates(subset=['Disease']).iterrows():
                    d = row['Disease'].strip()
                    self.disease_map[d] = set([str(s).strip() for s in row[1:].dropna() if str(s).strip()])
        except Exception as e:
            print(f"⚠️ Engine Initialization Error: {e}")

    def clean_image(self, pil_img):
        img = ImageOps.grayscale(pil_img)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        return img

    def scan_report(self, image_path):
        try:
            raw_img = Image.open(image_path)
            cleaned_img = self.clean_image(raw_img)
            raw_text = pytesseract.image_to_string(cleaned_img)
            found_symptoms = self.fuzzy_extract(raw_text)
            
            # STRENGTHENED REGEX: Now accepts words (Negative, Nil, Clear) as values
            marker_pattern = r'([A-Za-z\s\.]{3,25})[:\s-]+([A-Za-z0-9\.\-\+]+)\s?([a-zA-Z/%/dL/uL]*)'
            matches = re.findall(marker_pattern, raw_text)
            
            structured_markers = []
            for m in matches:
                name_raw = m[0].strip()
                name_lower = name_raw.lower()
                val = m[1]
                unit = m[2].lower()
                
                # Apply Aliases (Rename misread OCR names)
                for typo, correct_name in self.name_aliases.items():
                    if typo in name_lower:
                        name_raw = correct_name
                        break
                
                for typo, fix in self.unit_fixes.items():
                    if typo in unit: unit = fix
                
                if any(key in name_lower for key in self.medical_whitelist):
                    structured_markers.append(f"{name_raw.title()}: {val} {unit}")

            return {"symptoms": found_symptoms, "markers": structured_markers, "raw": raw_text}
        except Exception as e:
            return {"symptoms": [], "markers": [], "raw": f"Error: {str(e)}"}

    def fuzzy_extract(self, text):
        if not self.clean_columns: return []
        text = text.lower()
        found = set()
        for i, col in enumerate(self.clean_columns):
            if col in text and len(col) > 4: # Increased length to avoid false positive short words
                found.add(self.columns[i])
        return list(found)

    def calculate_comprehensive_vitals(self, weight, height, age, gender, activity):
        if gender == "Male": bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else: bmr = 10 * weight + 6.25 * height - 5 * age - 161
        act_map = {"Sedentary": 1.2, "Lightly Active": 1.375, "Moderately Active": 1.55, "Very Active": 1.725}
        tdee = bmr * act_map.get(activity, 1.2)
        bmi = round(weight / ((height/100)**2), 1)
        h_inches = height / 2.54
        if gender == "Male": ibw = 50 + 2.3 * (h_inches - 60) if h_inches > 60 else 50
        else: ibw = 45.5 + 2.3 * (h_inches - 60) if h_inches > 60 else 45.5
        return {"bmr": int(bmr), "tdee": int(tdee), "bmi": bmi, "ibw": round(ibw, 1), "water": round(weight * 0.033, 1)}

    def get_daily_tip(self):
        return random.choice(["Hydrate well.", "Check markers.", "BMI matters.", "Move daily.", "Track symptoms."])

    def get_top_n_diagnosis(self, symptoms, bmi_cat="Normal"):
        if not symptoms or self.model is None or not self.columns: return None
        vec = [0] * len(self.columns)
        for s in symptoms:
            if s in self.columns: vec[self.columns.index(s)] = 1
        probs = self.model.predict_proba([vec])[0]
        classes = self.model.classes_
        top_idx = np.argsort(probs)[-3:][::-1]
        results = []
        for idx in top_idx:
            name = classes[idx].strip()
            evidence = [s.replace("_", " ") for s in symptoms if s in self.disease_map.get(name, set())]
            desc = "N/A"
            if not self.desc_df.empty:
                val = self.desc_df[self.desc_df['Disease'] == name]['Description'].values
                if len(val) > 0: desc = val[0]
            results.append({"disease": name, "confidence": probs[idx], "evidence": evidence, "description": desc})
        return {"predictions": results, "urgency": max([self.severity_map.get(s, 1) for s in symptoms]) if self.severity_map else 1}

engine = ClinicalEngine()