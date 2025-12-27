from pydantic import BaseModel


class DownloanLinkSchemaOut(BaseModel):
    download_link: str


class UploadTestFileSchemaOut(BaseModel):
    s3_object_path: str


class DownloadTestFileSchemaOut(BaseModel):
    downloaded_file_path: str


class UploadUrlSchemaOut(BaseModel):
    url: str
    s3_object_path: str
    content_type: str = "application/octet-stream"
