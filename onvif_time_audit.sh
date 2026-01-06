#!/bin/bash

# ==============================================================================
# Script Name: onvif_time_audit.sh
# Description: Fetches system Date & Time from cameras using ONVIF protocol.
# Dependency: Requires 'onvif-cli' installed (npm install -g onvif-cli)
# ==============================================================================

# --- Configuration ---
INPUT_FILE="ips_teki.txt"
OUTPUT_RAW_FILE="raw_onvif_data.txt"
USER="monitora"
PASS="abcd1234" 

# --- Validation ---
if ! command -v onvif-cli &> /dev/null; then
    echo "ERROR: 'onvif-cli' not found. Please install it."
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "ERROR: Input file '$INPUT_FILE' not found."
    exit 1
fi

echo "--- Starting ONVIF Time Audit at $(date) ---" > "$OUTPUT_RAW_FILE"

# --- Main Loop ---
while IFS=',' read -ra line || [ -n "$line" ]; do
    # Extract IP (first column) and remove whitespace
    ip=$(echo "${line[0]}" | xargs)
    
    if [[ -z "$ip" ]]; then continue; fi

    echo "Processing IP: $ip..."
    
    # Run ONVIF command and append to file
    echo "--- DEVICE: $ip ---" >> "$OUTPUT_RAW_FILE"
    
    # Capture specific time data (grep context)
    onvif-cli --user "$USER" --password "$PASS" --host "$ip" devicemgmt GetSystemDateAndTime \
    | grep -A 4 "LocalDateTime" >> "$OUTPUT_RAW_FILE" 2>&1
    
    # Check if command failed (optional logic could be added here)

done < "$INPUT_FILE"

echo -e "\nAudit completed. Raw data saved to '$OUTPUT_RAW_FILE'."