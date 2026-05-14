name: Launchwise URA Pipeline

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  run-pipeline:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Test URA token with curl
        run: |
          curl -v "https://eservice.ura.gov.sg/uraDataService/insertNewToken/v1" \
            -H "AccessKey: b6a1de31-dc9a-47cf-850d-fd602d9209ec"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Run URA pipeline
        run: python pipeline.py
