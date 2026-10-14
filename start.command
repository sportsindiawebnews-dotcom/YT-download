#!/bin/bash
# Double-click launcher for the video downloader (Mac)
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 nahi mila. python.org/downloads se install karo, phir dobara chalao."
  read -n 1 -s -r -p "Koi bhi key dabao..."
  exit 1
fi

if [ ! -d venv ]; then
  echo "Pehli baar setup ho raha hai (1-2 minute lagenge)..."
  python3 -m venv venv || exit 1
fi

source venv/bin/activate
pip install -q -r requirements.txt
pip install -q -U yt-dlp

export PORT=5001
echo "Browser khul raha hai: http://localhost:$PORT"
echo "Band karne ke liye ye window band kar do ya Ctrl+C dabao."
(sleep 2 && open "http://localhost:$PORT") &
python app.py
