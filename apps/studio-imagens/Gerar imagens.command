#!/bin/zsh
cd -- "${0:A:h}"
STUDIO_URL=$("/opt/homebrew/bin/python3" boot.py) || exit 1
/usr/bin/open "$STUDIO_URL"
