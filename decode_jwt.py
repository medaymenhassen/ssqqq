#!/usr/bin/env python3
"""
Decode JWT token to see what claims it contains
"""

import base64
import json

def decode_jwt_payload(token):
    """Decode JWT payload (middle part)"""
    try:
        # Split the token into parts
        parts = token.split('.')
        if len(parts) != 3:
            print("Invalid JWT token format")
            return None
            
        # Decode the payload (middle part)
        payload = parts[1]
        
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
            
        # Decode base64
        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded_str = decoded_bytes.decode('utf-8')
        
        # Parse JSON
        payload_json = json.loads(decoded_str)
        return payload_json
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

def main():
    # Example JWT token from our tests (this is a sample, not a real one)
    sample_token = "eyJhbGciOiJIUzUxMiJ9.eyJyb2xlIjoiVVNFUiIsInN1YiI6InRlc3RfYmE0aWQ2b2N2dEBleGFtcGxlLmNvbSIsImlhdCI6MTc2NjQwNzk0MCwiZXhwIjoxNzY3MzA3OTQwfQ._ZlX1UHKr5ymt8TNCw3kLPa51yawP2qRm88A15L7ug6pPemZoKD1dwnLkiZzEHA7RP-WHC4yR9qnd-Aril5fTQ"
    
    print("Decoding JWT token payload...")
    payload = decode_jwt_payload(sample_token)
    
    if payload:
        print("JWT Payload:")
        for key, value in payload.items():
            print(f"  {key}: {value}")
            
        # Check if role is present
        if 'role' in payload:
            print(f"\n✅ Role found: {payload['role']}")
        else:
            print("\n❌ Role NOT found in token!")
            print("Available claims:", list(payload.keys()))
    else:
        print("Failed to decode token")

if __name__ == "__main__":
    main()