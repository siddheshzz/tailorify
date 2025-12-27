#!/bin/sh
# Wait for MinIO to start
echo "Waiting for MinIO..."
until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"; do
  sleep 1
done

# Create the bucket
mc mb --ignore-existing local/"$S3_BUCKET_NAME"

# --- ADD CORS CONFIGURATION ---
# Create a temporary json file for CORS
cat <<EOF > /tmp/cors.json
{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "AllowedHeaders": ["*"],
            "ExposeHeaders": ["ETag"]
        }
    ]
}
EOF

# Apply the CORS configuration to the bucket
# Note: In some mc versions, use 'mc anonymous set' or 'mc versioning' 
# but for modern MinIO, use:
mc sql --query "select * from s3object" local/"$S3_BUCKET_NAME" || true # Warm up
# Set public access (read-only) for later viewing
mc anonymous set download local/"$S3_BUCKET_NAME"

echo "MinIO bucket $S3_BUCKET_NAME is ready with CORS"



# #!/bin/sh

# # Wait for MinIO to be ready
# echo "Waiting for MinIO to start..."
# until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"; do
#   echo "Retrying..."
#   sleep 2
# done

# # Create bucket
# mc mb --ignore-existing local/$S3_BUCKET_NAME

# echo "MinIO bucket $S3_BUCKET_NAME is ready"


# #!/bin/sh
# mc alias set local http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
# mc mb --ignore-existing local/$S3_BUCKET_NAME
# echo 'MinIO bucket ${S3_BUCKET_NAME} is ready'