# Data

The dataset is **not stored in this repository** (too large). Download it from Kaggle.

## Download

```bash
# Option 1: Kaggle CLI (recommended)
pip install kaggle
kaggle datasets download -d masoudnickparvar/brain-tumor-mri-dataset
unzip brain-tumor-mri-dataset.zip -d data/

# Option 2: Manual download
# Visit: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
# Download and extract into this data/ folder
```

## Expected Structure

```
data/
├── Training/
│   ├── glioma/       (1321 images)
│   ├── meningioma/   (1339 images)
│   ├── no_tumor/     (1595 images)
│   └── pituitary/    (1457 images)
└── Testing/
    ├── glioma/       (300 images)
    ├── meningioma/   (306 images)
    ├── no_tumor/     (405 images)
    └── pituitary/    (300 images)
```

## Label Mapping

| Integer | Class Name |
|---------|-----------|
| 0 | glioma |
| 1 | meningioma |
| 2 | no_tumor |
| 3 | pituitary |

## Notes

- Image sizes vary — resize to 224×224 before training
- Remove black borders in preprocessing for better accuracy
- The **Testing/** folder images are the ones you must predict for submission
