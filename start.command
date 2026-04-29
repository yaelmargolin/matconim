#!/bin/bash
# Double-click this file to open the app.
# It starts a small local web server inside the aNote_App folder and opens your browser.

cd "$(dirname "$0")/aNote_App" || exit 1

PORT=8765
URL="http://localhost:$PORT/"

# If something is already serving on that port, just open the browser.
if curl -s --max-time 1 "$URL" >/dev/null 2>&1; then
  open "$URL"
  exit 0
fi

echo "Starting app at $URL"
echo "Keep this window open while using the app. Close it to stop the server."
echo

( sleep 0.6 && open "$URL" ) &

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m http.server "$PORT" --bind 127.0.0.1
elif command -v python >/dev/null 2>&1; then
  exec python -m SimpleHTTPServer "$PORT"
else
  echo "Python is not installed. Install Python 3 from https://www.python.org/downloads/"
  read -p "Press Enter to close…"
fi
