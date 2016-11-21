#!/usr/bin/env bash
set -e

BUILD_NAME="sxconsole-$1"
OUTPUT_FILE="$BUILD_NAME.tar"
TRANSLATIONS_DIR="sx-translations/sxconsole"
BUILD_TRANSLATIONS_DIR="$BUILD_NAME/$TRANSLATIONS_DIR"

git archive \
    --format tar \
    --prefix "$BUILD_NAME/" \
    --output "$OUTPUT_FILE" \
    "$1"
mkdir -p "$BUILD_TRANSLATIONS_DIR"
cp -r "$TRANSLATIONS_DIR" "$BUILD_TRANSLATIONS_DIR"
tar -f "$OUTPUT_FILE" -u "$BUILD_TRANSLATIONS_DIR"
rm -r "$BUILD_NAME"
gzip "$OUTPUT_FILE"

echo "$OUTPUT_FILE.gz"
