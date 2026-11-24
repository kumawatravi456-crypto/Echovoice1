# Project Echo (Echovoice) — College Mini Project Report
## Multimodal Live Conversation Assistant for People with Speech Impairments

---

| **Field** | **Details** |
| :--- | :--- |
| **Student Name** | **Ravi Kumawat** |
| **Enrollment No.** | **EN24CS3010841** |
| **Department** | Computer Science & Engineering |
| **Project Title** | Project Echo (Echovoice) |
| **Live Web App** | [https://ide-quicklink-6-five.vercel.app](https://ide-quicklink-6-five.vercel.app) |
| **GitHub Repository** | [https://github.com/kumawatravi456-crypto/Echovoice1](https://github.com/kumawatravi456-crypto/Echovoice1) |

---

## 1. Abstract
People living with speech and motor disabilities—such as Amyotrophic Lateral Sclerosis (ALS), cerebral palsy, Parkinson's disease, or stroke-induced dysarthria—often face severe communication barriers. Conventional speech recognition software is calibrated for standard neurotypical speech and consistently misinterprets atypical acoustic signals.

**Project Echo** is an accessible, real-time multimodal assistive communication system. By integrating **local computer vision** (MediaPipe hand tracking), **speech transcription** (browser-native Web Speech API / ElevenLabs), and **conversational AI**, the system assists users in expressing their thoughts. Core gestures (`YES`, `NO`, `HELP`, `WATER`, `STOP`) are classified in real time. A conversational AI suggests context-aware responses that the user can review and edit before explicit confirmation triggers text-to-speech output.

---

## 2. Problem Statement & Need
- **Inability of Standard Voice Assistants:** Mainstream voice recognition engines (Siri, Alexa, Google Assistant) fail on atypical speech patterns.
- **Slow AAC Hardware:** Traditional Augmentative and Alternative Communication devices rely on character-by-character typing or mechanical switch selection, resulting in slow communication rates.
- **Privacy Concerns:** Uploading continuous webcam streams to cloud servers introduces privacy risks. Project Echo solves this by extracting geometry vectors entirely on-device in the browser.

---

## 3. System Architecture & Workflow

1. **Visual Tracking (Client-Side Edge):**
   - MediaPipe Vision Tasks extracts 21 coordinates for hand joints and 468 facial points locally in the browser at 30 FPS.
   - Raw video frames never leave the client's device.
2. **Feature Extraction:**
   - Hand geometry is condensed into a 7-dimensional metric vector (inter-finger distances, thumb extension ratios, and palm angles).
3. **ML Classification (Backend):**
   - FastAPI backend evaluates the 7D vector via a `StandardScaler + LogisticRegression` model in under 10 ms.
4. **Contextual AI Formulation:**
   - Groq conversational model combines recent dialogue history and verified gestures to suggest short, natural answers.
5. **Human-in-the-Loop Confirmation:**
   - The user selects, edits, or confirms the suggested response before speech synthesis occurs.

---

## 4. Technology Stack

| Layer | Tools & Frameworks | Description |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite 8.3 | High-performance reactive user interface |
| **Styling** | Tailwind CSS | Glassmorphism, accessible dark-mode UI |
| **Edge Vision** | `@mediapipe/tasks-vision` | Browser-side 30 FPS hand landmark detection |
| **Backend API** | FastAPI, Uvicorn, Pydantic | High-speed asynchronous Python REST API |
| **Machine Learning**| scikit-learn, NumPy, Joblib | Gesture pipeline trained on hand geometry |
| **Speech Engine** | Web Speech API / ElevenLabs Scribe | Local real-time browser STT + Cloud ASR |
| **Cloud Hosting** | Vercel | Global CDN deployment |

---

## 5. Gesture Classes & Metrics

The custom hand classifier recognizes 5 critical everyday interaction gestures:

| Gesture | Real-World Intention | Evaluation Accuracy |
| :--- | :--- | :---: |
| **YES** | Agreement / Approval | 92.3% |
| **NO** | Disagreement / Decline | 90.0% |
| **HELP** | Emergency / Physical Assistance | 91.5% |
| **WATER** | Thirst / Hydration Request | 88.5% |
| **STOP** | Immediate Pause / Discontinue | 92.0% |

- **Cross-Validation Accuracy:** 88.89%
- **Balanced Accuracy:** 91.43%
- **Macro F1-Score:** 89.39%
- **Inference Latency:** < 8 ms

---

## 6. How to Run Locally

### Backend Setup:
```bash
git clone https://github.com/kumawatravi456-crypto/Echovoice1.git
cd Echovoice1
python3.11 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend python -m uvicorn app.main:app --port 8000 --reload
```

### Frontend Setup:
```bash
cd ide-quicklink-6
npm install --legacy-peer-deps
npm run dev
```

Open `http://localhost:3000` in Google Chrome.

---

## 7. Conclusion
Project Echo demonstrates that combining client-side computer vision with lightweight machine learning pipelines creates a private, accessible, and fast communication bridge for individuals with speech impairments.

---

<div align="center">
  <sub><strong>Project Echo</strong> &nbsp;|&nbsp; <strong>Student:</strong> Ravi Kumawat &nbsp;|&nbsp; <strong>Enrollment No.:</strong> EN24CS3010841</sub>
</div>
