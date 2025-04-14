name: PHP Linting

on:
  pull_request:

jobs:
  lint:
    name: Execute PHP Linting
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up PHP 8
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'

      - name: Run PHP Lint
        uses: michaelw90/php-lint@master
