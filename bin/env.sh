echo "Usage: source ./bin/env.sh"
echo ""

export RRD_HOME="$(cd "$(dirname "$0")"/..; pwd)"
echo "RRD_HOME = $RRD_HOME"

echo "Done!"
