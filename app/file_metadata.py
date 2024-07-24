import PIL
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
import PIL.TiffImagePlugin


def get_image_metadata(image=None) -> dict:
    picture = Image.open(f"./app/uploads/{image}")
    pic_exif = picture.getexif()
    file_metadata = {TAGS[key]: value for key, value in pic_exif.items()if type(
        value) != PIL.TiffImagePlugin.IFDRational}
    return file_metadata
