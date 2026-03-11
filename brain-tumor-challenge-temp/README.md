# 🧠 Brain Tumor MRI Classification Challenge

<div align="center">

![Brain MRI](https://img.shields.io/badge/Task-Multi--Class%20Classification-blue)
![Classes](https://img.shields.io/badge/Classes-4-green)
![Images](https://img.shields.io/badge/MRI%20Images-7023-orange)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

**Can your model detect brain tumors from MRI scans?**

[📊 Leaderboard](#-leaderboard) • [📁 Dataset](#-dataset) • [🚀 Quick Start](#-quick-start) • [📤 How to Submit](#-submission-process) • [🔒 Security](#-security-system)

</div>

---

## 🏆 Leaderboard

| Rank | Team | Accuracy | F1 Score (Macro) | Submissions | Last Updated |
|------|------|----------|-------------------|-------------|--------------|
| 🥇 | — | — | — | — | — |
| 🥈 | — | — | — | — | — |
| 🥉 | — | — | — | — | — |

> 📣 Leaderboard auto-updates within **2–5 minutes** after each valid submission.  
> Full leaderboard: [`leaderboard/leaderboard.csv`](leaderboard/leaderboard.csv)

---

## 📋 Overview

### Task
Classify brain MRI images into **4 categories**:

| Label | Class | Description |
|-------|-------|-------------|
| `0` | `glioma` | Glioma tumor — arises from glial cells |
| `1` | `meningioma` | Meningioma tumor — arises from meninges |
| `2` | `no_tumor` | Healthy brain — no tumor detected |
| `3` | `pituitary` | Pituitary tumor — in the pituitary gland |

### Metrics
- **Primary**: Weighted F1 Score
- **Secondary**: Accuracy

### Timeline
| Event | Date |
|-------|------|
| Competition Start | TBD |
| Submission Deadline | TBD |
| Results Announced | TBD |

---

## 📁 Dataset

**Source**: [Brain Tumor MRI Dataset — Kaggle (masoudnickparvar)](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset)

- **Total images**: 7,023 MRI scans
- **Training set**: 5,712 images (provided to participants)
- **Test set**: 1,311 images (labels hidden — used for evaluation only)
- **Format**: JPEG images, variable sizes

### Class Distribution (Training)
| Class | Train Images |
|-------|-------------|
| glioma | 1,321 |
| meningioma | 1,339 |
| no_tumor | 1,595 |
| pituitary | 1,457 |

### Download & Setup
```bash
# Option 1: Kaggle CLI
pip install kaggle
kaggle datasets download -d masoudnickparvar/brain-tumor-mri-dataset
unzip brain-tumor-mri-dataset.zip -d data/

# Option 2: Direct download from Kaggle website
# https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
```

Expected structure after download:
```
data/
├── Training/
│   ├── glioma/        (1321 images)
│   ├── meningioma/    (1339 images)
│   ├── no_tumor/      (1595 images)
│   └── pituitary/     (1457 images)
└── Testing/
    ├── glioma/        (300 images)
    ├── meningioma/    (306 images)
    ├── no_tumor/      (405 images)
    └── pituitary/     (300 images)
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/<your-org>/brain-tumor-mri-challenge.git
cd brain-tumor-mri-challenge
```

### 2. Install Dependencies
```bash
pip install -r baseline/requirements.txt
```

### 3. Download the Dataset
See [Dataset section](#-dataset) above.

### 4. Train Your Model
Start from our baseline or build your own:
```bash
python baseline/baseline.py
```

### 5. Generate Predictions
Your model should produce a CSV with this format:
```csv
filename,prediction
Te-gl_0010.jpg,0
Te-me_0015.jpg,1
Te-no_0022.jpg,2
Te-pi_0031.jpg,3
```

### 6. Submit
See [Submission Process](#-submission-process) below.

---

## 📤 Submission Process

### Step 1 — Generate Your Predictions
Create `submissions/your_team_name.csv`:
```csv
filename,prediction
Te-gl_0010.jpg,0
Te-me_0015.jpg,1
...
```
- `filename`: exact filename from the test set
- `prediction`: integer label (0=glioma, 1=meningioma, 2=no_tumor, 3=pituitary)

### Step 2 — Encrypt Your Submission
```bash
python encryption/encrypt.py \
  submissions/your_team_name.csv \
  encryption/public_key.pem \
  submissions/your_team_name.enc
```
This produces an encrypted `.enc` file. **The original `.csv` must NOT be committed.**

### Step 3 — Submit via Pull Request
```bash
git checkout -b submission/your-team-name
git add submissions/your_team_name.enc
git commit -m "Submission: Your Team Name"
git push origin submission/your-team-name
```
Then open a **Pull Request** to `main`.

### Step 4 — Wait for Results
- GitHub Actions automatically decrypts and evaluates your submission
- Leaderboard updates in **2–5 minutes**
- You'll see your score in the PR comments

### Rules
- ✅ Maximum **3 submissions per day** per team
- ✅ You may use any model architecture
- ✅ External pre-trained weights allowed (must be declared)
- ❌ Do NOT commit raw prediction `.csv` files
- ❌ Do NOT share or copy other teams' encrypted files
- ❌ Manual label lookup or data leakage is grounds for disqualification

---

## 🔒 Security System

This competition uses an **end-to-end encrypted evaluation pipeline** to keep test labels hidden from all participants.

```
┌─────────────────────────────────────────────────────────┐
│                    HOW IT WORKS                         │
├───────────────┬─────────────────────────────────────────┤
│  YOUR SIDE    │  1. Create predictions.csv              │
│  (Public)     │  2. Encrypt with public_key.pem         │
│               │  3. Submit .enc via Pull Request        │
├───────────────┼─────────────────────────────────────────┤
│  GITHUB       │  4. PR triggers GitHub Actions          │
│  ACTIONS      │  5. Private key (in Secrets) decrypts   │
│  (Automated)  │  6. Predictions scored vs hidden labels │
│               │  7. Leaderboard.csv updated + committed │
└───────────────┴─────────────────────────────────────────┘
```

- 🔑 **Public key**: available in `encryption/public_key.pem` — anyone can encrypt
- 🔐 **Private key**: stored only in GitHub Secrets — never exposed
- 📋 **Test labels**: stored encrypted in the repo — never exposed
- 🤖 **Automated**: no human sees your raw predictions

---

## 📊 Evaluation

Scoring is done using **scikit-learn**:

```python
from sklearn.metrics import f1_score, accuracy_score

# Primary metric
f1 = f1_score(y_true, y_pred, average='weighted')

# Secondary metric  
acc = accuracy_score(y_true, y_pred)
```

Rankings are sorted by **F1 Score (weighted)**, with Accuracy as tiebreaker.

---

## 🛠 Baseline

A CNN baseline using transfer learning (EfficientNet-B0) is provided:

```
baseline/
├── baseline.py        # Training + inference script
└── requirements.txt   # Dependencies
```

Expected baseline performance:
- Accuracy: ~92%
- F1 Score: ~0.91

Beat the baseline and share your approach!

---

## 📂 Repository Structure

```
brain-tumor-mri-challenge/
├── README.md
├── .github/
│   └── workflows/
│       └── evaluate.yml       # Automated evaluation pipeline
├── data/
│   └── README.md              # Data download instructions
├── encryption/
│   ├── public_key.pem         # RSA public key (use to encrypt)
│   ├── encrypt.py             # Encryption script for participants
│   └── README.md
├── submissions/
│   └── *.enc                  # Encrypted team submissions
├── leaderboard/
│   ├── leaderboard.csv        # Live leaderboard
│   └── update_leaderboard.py  # Auto-update script (used by CI)
├── evaluation/
│   ├── evaluate.py            # Scoring logic
│   └── setup_hidden_labels.py # Organizer setup script
├── baseline/
│   ├── baseline.py            # Starter code
│   └── requirements.txt
└── scripts/
    └── generate_keys.py       # Key generation utility
```

---

## 💡 Tips & Resources

- 📖 [Transfer Learning with PyTorch](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- 📖 [EfficientNet Paper](https://arxiv.org/abs/1905.11946)
- 📖 [ResNet for Medical Imaging](https://arxiv.org/abs/1512.03385)
- 🧪 Try data augmentation: rotation, flipping, brightness/contrast changes
- 🧪 Class imbalance: consider weighted loss functions
- 🧪 Preprocessing: crop black borders, normalize pixel values

---

## 📬 Contact

Open an issue for questions, bugs, or feedback.

---

<div align="center">
<sub>Challenge powered by GitHub Actions • Data from <a href="https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset">Kaggle</a></sub>
</div>
