#!/bin/bash

# Define the input JSON file and the base dataset path
JSON_FILE="/content/CS5491_AI_Project_Enhanced_FunSearch/dataset_links.json"
BASE_DIR="/content/CS5491_AI_Project_Enhanced_FunSearch/dataset"

# 1. Install dependencies if they are missing (Assumes Debian/Ubuntu)
# We need jq (JSON parser), curl (downloader), and p7zip-full (7z extractor)
echo "Checking dependencies..."
if ! command -v jq &> /dev/null || ! command -v 7z &> /dev/null || ! command -v curl &> /dev/null; then
    echo "Required tools missing. Installing jq, curl, and p7zip-full..."
    sudo apt-get update
    sudo apt-get install -y jq curl p7zip-full
else
    echo "All dependencies are installed."
fi

# 2. Check if the JSON file exists
if [ ! -f "$JSON_FILE" ]; then
    echo "Error: Cannot find '$JSON_FILE' in the current directory."
    echo "Please ensure the file exists or update the JSON_FILE variable."
    exit 1
fi

# 3. Create the base dataset path

mkdir -p "$BASE_DIR"

echo "Starting download and extraction process..."
echo "-----------------------------------------"

# 4. Parse JSON and iterate through key-value pairs
# 'to_entries' converts the JSON object into an array of {key, value} objects
# We use a tab separator (\t) to safely handle names with spaces
jq -r 'to_entries | .[] | "\(.key)\t\(.value)"' "$JSON_FILE" | while IFS=$'\t' read -r name link; do
    
    echo "Processing: $name"
    
    # Create the target subdirectory
    TARGET_DIR="$BASE_DIR/$name"
    mkdir -p "$TARGET_DIR"
    
    # Define a temporary path for the downloaded .7z file
    TEMP_ARCHIVE="/tmp/${name}.7z"
    
    # Download the file
    echo " -> Downloading from $link"
    curl -L -s "$link" -o "$TEMP_ARCHIVE"
    
    # Check if download was successful
    if [ $? -eq 0 ]; then
        echo " -> Extracting to $TARGET_DIR"
        # Extract the archive. '-y' assumes yes to all queries, '-o' sets output dir
        7z x "$TEMP_ARCHIVE" -o"$TARGET_DIR" -y > /dev/null
        
        # Clean up the temporary .7z file
        rm "$TEMP_ARCHIVE"
        echo " -> Done with $name"
    else
        echo " -> Error: Failed to download $link"
    fi
    
    echo "-----------------------------------------"
done

echo "All datasets downloaded successfully."