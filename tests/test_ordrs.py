from unittest.mock import patch
import pytest

@pytest.mark.asyncio
async def test_generate_upload_url(client, user_token_headers):
    # We "intercept" the S3 call so it doesn't try to connect to MinIO
    with patch("app.core.s3_api.S3Service.generate_presigned_upload_url") as mock_s3:
        mock_s3.return_value = ("http://fake-s3-url.com/put", "orders/test-path.jpg")
        
        # Now call your actual API endpoint
        response = await client.get(
            "/api/v1/orders/00000000-0000-0000-0000-000000000000/generate-upload-url", 
            headers=user_token_headers
        )
        
        assert response.status_code == 200
        assert "url" in response.json()
        assert response.json()["url"] == "http://fake-s3-url.com/put"


