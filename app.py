"""Python 3.14 compatible Streamlit image exploration demo.

This application intentionally has no TensorFlow, Keras, OpenCV, or pickled
machine-learning dependency. It is designed to deploy reliably on Streamlit
Community Cloud with Python 3.14.

It is an educational visualisation tool, not a medical device. It does not
diagnose cancer or estimate a patient's probability of cancer.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageOps


@dataclass(frozen=True)
class ImageMetrics:
    """Simple, deterministic image statistics for display in the UI."""

    width: int
    height: int
    brightness: float
    contrast: float
    edge_density: float
    dark_area: float


def normalise_image(image: Image.Image) -> Image.Image:
    """Return a consistently oriented RGB image with a safe size."""
    result = ImageOps.exif_transpose(image).convert("RGB")
    result.thumbnail((1600, 1600))
    return result


def image_metrics(image: Image.Image) -> ImageMetrics:
    """Calculate non-diagnostic visual statistics with NumPy only."""
    gray = np.asarray(image.convert("L"), dtype=np.float32) / 255.0
    gradient_y, gradient_x = np.gradient(gray)
    edge_strength = np.hypot(gradient_x, gradient_y)

    return ImageMetrics(
        width=image.width,
        height=image.height,
        brightness=float(gray.mean() * 100),
        contrast=float(gray.std() * 100),
        edge_density=float((edge_strength > 0.08).mean() * 100),
        dark_area=float((gray < 0.25).mean() * 100),
    )


def annotated_preview(image: Image.Image) -> Image.Image:
    """Create a grayscale preview with edges highlighted for visual inspection."""
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_array = np.asarray(edges, dtype=np.uint8)
    base = np.asarray(gray, dtype=np.uint8)
    overlay = np.stack((base, base, base), axis=-1)
    mask = edge_array > 55
    overlay[mask] = (30, 150, 225)
    return Image.fromarray(overlay, mode="RGB")


def synthetic_demo_image(seed: int) -> Image.Image:
    """Generate a clearly labelled synthetic test image without an AI model."""
    rng = np.random.default_rng(seed)
    height, width = 512, 512
    y, x = np.ogrid[:height, :width]
    distance = np.sqrt(((x - width / 2) / 1.15) ** 2 + ((y - height / 2) / 0.75) ** 2)
    background = 28 + 45 * np.exp(-(distance / 175) ** 2)
    noise = rng.normal(0, 11, size=(height, width))
    pixels = np.clip(background + noise, 0, 255).astype(np.uint8)
    image = Image.fromarray(pixels, mode="L").convert("RGB")

    draw = ImageDraw.Draw(image)
    draw.ellipse((170, 185, 350, 320), outline=(230, 230, 230), width=2)
    draw.text((15, 15), "SYNTHETIC DEMO - NOT A MEDICAL IMAGE", fill=(255, 205, 70))
    return image


def png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def show_metrics(metrics: ImageMetrics) -> None:
    first, second, third, fourth = st.columns(4)
    first.metric("Dimensions", f"{metrics.width} x {metrics.height}")
    second.metric("Brightness", f"{metrics.brightness:.1f}%")
    third.metric("Contrast", f"{metrics.contrast:.1f}%")
    fourth.metric("Edge density", f"{metrics.edge_density:.1f}%")
    st.caption(
        f"Dark-pixel share: {metrics.dark_area:.1f}%. These are image properties, "
        "not clinical findings or a cancer-risk prediction."
    )


def inspect_image(image: Image.Image) -> None:
    image = normalise_image(image)
    metrics = image_metrics(image)
    original, preview = st.columns(2)
    with original:
        st.image(image, caption="Uploaded image", use_container_width=True)
    with preview:
        rendered = annotated_preview(image)
        st.image(
            rendered,
            caption="Grayscale preview with highlighted edges",
            use_container_width=True,
        )
    show_metrics(metrics)
    st.download_button(
        "Download edge preview",
        data=png_bytes(rendered),
        file_name="image-edge-preview.png",
        mime="image/png",
    )


def image_workspace() -> None:
    st.header("Image workspace")
    st.write(
        "Upload an image or take a picture. The tool displays safe visual statistics "
        "and an edge preview using Pillow and NumPy."
    )
    st.info(
        "This is not an ultrasound diagnostic model. Do not use it to diagnose, "
        "rule out, or make treatment decisions for cancer."
    )

    source = st.radio("Choose an image source", ["Upload image", "Camera", "Synthetic demo"])
    image: Image.Image | None = None

    if source == "Upload image":
        upload = st.file_uploader(
            "Choose a JPG, JPEG, PNG, or WEBP image",
            type=["jpg", "jpeg", "png", "webp"],
        )
        if upload is not None:
            image = Image.open(upload)
    elif source == "Camera":
        capture = st.camera_input("Take a picture")
        if capture is not None:
            image = Image.open(capture)
    else:
        seed = st.number_input("Demo-image seed", min_value=0, max_value=99_999, value=42)
        image = synthetic_demo_image(int(seed))

    if image is not None:
        try:
            inspect_image(image)
        except Exception as error:
            st.error(f"The image could not be read: {error}")


def clinical_reference() -> None:
    st.header("Clinical discussion reference")
    st.warning(
        "This page is an educational discussion aid. It does not calculate cancer "
        "risk and is not a substitute for a qualified clinician or radiologist."
    )
    category = st.selectbox("Reported TI-RADS category", ["Not provided", "2", "3", "4a", "4b", "4c", "5"])
    age = st.number_input("Age (optional)", min_value=0, max_value=120, value=None, step=1)
    notes = st.text_area("Questions or notes for a clinician (optional)")

    if st.button("Show discussion prompt", type="primary"):
        if category == "Not provided":
            st.info("Ask a qualified clinician to explain the imaging category and next steps.")
        else:
            st.info(
                f"You selected TI-RADS {category}. Discuss the report, relevant symptoms, "
                "and whether follow-up imaging or specialist review is appropriate with a clinician."
            )
        if age is not None:
            st.caption(f"Age recorded for your own discussion notes: {age} years.")
        if notes.strip():
            st.caption("Your notes stay in this browser session and are not stored by the app.")


def about() -> None:
    st.header("About this rebuild")
    st.markdown(
        """
This Python 3.14 edition replaces the old TensorFlow/Keras image runtime with:

- Streamlit's built-in uploader and camera widgets.
- Pillow for image loading, orientation correction, filtering, preview generation, and PNG export.
- NumPy for deterministic brightness, contrast, edge-density, and dark-area calculations.

There are no TensorFlow, Keras, OpenCV, or scikit-learn dependencies. This keeps
the deployment small and compatible with Python 3.14 on Streamlit Community Cloud.
        """
    )


def main() -> None:
    st.set_page_config(page_title="Thyroid Image Explorer", page_icon="T", layout="wide")
    st.title("Thyroid Image Explorer")
    st.caption("Python 3.14 and Streamlit Community Cloud compatible")

    page = st.sidebar.radio("Navigate", ["Image workspace", "Clinical reference", "About"])
    st.sidebar.divider()
    st.sidebar.caption("Lightweight stack: Streamlit + Pillow + NumPy")

    if page == "Image workspace":
        image_workspace()
    elif page == "Clinical reference":
        clinical_reference()
    else:
        about()


if __name__ == "__main__":
    main()
