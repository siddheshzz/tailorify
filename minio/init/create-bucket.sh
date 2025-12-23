#!/bin/sh
mc alias set local http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
mc mb --ignore-existing local/$MINIO_BUCKET_NAME
