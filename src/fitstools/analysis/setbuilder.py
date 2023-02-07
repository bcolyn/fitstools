from typing import Iterable

from fitstools.analysis.metadata import MetadataAnalyser
from fitstools.db.database_peewee import *
from fitstools.model import NormalizedImageMeta, ImageType

import logzero
from logzero import logger


class SetBuilder:

    @staticmethod
    def combine():
        images = 0
        sets = 0
        combinable = [ImageType.LIGHT, ImageType.DARK, ImageType.BIAS, ImageType.FLAT]
        images_with_meta = SetBuilder.find_unmatched_images()
        for image in images_with_meta:
            image_meta = MetadataAnalyser.normalize(image.get_header(), image.file.full_filename())
            if image_meta.img_type in combinable:
                matching_set = SetBuilder.find_matching_set(image_meta, image.file.path, image.file.root.get_id())
                if matching_set is None:
                    matching_set = SetBuilder.create_set(image_meta, image.file.path, image.file.root.get_id())
                    sets += 1
                image.image_set = matching_set.get_id()
                image.save()
                images += 1
        return images, sets

    @staticmethod
    def find_matching_set(image_meta: NormalizedImageMeta, path: str, root_id: int):
        where_clauses = [ImageSet.path == path,
                         ImageSet.root == root_id,
                         ImageSet.img_type == image_meta.img_type.name,
                         ImageSet.capture_date == image_meta.session_date(),
                         ImageSet.object_name == image_meta.object_name,
                         ImageSet.filter == image_meta.filter,
                         ImageSet.exposure == image_meta.exposure,  # TODO: +/- 1s?
                         ImageSet.camera_name == image_meta.camera_name,
                         ImageSet.xbin == image_meta.xbin,
                         ImageSet.ybin == image_meta.ybin,
                         ImageSet.offset == image_meta.offset,
                         ImageSet.telescope == image_meta.telescope,
                         ImageSet.gain == image_meta.gain]
        if image_meta.camera_temperature is not None:
            where_clauses.append(
                ImageSet.camera_temperature.between(image_meta.camera_temperature - 1,
                                                    image_meta.camera_temperature + 1))
        else:
            where_clauses.append(ImageSet.camera_temperature.is_null())

        matching_set = ImageSet.select().where(*where_clauses).get_or_none()
        return matching_set

    @staticmethod
    def find_unmatched_images() -> Iterable[Image]:
        images = Image.select(Image, File).join(File).where(Image.image_set.is_null())
        meta = ImageMeta.select()
        images_with_meta = prefetch(images, meta)
        return images_with_meta

    @classmethod
    def create_set(cls, image_meta: NormalizedImageMeta, path: str, root_id: int) -> ImageSet:
        return ImageSet.create(root=root_id,
                               path=path,
                               img_type=image_meta.img_type.name,
                               exposure=image_meta.exposure,
                               camera_name=image_meta.camera_name,
                               camera_temperature=image_meta.camera_temperature,
                               object_name=image_meta.object_name,
                               filter=image_meta.filter,
                               xbin=image_meta.xbin,
                               ybin=image_meta.ybin,
                               gain=image_meta.gain,
                               offset=image_meta.offset,
                               telescope=image_meta.telescope,
                               capture_date=image_meta.session_date(),
                               )
