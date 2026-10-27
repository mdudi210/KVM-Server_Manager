#!/bin/bash

# Script to generate self-signed SSL certificate for internal network use

DOMAIN="${1:-kvm-server.local}"
OUTPUT_DIR="${2:-./ssl}"

echo "Generating SSL certificate for domain: $DOMAIN"
echo "Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate private key
openssl genrsa -out "$OUTPUT_DIR/key.pem" 2048

# Generate certificate signing request
openssl req -new -key "$OUTPUT_DIR/key.pem" -out "$OUTPUT_DIR/cert.csr" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in "$OUTPUT_DIR/cert.csr" -signkey "$OUTPUT_DIR/key.pem" \
    -out "$OUTPUT_DIR/cert.pem" \
    -extensions v3_req \
    -extfile <(echo "[v3_req]"; echo "subjectAltName=DNS:$DOMAIN,DNS:*.$DOMAIN,IP:127.0.0.1")

# Clean up CSR
rm "$OUTPUT_DIR/cert.csr"

# Set permissions
chmod 600 "$OUTPUT_DIR/key.pem"
chmod 644 "$OUTPUT_DIR/cert.pem"

echo "SSL certificate generated successfully!"
echo "Certificate: $OUTPUT_DIR/cert.pem"
echo "Private Key: $OUTPUT_DIR/key.pem"
echo ""
echo "To use with Docker, copy these files to nginx/ssl/ directory"
