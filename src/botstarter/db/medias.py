from botstarter.db.base import Base, register_model


@register_model("medias")
class Media(Base):
    """
    A class to represent medias collection
    """


def get_media_by_path(path):
    media = Media.find_one({"path": path})
    return media


def create_media(path, upload_id):
    media = Media({
        "path": path,
        "upload_id": upload_id
    })
    media.save()
    media.reload()
    return media
