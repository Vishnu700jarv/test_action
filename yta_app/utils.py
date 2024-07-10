import csv
import os
from django.conf import settings
import base64
from PIL import Image
from io import BytesIO


class CSVLogger:
    def __init__(self, filename='upload_backlog.csv', subfolder='logs'):
        # Construct the path to the folder where the CSV files will be stored
        log_directory = os.path.join(settings.MEDIA_ROOT, subfolder)
        
        # Ensure the directory exists, create if it does not
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)  # Create the logs directory if it doesn't exist
        
        # Set up the full filepath for the CSV file
        self.filepath = os.path.join(log_directory, filename)
        
        # Check if the file exists already, and if not, create it and write headers
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date-Time', 'Job Name', 'Path'])

    def append(self, datetime, job_name, image_path):
        # Open the CSV file and append a new row with the job details
        with open(self.filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.strftime('%Y-%m-%d %H:%M:%S'), job_name, image_path])






class ImageToBase64Converter:
    def __init__(self, image_path):
        self.image_path = image_path

    def convert_image_to_base64(self):
        with Image.open(self.image_path) as image:
            # Detect if the image has an alpha channel (transparency)
            if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                # Convert the image to RGBA if it has transparency, to handle it correctly
                image = image.convert('RGBA')
            else:
                # Otherwise, convert the image to RGB
                image = image.convert('RGB')
            
            # Save the image to a bytes buffer
            buffered = BytesIO()
            image.save(buffered, format="PNG")  # Saving as PNG to keep transparency intact if present
            # Encode the bytes buffer to Base64
            img_str = base64.b64encode(buffered.getvalue())
            return img_str.decode('utf-8')

    def save_base64_to_image(self, base64_string, output_path):
        # Decode the base64 string to bytes
        image_data = base64.b64decode(base64_string)
        # Create a bytes buffer from the decoded data
        image_buffer = BytesIO(image_data)
        # Open the image from the bytes buffer
        image = Image.open(image_buffer)
        # Save the image to the specified path in PNG format
        image.save(output_path, format="PNG")