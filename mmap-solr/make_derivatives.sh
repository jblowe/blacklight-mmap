#!/usr/bin/env bash
set -x
# set -euo pipefail

# md.sh — build "derivative" (thumbnail) images in a parallel directory tree.
#
# Usage:
#   ./md.sh [options] ORIGINAL_DIR DERIVATIVES_DIR
#
# Options:
#   --clean            Remove existing contents of DERIVATIVES_DIR before processing
#   --size N           Max pixel dimension (default: 512)
#   --quality N        JPEG quality (default: 65)
#   --dry-run          Show what would be done, but do not run ImageMagick
#
# Notes:
# - Keeps the same relative directory hierarchy under DERIVATIVES_DIR.
# - Image files keep their original extension.
# - PDF files: first page only, written as JPEG (.pdf -> .jpg)

CLEAN=0
DRYRUN=0
SIZE=512
QUALITY=65

# Parse options
while [[ $# -gt 0 ]]; do
  case "$1" in
    --clean)
      CLEAN=1
      shift
      ;;
    --dry-run)
      DRYRUN=1
      shift
      ;;
    --size)
      SIZE="${2:?Missing value for --size}"
      shift 2
      ;;
    --quality)
      QUALITY="${2:?Missing value for --quality}"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

ORIGINAL_DIR="${1:-}"
DERIVATIVES_DIR="${2:-}"

if [[ -z "${ORIGINAL_DIR}" || -z "${DERIVATIVES_DIR}" ]]; then
  echo "Usage: $0 [options] ORIGINAL_DIR DERIVATIVES_DIR" >&2
  exit 2
fi

if [[ ! -d "${ORIGINAL_DIR}" ]]; then
  echo "Could not find directory: ${ORIGINAL_DIR}" >&2
  exit 1
fi

mkdir -p "${DERIVATIVES_DIR}"

if [[ "${CLEAN}" -eq 1 ]]; then
  if [[ -n "${DERIVATIVES_DIR}" && "${DERIVATIVES_DIR}" != "/" ]]; then
    echo "Cleaning derivatives directory: ${DERIVATIVES_DIR}"
    rm -rf "${DERIVATIVES_DIR:?}/"*
  fi
fi

LIST_FILE="$(pwd)/files-to-convert.txt"
RESULT_FILE="$(pwd)/files-to-convert-converted.txt"
rm -f "${LIST_FILE}" "${RESULT_FILE}"

# Collect candidates
while IFS= read -r -d '' f; do
  rel="${f#${ORIGINAL_DIR}/}"
  printf '%s\n' "${rel}" >> "${LIST_FILE}"
done < <(
  find "${ORIGINAL_DIR}" -type f \(     -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.gif' \
    -o -iname '*.tif' -o -iname '*.tiff' -o -iname '*.webp' -o -iname '*.pdf'   \) -print0
)

LINES=0

while IFS= read -r rel; do
  [[ -z "${rel}" ]] && continue
  ((LINES++))

  src="${ORIGINAL_DIR}/${rel}"
  out_rel="${rel}"
  ext="${rel##*.}"
  ext_lc="$(printf '%s' "${ext}" | tr '[:upper:]' '[:lower:]')"

  if [[ "${ext_lc}" == "pdf" ]]; then
    out_rel="${rel%.*}.jpg"
  fi

  dest="${DERIVATIVES_DIR}/${out_rel}"
  mkdir -p "$(dirname "${dest}")"

  if [[ -e "${dest}" ]]; then
    printf '%s\n' "${dest}" >> "${RESULT_FILE}"
    continue
  fi

  # on ubuntu, it's still called convert
  # CMD=(magick -density 200)
  CMD=(convert -density 200)

  if [[ "${ext_lc}" == "pdf" ]]; then
    CMD+=("${src}[0]")
  else
    CMD+=("${src}")
  fi

  CMD+=(
    -background white -alpha remove
    -resize "${SIZE}x${SIZE}>"
    -strip
    -interlace JPEG
    -sampling-factor 4:2:0
    -quality "${QUALITY}"
    "${dest}"
  )

  if [[ "${DRYRUN}" -eq 1 ]]; then
    echo "[dry-run] ${CMD[*]}"
  else
    "${CMD[@]}"
  fi

  printf '%s\n' "${dest}" >> "${RESULT_FILE}"
done < "${LIST_FILE}"

echo "${LINES} files processed"
echo "Wrote: ${RESULT_FILE}"
