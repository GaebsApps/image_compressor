# Web Image Compressor

This Streamlit app allows you to upload multiple images or entire folders and compress them by setting the JPEG quality and maximum target size for the longest image side. You can download the compressed images as a zip file once the process is complete.

## Features

- Upload multiple images or entire folders.
- Set JPEG quality using a slider with increments of 5.
- Set maximum target size for the longest image side using a slider with increments of 10 pixels.
- Compress images and download them as a zip file.

## How to Use

1. **Upload Files**: Upload multiple images or entire folders.
2. **Set JPEG Quality**: Use the slider to set the JPEG quality.
3. **Set Target Size**: Use the slider to set the maximum target size for the longest image side.
4. **Compress Images**: Click "Compress Images" to start the compression process.
5. **Download**: Download all compressed images as a zip file once the process is complete.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GaebsApps/image_compressor.git
   cd image-compressor

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt

## Running the App

Run the Streamlit app:
    ```bash
    streamlit run streamlit_app.py

## Dependencies

    Streamlit
    Pillow
    PyMuPDF

## License

    This project is licensed under the MIT License.
