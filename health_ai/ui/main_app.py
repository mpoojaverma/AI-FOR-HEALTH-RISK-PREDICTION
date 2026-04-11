import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Path Fix
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, "../model"))
from predict import engine

class MetricCard(QFrame):
    def __init__(self, title, val, color="#38bdf8"):
        super().__init__()
        self.setObjectName("MetricCard")
        l = QVBoxLayout(self)
        l.setContentsMargins(15, 12, 15, 12)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(f"color:{color}; font-weight:900; font-size:20px; letter-spacing:2px;")
        self.val_lbl = QLabel(val)
        self.val_lbl.setStyleSheet("font-size:25px; font-weight:900; color:#f8fafc;")
        l.addWidget(t_lbl); l.addWidget(self.val_lbl)

class ReportAnalysisDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clinical OCR Analysis Report")
        self.resize(900, 650)
        self.setStyleSheet(parent.styleSheet())
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        header = QLabel("AI Interpretative Analysis", objectName="H1"); layout.addWidget(header)
        body = QHBoxLayout()
        left = QVBoxLayout(); left.addWidget(QLabel("RAW SCANNED TEXT FROM YOUR MEDICAL RREPORTS", styleSheet="color:#64748b; font-weight:bold; font-size:14px;"))
        raw_box = QTextEdit(); raw_box.setPlainText(data['raw']); raw_box.setReadOnly(True); raw_box.setObjectName("LogBox")
        left.addWidget(raw_box)
        right = QVBoxLayout(); right.addWidget(QLabel("INTERPRETED LAB REPORT MARKERS", styleSheet="color:#22c55e; font-weight:bold;"))
        marker_list = QListWidget(); marker_list.setObjectName("GlassCard")
        if data['markers']:
            for m in data['markers']: marker_list.addItem(m)
        else: marker_list.addItem("No clear lab markers detected.")
        right.addWidget(marker_list); right.addWidget(QLabel("IDENTIFIED SYMPTOMS", styleSheet="color:#38bdf8; font-weight:bold;"))
        sym_list = QListWidget(); sym_list.setObjectName("GlassCard")
        if data['symptoms']:
            for s in data['symptoms']: sym_list.addItem(s.replace("_", " ").title())
        else: sym_list.addItem("No symptomatic matches found.")
        right.addWidget(sym_list); body.addLayout(left, 1); body.addLayout(right, 1); layout.addLayout(body)
        close_btn = QPushButton("DISMISS AND SYNC DATA"); close_btn.setObjectName("PrimaryBtn"); close_btn.clicked.connect(self.accept); layout.addWidget(close_btn)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HealthAI — Clinical Intelligence Suite"); self.resize(1350, 920)
        self.active_symptoms = set(); self.user_bmi = "Normal"; self.init_ui(); self.apply_theme()

    def init_ui(self):
        cw = QWidget(); self.setCentralWidget(cw)
        root = QHBoxLayout(cw); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(320)
        side_lay = QVBoxLayout(sidebar); side_lay.setContentsMargins(20,40,20,20)
        logo = QLabel("🩺 Symptomate"); logo.setObjectName("AppLogo"); side_lay.addWidget(logo, alignment=Qt.AlignCenter); side_lay.addSpacing(20)
        self.stack = QStackedWidget(); self.btns = []
        menus = [("Dashboard", "📊"), ("AI Diagnostics", "🧪"), ("AI Consultant", "💬"), ("Vitals Hub", "👤")]
        for i, (name, icon) in enumerate(menus):
            btn = QPushButton(f"  {icon}  {name}"); btn.setCheckable(True); btn.setObjectName("NavBtn")
            btn.clicked.connect(lambda _, x=i: self.nav(x)); side_lay.addWidget(btn); self.btns.append(btn)
        side_lay.addStretch()
        self.sys_status = QLabel("CLINICAL MODE: ACTIVE\n"); self.sys_status.setObjectName("SysStat"); side_lay.addWidget(self.sys_status); root.addWidget(sidebar)
        self.stack.addWidget(self.ui_dashboard()); self.stack.addWidget(self.ui_analyzer()); self.stack.addWidget(self.ui_chat()); self.stack.addWidget(self.ui_vitals())
        root.addWidget(self.stack); self.nav(0)

    def ui_dashboard(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.setContentsMargins(60,60,60,60)
        v = QVBoxLayout(); v.addWidget(QLabel("Clinical Dashboard", objectName="H1")); v.addWidget(QLabel("Your Clinical Healthcare Assistant.", styleSheet="color:#64748b; font-size:20px;"))
        lay.addLayout(v); lay.addSpacing(40)
        grid = QGridLayout(); grid.setSpacing(25)
        self.c_bmi = MetricCard("BMI INDEX", "--"); self.c_tdee = MetricCard("DAILY CALORIES", "--", "#fbbf24")
        self.c_water = MetricCard("WATER TARGET", "--", "#38bdf8"); self.c_risk = MetricCard("DIAGNOSTIC RISK", "STABLE", "#22c55e")
        grid.addWidget(self.c_bmi, 0, 0); grid.addWidget(self.c_tdee, 0, 1); grid.addWidget(self.c_water, 1, 0); grid.addWidget(self.c_risk, 1, 1)
        lay.addLayout(grid); lay.addSpacing(50); lay.addWidget(QLabel("Clinical Insights", objectName="H1", styleSheet="color:#22c55e;"))
        tip_box = QFrame(); tip_box.setObjectName("GlassCard"); tl = QVBoxLayout(tip_box); self.daily_tip = QLabel(engine.get_daily_tip()); self.daily_tip.setWordWrap(True)
        self.daily_tip.setStyleSheet("font-size:18px; font-weight:500; color:#e2e8f0;"); tl.addWidget(self.daily_tip); lay.addWidget(tip_box); lay.addStretch(); return pg

    def ui_analyzer(self):
        pg = QWidget(); lay = QHBoxLayout(pg); lay.setContentsMargins(30,30,30,30)
        left = QVBoxLayout(); left.addWidget(QLabel("Clinical Symptom Index", objectName="H2"))
        self.search = QLineEdit(); self.search.setPlaceholderText("🔎 Search symptoms..."); self.search.textChanged.connect(self.filter_list)
        self.list_w = QListWidget(); self.list_w.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_w.itemClicked.connect(self.toggle_marker)
        
        # FIXED: Added getattr to handle cases where engine fails to load columns
        for s in getattr(engine, 'columns', []): 
            it = QListWidgetItem(s.replace("_"," ").title()); it.setData(Qt.UserRole, s); self.list_w.addItem(it)
            
        left.addWidget(self.search); left.addWidget(self.list_w)
        mid = QVBoxLayout(); mid.addWidget(QLabel("Diagnosis Insights", objectName="H2"))
        self.res_scroll = QScrollArea(); self.res_scroll.setWidgetResizable(True); self.res_cont = QWidget(); self.res_lay = QVBoxLayout(self.res_cont); self.res_lay.setAlignment(Qt.AlignTop)
        self.res_scroll.setWidget(self.res_cont); mid.addWidget(self.res_scroll); btn = QPushButton("ANALYZE SYMPTOMS"); btn.setObjectName("PrimaryBtn"); btn.clicked.connect(self.run_diagnosis); mid.addWidget(btn)
        self.log_frame = QFrame(); self.log_frame.setFixedWidth(300); rl = QVBoxLayout(self.log_frame); rl.addWidget(QLabel("Analysis Log", objectName="H2"))
        self.diag_logs = QTextEdit(); self.diag_logs.setReadOnly(True); self.diag_logs.setObjectName("LogBox"); rl.addWidget(self.diag_logs); lay.addLayout(left, 1); lay.addLayout(mid, 2); lay.addWidget(self.log_frame); return pg

    def ui_chat(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.setContentsMargins(50,50,50,50)
        self.chat_w = QTextEdit(); self.chat_w.setReadOnly(True); self.chat_w.setObjectName("ChatBox"); self.chat_w.setHtml("<p style='color:#94a3b8;'>AI Consultant Ready.</p>")
        row = QHBoxLayout(); self.chat_in = QLineEdit(); self.chat_in.setPlaceholderText("Describe how you feel...")
        send = QPushButton("Consult"); send.setObjectName("PrimaryBtn"); send.setFixedWidth(120); send.clicked.connect(self.do_chat); row.addWidget(self.chat_in); row.addWidget(send); lay.addWidget(self.chat_w); lay.addLayout(row); return pg

    def ui_vitals(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.setContentsMargins(40,20,40,20); lay.setSpacing(10)
        lay.addWidget(QLabel("Health Metrics Hub", objectName="H1"))
        lay.addWidget(QLabel("Calculate metabolic data or scan medical reports.", styleSheet="color:#64748b; font-size:20px; font-weight:500;"))
        body = QHBoxLayout(); body.setSpacing(10); body.setAlignment(Qt.AlignTop)
        form_card = QFrame(); form_card.setObjectName("GlassCard"); form_card.setFixedWidth(300); form = QVBoxLayout(form_card)
        form.addWidget(QLabel("Metabolic Inputs", objectName="H2"))
        self.v_age = QLineEdit(); self.v_age.setPlaceholderText("Age (Years)")
        self.v_gender = QComboBox(); self.v_gender.addItems(["Female", "Male", "Others"])
        self.v_h = QLineEdit(); self.v_h.setPlaceholderText("Enter height (cm)")
        self.v_w = QLineEdit(); self.v_w.setPlaceholderText("Enter weight (kg)")
        self.v_act = QComboBox(); self.v_act.addItems(["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        form.addWidget(self.v_age); form.addWidget(self.v_gender); form.addWidget(self.v_h); form.addWidget(self.v_w); form.addWidget(self.v_act)
        btn_calc = QPushButton("CALCULATE PROFILE"); btn_calc.setObjectName("PrimaryBtn"); btn_calc.clicked.connect(self.run_vitals_calc); form.addWidget(btn_calc)
        btn_ocr = QPushButton("SCAN MEDICAL REPORT"); btn_ocr.setObjectName("PrimaryBtn"); btn_ocr.setStyleSheet("background: #10b981; margin-top: 10px;")
        btn_ocr.clicked.connect(self.run_ocr_scan); form.addWidget(btn_ocr)
        res_grid = QGridLayout(); res_grid.setSpacing(15); res_grid.setAlignment(Qt.AlignTop)
        self.v_res_bmr = MetricCard("BMR", "--", "#a855f7"); self.v_res_ibw = MetricCard("Ideal Weight", "--", "#10b981")
        self.v_res_tdee = MetricCard("TDEE", "--", "#fbbf24"); self.v_res_water = MetricCard("Daily Water", "--", "#38bdf8")
        res_grid.addWidget(self.v_res_bmr, 0, 0); res_grid.addWidget(self.v_res_ibw, 0, 1); res_grid.addWidget(self.v_res_tdee, 1, 0); res_grid.addWidget(self.v_res_water, 1, 1)
        body.addWidget(form_card); body.addLayout(res_grid); lay.addLayout(body)
        info_card = QFrame(); info_card.setObjectName("GlassCard"); info_lay = QVBoxLayout(info_card); info_lay.setSpacing(8)
        info_title = QLabel("How These Metrics Drive Risk Prediction?")
        info_title.setStyleSheet("font-size:20px; font-weight:800; color:#22c55e;")
        info_desc = QLabel(
            "These metabolic indicators are used to evaluate baseline health status and enhance diagnostic accuracy.\n\n"
            "• BMR: Energy usage at rest.\n"
            "• Ideal Weight (IBW): Healthy body range.\n"
            "• TDEE: Daily calorie requirement.\n"
            "• Water Intake: Hydration and organ function. \n"
            "• SCAN MEDICAL REPORT: AI interpretative analysis of your medical reports.\n"
            "All metrics are combined with symptom-based AI analysis to provide a comprehensive risk assessment."
        )
        info_desc.setWordWrap(True); info_desc.setStyleSheet("color:#cbd5e1; font-size:14px;")
        info_lay.addWidget(info_title); info_lay.addWidget(info_desc)
        lay.addSpacing(15); lay.addWidget(info_card); lay.addStretch(); return pg

    def nav(self, i):
        self.stack.setCurrentIndex(i)
        for idx, b in enumerate(self.btns): b.setChecked(idx == i)

    def filter_list(self):
        t = self.search.text().lower()
        for i in range(self.list_w.count()): it = self.list_w.item(i); it.setHidden(t not in it.text().lower())

    def toggle_marker(self, it):
        raw = it.data(Qt.UserRole)
        if it.isSelected(): self.active_symptoms.add(raw)
        else: self.active_symptoms.discard(raw)

    def run_vitals_calc(self):
        try:
            w, h, a = float(self.v_w.text()), float(self.v_h.text()), int(self.v_age.text())
            g, act = self.v_gender.currentText(), self.v_act.currentText()
            d = engine.calculate_comprehensive_vitals(w, h, a, g, act)
            self.c_bmi.val_lbl.setText(str(d['bmi'])); self.c_tdee.val_lbl.setText(f"{d['tdee']} kcal"); self.c_water.val_lbl.setText(f"{d['water']} L")
            self.v_res_bmr.val_lbl.setText(f"{d['bmr']} kcal"); self.v_res_ibw.val_lbl.setText(f"{d['ibw']} kg"); self.v_res_tdee.val_lbl.setText(f"{d['tdee']} kcal"); self.v_res_water.val_lbl.setText(f"{d['water']} L")
        except: pass

    def run_ocr_scan(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Medical Report", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.diag_logs.append(f"[{datetime.now().strftime('%H:%M')}] OCR Clean Scan Initiated...")
            data = engine.scan_report(file_path)
            dialog = ReportAnalysisDialog(data, self)
            if dialog.exec_():
                if data.get('symptoms'):
                    self.active_symptoms.update(data['symptoms'])
                    for i in range(self.list_w.count()):
                        it = self.list_w.item(i)
                        if it.data(Qt.UserRole) in self.active_symptoms: it.setSelected(True)
                    self.diag_logs.append(f"✅ Synced {len(data['symptoms'])} symptoms from OCR.")
                
                if data.get('markers'):
                    for m in data['markers']: self.diag_logs.append(f"🩺 Marker Detected: {m}")
                else: self.diag_logs.append("ℹ️ No specific medical markers were identified.")

    def do_chat(self):
        text = self.chat_in.text().strip()
        self.chat_in.clear()

        if not text:
            return

        # USER MESSAGE
        self.chat_w.append(
            "<div style='text-align:right; margin:10px 0;'>"
            "<span style='background:#38bdf8; color:#020617; padding:8px 14px; "
            "border-radius:12px; font-weight:600; display:inline-block;'>"
            f"{text}"
            "</span></div>"
        )

        # EXTRACT SYMPTOMS
        found = engine.fuzzy_extract(text)

        if not found:
            self.chat_w.append(
                "<div style='margin:10px 0;'>"
                "<span style='background:#1e293b; padding:10px 14px; border-radius:12px; color:#94a3b8;'>"
                "⚠️ No symptoms recognized. Try fever, cough, headache."
                "</span></div>"
            )
            return

        # RESET symptoms (IMPORTANT FIX)
        self.active_symptoms = set(found)

        # Sync UI selection
        for i in range(self.list_w.count()):
            it = self.list_w.item(i)
            if it.data(Qt.UserRole) in self.active_symptoms:
                it.setSelected(True)
            else:
                it.setSelected(False)

        # GET predictions
        result = engine.get_top_n_diagnosis(list(self.active_symptoms), self.user_bmi)

        if not result or not result.get("predictions"):
            self.chat_w.append(
                "<div style='margin:10px 0; color:#94a3b8;'>Unable to generate prediction.</div>"
            )
            return
        # FILTERING LAYER
    
        common_keywords = {"fever", "headache", "cough", "fatigue"}
        dangerous_diseases = {
            "Paralysis (brain hemorrhage)",
            "Heart attack",
            "Brain tumor"
        }

        filtered = []

        for p in result["predictions"]:
            disease = p["disease"]
            confidence = p["confidence"]

            # Remove dangerous diseases for mild symptoms
            if any(sym in common_keywords for sym in self.active_symptoms):
                if disease in dangerous_diseases:
                    continue

            # Keep meaningful predictions
            if confidence > 0.20:
                filtered.append(p)

        # fallback
        if not filtered:
            filtered = result["predictions"][:2]

        # SORT (highest confidence first)
        filtered = sorted(filtered, key=lambda x: x["confidence"], reverse=True)

        # RESPONSE UI
        msg = (
            "<div style='margin:12px 0; padding:16px; background:#0f172a; "
            "border-radius:14px; border:1px solid #1e293b;'>"
            "<div style='color:#22c55e; font-size:15px; font-weight:700; margin-bottom:10px;'>"
            "🧠 AI Clinical Analysis</div>"
        )

        for p in filtered:
            confidence = int(p['confidence'] * 100)

            msg += (
                "<div style='margin-bottom:10px; padding:10px; background:#020617; border-radius:10px;'>"
                "<div style='display:flex; justify-content:space-between;'>"
                f"<span style='font-weight:700; color:#38bdf8;'>{p['disease']}</span>"
                f"<span style='color:#22c55e; font-weight:600;'>{confidence}%</span>"
                "</div>"
                "<div style='height:6px; background:#1e293b; border-radius:6px; margin-top:6px;'>"
                f"<div style='width:{confidence}%; background:#38bdf8; height:100%; border-radius:6px;'></div>"
                "</div></div>"
            )

        msg += "</div>"

        self.chat_w.append(msg)

    def run_diagnosis(self):
        if not self.active_symptoms: return
        data = engine.get_top_n_diagnosis(list(self.active_symptoms), self.user_bmi)
        for i in reversed(range(self.res_lay.count())): self.res_lay.itemAt(i).widget().setParent(None)
        for i, res in enumerate(data['predictions']):
            card = QFrame(); card.setObjectName("ResCard"); l = QVBoxLayout(card)
            l.addWidget(QLabel(f"{i+1}. {res['disease']} ({int(res['confidence']*100)}%)", styleSheet="font-size:18px; font-weight:900; color:#38bdf8;"))
            l.addWidget(QLabel(res['description'], styleSheet="color:#cbd5e1; font-size:13px;"))
            self.res_lay.addWidget(card)
        top = data['predictions'][0]; color = "#ef4444" if data['urgency'] > 6 else "#fbbf24"
        self.c_risk.val_lbl.setText(top['disease'].upper()); self.c_risk.val_lbl.setStyleSheet(f"font-size:18px; color:{color};")

    def apply_theme(self):
        self.setStyleSheet("""
            QWidget { background: #020617; color: #f1f5f9; font-family: 'Segoe UI', sans-serif; }
            #Sidebar { background: #0f172a; border-right: 1px solid #1e293b; }
            #AppLogo { font-size: 25px; font-weight: 900; color: #38bdf8; padding: 30px; }
            #NavBtn { border: none; padding: 16px; text-align: left; border-radius: 20px; margin: 10px 30px; color: #94a3b8; font-size: 16px; font-weight: 600; }
            #NavBtn:hover { background: #1e293b; color: white; }
            #NavBtn:checked { background: #38bdf8; color: #020617; font-weight: 800; }
            #SysStat { font-size: 13px; color: #475569; padding: 20px; border-top: 1px solid #1e293b; }
            #H1 { font-size: 44px; font-weight: 900; letter-spacing: -2px; color: #f8fafc; }
            #H2 { font-size: 18px; font-weight: 800; color: #38bdf8; margin: 20px 0; }
            #MetricCard { background: #0f172a; border-radius: 10px; padding: 20px; border: 5px solid #1e293b; min-width: 180px; }
            #MetricCard:hover { border: 2px solid #38bdf8; }
            #GlassCard { background: #0f172a; border-radius: 20px; border: 1px solid #1e293b; padding: 20px; }
            #PrimaryBtn { background: #38bdf8; color: #020617; font-weight: 900; padding: 18px; border-radius: 15px; border: none; }
            QLineEdit, QListWidget, QTextEdit, QComboBox { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 12px; }
            #LogBox { font-family: 'Consolas', 'Courier New'; font-size: 11px; color: #64748b; }
            #ResCard { background: #1e293b; border-radius: 25px; padding: 35px; border: 2px solid #334155; margin-bottom: 12px; }
            QListWidget::item { padding: 10px; border-radius: 8px; }
            QListWidget::item:selected { background: #38bdf8; color: #020617; font-weight: 700; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainApp(); win.show(); sys.exit(app.exec_())
