# Thyroid Image Explorer (Python 3.14)

A lightweight Streamlit rebuild that runs on Python 3.14 without TensorFlow,
Keras, OpenCV, scikit-learn, or the legacy model files.

## Why this version is different

The original project depends on TensorFlow/Keras models. The Streamlit Cloud
deployment log shows that `tensorflow==2.20.0` has no Python 3.14 package, so
that stack cannot be deployed on Python 3.14. This rebuild uses only packages
with Python 3.14-compatible releases:

- Streamlit for the user interface, file uploader, camera input, and deployment.
- Pillow for reliable image opening, resize/orientation correction, filtering,
  synthetic demo-image generation, and PNG output.
- NumPy for lightweight image-statistic calculations.

## Features

- Upload JPG, JPEG, PNG, or WEBP images.
- Capture an image through the Streamlit camera widget.
- Generate a synthetic demo image with no model download or external API.
- Review brightness, contrast, edge density, and dark-area share.
- Download the generated edge-highlight preview.

The app is educational only. It does **not** diagnose cancer, estimate cancer
risk, or replace a clinician or radiologist.

## Run with one click on Windows

1. Install Python 3.14 and enable the Python launcher (`py`) during setup.
2. Double-click `run_app.bat`.
3. Wait for the first dependency installation. The app opens at
   `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository containing the files in this `new__project` folder.
2. In Streamlit Community Cloud, select the repository and set the main file to
   `app.py`.
3. In **Advanced settings**, select **Python 3.14**.
4. Select **Deploy**.

The three packages in `requirements.txt` are installed automatically.

## Git CMD commands

From this folder, run:

```bat
git init
git add .
git commit -m "Create Python 3.14 Streamlit image explorer"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
