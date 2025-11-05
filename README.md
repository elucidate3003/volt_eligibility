# Volt Eligibility
This repository contains automated UI tests that exercise the Volt Money eligibility flow. The suite drives the public eligibility page, submits mobile/PAN combinations, and verifies the validation and success states exposed to end users.

## Framework overview
- **Pytest**: Provides the core test runner, fixtures, and parametrization support.
- **Selenium WebDriver**: Powers browser automation for interacting with the eligibility form.
- **Google Chrome + Chromedriver**: Default browser stack configured via `utils.browser.initialize_browser`.

## Setup and run instructions
1. Clone the repository: `git clone https://github.com/elucidate3003/volt_eligibility.git` and `cd Volt_Eligibility`.
2. Ensure Python 3.9+ is available. Optionally create a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Install Google Chrome and the matching Chromedriver on your PATH if not already present.
5. Execute the suite: `python -m pytest` (or `python3 -m pytest` on macOS/Linux).
6. To run specific tests or groups of tests:
    ```bash
    # Run all tests in a file
    python -m pytest tests/test_eligibility.py  
    # Run a single test method
    python -m pytest tests/test_eligibility.py::test_mobile_validation
    ```

## Pending items
- Add retry-aware helpers for dynamic validation banners rendered without visible text.
- Document Firefox/WebDriver setup for running the suite on alternate browsers.
