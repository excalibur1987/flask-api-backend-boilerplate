import io
import uuid
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError
from flask import current_app


class FileStorageInterface:
    data: io.BytesIO
    name: str
    public: bool
    file_url: str
    file_args: Dict[str, str]
    file_object: Any

    def __init__(
        self, data: io.BytesIO, name: str, public: bool = False, url: str = None
    ) -> None:
        pass

    def _get_fileobj_fromurl(self) -> None:
        pass

    def _create_fileobj(self) -> None:
        pass

    def _create_url(self, file_key: str) -> str:
        pass

    def save(
        self,
    ) -> None:
        pass

    def delete(
        self,
    ) -> None:
        pass

    def update(self, data: io.BytesIO, name: str, public: bool = False) -> None:
        pass


class FileStorage:
    handler: FileStorageInterface
    url: str

    def __init__(
        self,
        data: io.BytesIO = None,
        name: str = None,
        public: bool = False,
        url: str = None,
    ) -> None:

        storage_handlers = {"s3": FileStorageS3}
        self.handler = storage_handlers[current_app.config["STORAGE_TARGET"]](
            data,
            name,
            public,
            url,
        )

    def __repr__(self) -> str:
        self.handler.__repr__()

    def _get_fileobj_fromurl(self) -> None:
        self.handler._get_fileobj_fromurl()

    def _create_fileobj(self) -> None:
        self.handler._create_fileobj()

    def save(
        self,
    ) -> None:
        self.handler.save()

    @property
    def url(self):
        return self.handler.file_url

    @url.getter
    def get_url(self):
        return self.handler.file_url

    def delete(
        self,
    ) -> None:
        self.handler.delete()

    def update(self, data: io.BytesIO, name: str, public: bool = False) -> None:
        self.handler.update(data=data, name=name, public=public)


class FileStorageS3(FileStorageInterface):
    def __init__(
        self, data: io.BytesIO, name: str, public: bool = False, url: str = None
    ) -> None:
        self.data = data
        self.name = name
        self.public = public
        self.file_args = {} if not public else {"ACL": "public-read"}

        if url:
            self.file_url = url
            self.file_object = self._get_fileobj_fromurl()
        if data:
            self.file_object = self._create_fileobj()

    def __repr__(self) -> str:
        return self.file_url

    def _get_fileobj_fromurl(
        self,
    ) -> Any:
        protocol = (
            "https" if current_app.config["FLASK_ENV"] == "production" else "http"
        )
        s3_resource = boto3.resource(
            "s3",
            endpoint_url=f"{protocol}://" + current_app.config["AWS_ENDPOINT"],
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        )
        return s3_resource.Object(
            current_app.config["S3_BUCKET_NAME"], self.file_url.split("/")[-1]
        )

    def _create_fileobj(self) -> Any:
        protocol = (
            "https" if current_app.config["FLASK_ENV"] == "production" else "http"
        )
        s3_resource = boto3.resource(
            "s3",
            endpoint_url=f"{protocol}://" + current_app.config["AWS_ENDPOINT"],
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        )

        random_file_name = "".join([str(uuid.uuid4().hex[:6]), self.name])
        return s3_resource.Object(
            current_app.config["S3_BUCKET_NAME"], random_file_name
        )

    def _create_url(self, file_key: str) -> None:
        protocol = (
            "https" if current_app.config["FLASK_ENV"] == "production" else "http"
        )

        self.file_url = f"{protocol}://s3-{current_app.config['AWS_REGION']}.{current_app.config['AWS_ENDPOINT']}/{current_app.config['S3_BUCKET_NAME']}/{file_key}"

    def save(
        self,
    ) -> str:

        self.file_object.upload_fileobj(self.data, ExtraArgs=self.file_args)

        self._create_url(self.file_object.key)

    def delete(self):

        try:
            if self.file_object.content_length > 0:
                _ = self.file_object.delete()
            return True
        except ClientError:
            return False

    def update(self, data: io.BytesIO, name: str, public: bool = False) -> None:
        self.delete()
        self.data = data
        self.name = name
        self.public = public
        self.file_args = {} if not public else {"ACL": "public-read"}
        self.file_object = self._create_fileobj()
        self.save()
