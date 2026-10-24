import os
from cloudinary_storage.storage import MediaCloudinaryStorage

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico', '.tiff'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mp3', '.wav', '.ogg'}


class CustomCloudinaryStorage(MediaCloudinaryStorage):
    """
    Universal Cloudinary storage that automatically assigns:
    - 'image' to pictures
    - 'video' to video/audio files
    - 'raw' to documents, PDFs, zip, spreadsheets, and text attachments
    """
    def _get_resource_type(self, name):
        ext = os.path.splitext(name)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            return 'image'
        elif ext in VIDEO_EXTENSIONS:
            return 'video'
        return 'raw'
