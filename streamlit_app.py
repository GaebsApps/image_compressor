import streamlit as st
import os
import zipfile
from PIL import Image, ExifTags
import fitz  # PyMuPDF

def resize_images_in_directory(directory, target_size, quality):
    compressed_folder = os.path.join(directory, "compressed_images")
    os.makedirs(compressed_folder, exist_ok=True)
    
    for root, dirs, files in os.walk(directory):
        images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.tif', '.tiff'))]

        for image_file in images:
            # Skip already compressed images
            if 'compressed' in image_file:
                continue
            
            try:
                image_path = os.path.join(root, image_file)
                if image_file.lower().endswith('.pdf'):
                    # Handle PDF
                    pdf_document = fitz.open(image_path)
                    for page_num in range(len(pdf_document)):
                        page = pdf_document.load_page(page_num)
                        pix = page.get_pixmap()
                        pdf_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        # Save each page as an image
                        new_file_name = f"{os.path.splitext(image_file)[0]}_page_{page_num}_compressed.jpg"
                        new_file_path = os.path.join(compressed_folder, new_file_name)
                        pdf_image.save(new_file_path, 'JPEG', quality=quality)
                else:
                    with Image.open(image_path) as img:
                        if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            # Handle EXIF orientation for JPEG and PNG
                            for orientation in ExifTags.TAGS.keys():
                                if ExifTags.TAGS[orientation] == 'Orientation':
                                    break

                            exif = img._getexif()
                            if exif is not None:
                                exif = dict(exif.items())
                                orientation = exif.get(orientation, 1)

                                if orientation == 3:
                                    img = img.rotate(180, expand=True)
                                elif orientation == 6:
                                    img = img.rotate(270, expand=True)
                                elif orientation == 8:
                                    img = img.rotate(90, expand=True)

                        width, height = img.size
                        if max(width, height) <= target_size:
                            # Image is smaller than target size, just compress
                            resized_img = img
                        else:
                            if width > height:
                                new_width = target_size
                                new_height = int((target_size / width) * height)
                            else:
                                new_height = target_size
                                new_width = int((target_size / height) * width)

                            resized_img = img.resize((new_width, new_height), Image.LANCZOS)

                        new_file_name = f"{os.path.splitext(image_file)[0]}_compressed"
                        if resized_img.mode == 'RGBA' and image_file.lower().endswith('.png'):
                            # Keep PNG with alpha
                            new_file_path = os.path.join(compressed_folder, new_file_name + '.png')
                            resized_img.save(new_file_path, 'PNG')
                        else:
                            # Convert RGBA to RGB if necessary and save as JPEG
                            if resized_img.mode == 'RGBA':
                                resized_img = resized_img.convert('RGB')
                            new_file_path = os.path.join(compressed_folder, new_file_name + '.jpg')
                            resized_img.save(new_file_path, 'JPEG', quality=quality)

            except Exception as e:
                st.error(f"Error processing {image_file}: {e}")

    return compressed_folder


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 
                           os.path.join(folder_path, '..')))

def clean_up(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    if os.path.exists(directory):
        os.rmdir(directory)

# Streamlit app layout
st.title("🖼️ Web Image Optimizer")
st.write("**Compressing images** before uploading to your website is a game-changer for **speedy load times**, **awesome user experience**, and **cutting bandwidth costs**. High-res images can drag your site down, so let's compress them! With this app, you can **bulk compress images** in no time, keeping your site **fast and smooth**.")
st.header("How to use")
st.write("""
1. Upload multiple images or entire folders.
2. Set the JPEG quality using the slider.
3. Set the maximum target size for the longest image side using the slider.
4. Click "Compress Images".
5. Download all compressed images as a zip file once the process is complete.
""")

st.markdown("---")
st.write("")

uploaded_files = st.file_uploader("Upload multiple images", type=['png', 'jpg', 'jpeg', 'pdf', 'tif', 'tiff'], accept_multiple_files=True)

st.write("")
st.write("")

# Combined slider and input field for JPEG quality with increments of 5
quality = st.slider("JPEG Quality in %", 5, 100, 50, step=5, format="%d")

# Combined slider and input field for target size with increments of 10
target_size = st.slider("Target Size (long side)", 500, 3000, 1500, step=10, format="%d")

if st.button("Compress Images"):
    if uploaded_files:
        with st.spinner("Compressing images..."):
            # Create a temporary directory to save uploaded files
            temp_directory = "temp_upload"
            os.makedirs(temp_directory, exist_ok=True)

            # Save uploaded files to the temporary directory
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_directory, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Resize and compress images
            compressed_folder = resize_images_in_directory(temp_directory, target_size, quality)

            # Zip the compressed folder
            zip_path = "compressed_images.zip"
            zip_folder(compressed_folder, zip_path)

            st.success("Compression finished.")
            st.download_button("Download Compressed Images", data=open(zip_path, "rb"), file_name="compressed_images.zip")

            # Clean up temporary directories and files
            clean_up(temp_directory)
            clean_up(compressed_folder)
    else:
        st.warning("Please upload at least one image.")
