"""Tests for authentication key endpoints (public key, JWKS)."""

from fastapi.testclient import TestClient
from unittest.mock import patch
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings


def test_get_public_key_rs256(client: TestClient):
    """Test getting public key when RS256 is enabled."""
    with patch.object(settings, 'JWT_ALGORITHM', 'RS256'), \
         patch.object(settings, 'JWT_PUBLIC_KEY', '-----BEGIN PUBLIC KEY-----\nMOCK_KEY\n-----END PUBLIC KEY-----'):
        response = client.get(f"{settings.API_V1_STR}/auth/public-key")
        assert response.status_code == 200
        assert "BEGIN PUBLIC KEY" in response.text
        logger.info("Public key endpoint test passed")


def test_get_public_key_not_rs256(client: TestClient):
    """Test public key endpoint when not using RS256."""
    with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
        response = client.get(f"{settings.API_V1_STR}/auth/public-key")
        assert response.status_code == 501
        assert "only available when using RS256" in response.json()["detail"].lower()
        logger.info("Public key endpoint (non-RS256) test passed")


def test_get_jwks_rs256(client: TestClient):
    """Test getting JWKS when RS256 is enabled."""
    with patch.object(settings, 'JWT_ALGORITHM', 'RS256'), \
         patch.object(settings, 'JWT_PUBLIC_KEY', '-----BEGIN PUBLIC KEY-----\nMOCK_KEY\n-----END PUBLIC KEY-----'):
        # Mock the cryptography library to avoid actual key parsing
        with patch("app.api.v1.endpoints.auth_keys.serialization.load_pem_public_key") as mock_load:
            mock_key = type('obj', (object,), {
                'public_numbers': type('obj', (object,), {
                    'n': 12345,
                    'e': 65537
                })()
            })()
            mock_load.return_value = mock_key
            
            response = client.get(f"{settings.API_V1_STR}/auth/jwks")
            assert response.status_code == 200
            data = response.json()
            assert "keys" in data
            assert len(data["keys"]) > 0
            assert data["keys"][0]["kty"] == "RSA"
            assert data["keys"][0]["alg"] == "RS256"
            logger.info("JWKS endpoint test passed")

