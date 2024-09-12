python3 setup.py build_ext --inplace
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo cp "$SCRIPT_DIR/lib/libCCBS.so" /usr/lib/