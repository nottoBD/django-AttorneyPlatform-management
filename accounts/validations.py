from django.core.exceptions import ValidationError
from PIL import Image


# validations.py
def validate_image(file):
    valid_formats = ['JPEG', 'PNG', 'GIF']

    try:
        image = Image.open(file)
        image_format = image.format
        if image_format not in valid_formats:
            raise ValidationError('Unsupported file type.')
    except Exception as e:
        raise ValidationError('Invalid image file.')

    file.seek(0)  # Reset file pointer
