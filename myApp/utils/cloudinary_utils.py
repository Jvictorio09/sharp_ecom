"""
Cloudinary Utilities
Handles image upload, compression, and URL generation
"""
import io
import logging
from PIL import Image
import cloudinary
import cloudinary.uploader

logger = logging.getLogger(__name__)

# Compression settings
MAX_BYTES = 10 * 1024 * 1024  # 10MB
TARGET_BYTES = int(MAX_BYTES * 0.93)  # 9.3MB target


def smart_compress_to_bytes(image_file, target_bytes=TARGET_BYTES, max_bytes=MAX_BYTES):
    """
    Compress an image to target size while maintaining quality.
    Returns bytes object ready for upload.
    """
    try:
        # Open image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Get current size
        current_bytes = len(image_file.read())
        image_file.seek(0)  # Reset file pointer
        
        # If already small enough, return original
        if current_bytes <= target_bytes:
            return image_file.read()
        
        # Start with high quality
        quality = 85
        output = io.BytesIO()
        
        # Compress in a loop until we hit target size
        while quality > 10:
            output.seek(0)
            output.truncate(0)
            
            # Save with current quality
            img.save(output, format='JPEG', quality=quality, optimize=True)
            size = output.tell()
            
            # If we're close enough, return
            if size <= target_bytes:
                output.seek(0)
                return output.read()
            
            # Reduce quality for next iteration
            quality -= 5
        
        # If still too large, resize image
        if size > max_bytes:
            # Calculate new dimensions (maintain aspect ratio)
            ratio = (max_bytes / size) ** 0.5
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            
            # Resize
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save again
            output.seek(0)
            output.truncate(0)
            img.save(output, format='JPEG', quality=75, optimize=True)
        
        output.seek(0)
        return output.read()
        
    except Exception as e:
        logger.error(f"Error compressing image: {str(e)}")
        # Return original if compression fails
        image_file.seek(0)
        return image_file.read()


def upload_to_cloudinary(image_file, folder="uploads", public_id=None):
    """
    Upload an image to Cloudinary with smart compression.
    Returns dict with URLs and metadata.
    """
    try:
        # Compress image
        compressed_bytes = smart_compress_to_bytes(image_file)
        
        # Create file-like object from bytes
        image_file_obj = io.BytesIO(compressed_bytes)
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            image_file_obj,
            folder=folder,
            public_id=public_id,
            resource_type="image",
            transformation=[
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        
        # Extract URLs
        secure_url = upload_result.get('secure_url', '')
        public_id_result = upload_result.get('public_id', '')
        
        # Generate URL variants
        # Original
        original_url = secure_url
        
        # Web-optimized (WebP, quality 80, max width 1920)
        web_url = secure_url.replace(
            "/upload/",
            "/upload/f_webp,q_80,w_1920/"
        )
        
        # Thumbnail (WebP, quality 80, width 400)
        thumbnail_url = secure_url.replace(
            "/upload/",
            "/upload/f_webp,q_80,w_400/"
        )
        
        return {
            'success': True,
            'original_url': original_url,
            'web_url': web_url,
            'thumbnail_url': thumbnail_url,
            'public_id': public_id_result,
            'width': upload_result.get('width'),
            'height': upload_result.get('height'),
            'bytes': upload_result.get('bytes'),
            'format': upload_result.get('format'),
        }
        
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

