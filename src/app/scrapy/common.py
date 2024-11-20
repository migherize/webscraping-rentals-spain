import re


def get_all_imagenes(space_images: list) -> list[dict]:
    all_imagenes = []

    if not space_images:
        return []
    for index, value in enumerate(space_images):
        cover = True if index == 0 else False
        all_imagenes.append(
            {
                "image": value,
                "isCover": cover,
            }
        )
    return all_imagenes


def get_all_images(all_url_images: list) -> list:
    
    if not all_url_images:
        return []
    
    all_images = all_url_images.split(',')
    all_images = list(map(lambda url: re.sub(r'\\/', '/', url), all_images))
    all_images = get_all_imagenes(all_images)
    return all_images

def clean_information_html(text):
    """
    This function receives a text with HTML tags and returns the cleaned text.
    
    :param text: str - Text with HTML tags.
    :return: str - Cleaned text without HTML tags.
    """
    # Remove HTML tags
    cleaned = re.sub(r'<.*?>', '', text)  # Remove any HTML tags
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with a single space
    return cleaned.strip()  # Remove leading and trailing whitespace