#!/bin/bash

git pull origin main || echo "Pullに失敗したけど続けるよ"

TODAY=$(date "+%Y-%m-%d")
NOW=$(date "+%H:%M:%S")

if grep -q "$TODAY" entry_log.csv; then
    echo "今日のエントリーは既に記録されているよ"
    exit 0
fi
echo "$TODAY,$NOW" >> entry_log.csv

uv run plot_graph.py

git add .
git commit -m "Lab Entry: $TODAY"
git push origin main