echo "Usage: source ./bin/env.sh"
echo ""

export RRD_HOME="${1:-${PWD}}"
echo "RRD_HOME = $RRD_HOME"

echo "Done!"
