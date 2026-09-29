# Automation Exercise – UI Test Automation Framework

A simple, maintainable Page Object Model (POM) UI automation framework for
[automationexercise.com](https://automationexercise.com/), built with
**Python 3.11, Pytest, Playwright (Sync API), pytest-playwright, Allure and Ruff**.

It covers three business scenarios:

1. **Product Search** – CSV-driven search for products (Blue Top, Men Tshirt, Winter Top).
2. **Login Validation** – valid user, valid email/invalid password, unknown email.
3. **Add Product to Cart** – search, open a product, add to cart, verify cart contents.

---

## 1. Project Structure

```
automation-exercise-framework/
├── conftest.py                # Shared fixtures: config, credentials, page setup, ad handling, Allure evidence
├── pytest.ini                 # Pytest config: markers, Allure results dir
├── pyproject.toml             # Ruff (lint + format) configuration
├── requirements.txt           # Python dependencies
├── .env.example                # Template for required environment variables
├── .gitignore
├── config/
│   └── config.yaml            # Application & framework configuration (base URL, browser, timeouts, ad selectors)
├── data/
│   ├── search_products.csv    # Test data for Product Search
│   ├── login_data.csv         # Test data for Login Validation
│   └── cart_products.csv      # Test data for Add to Cart
├── pages/                     # Page Object Model
│   ├── home_page.py
│   ├── login_page.py
│   ├── products_page.py
│   └── cart_page.py
├── utilities/                 # Small, genuinely reusable helpers
│   ├── csv_reader.py          # Generic CSV -> list[dict] reader
│   ├── yaml_reader.py         # Generic YAML -> dict reader
│   └── ad_handler.py          # Central, reusable ad/overlay dismissal logic
├── tests/
│   ├── test_product_search.py
│   ├── test_login.py
│   └── test_add_to_cart.py
└── reports/
    └── allure-results/        # Raw Allure results (generated at run time)
```

### Design notes

- **Page Objects** hold locators and user-facing actions only (no assertions
  baked in, except small `expect()` auto-waits needed to keep flows stable).
  Assertions live in the tests, where business intent belongs.
- **No unnecessary base classes/wrappers.** Each page object is a plain class
  built directly on the Playwright `Page`; there is no `BasePage`, factory, or
  driver-manager layer, since pytest-playwright already manages the browser
  lifecycle.
- **Ad/overlay handling is centralized** in `utilities/ad_handler.py` and is
  wired into the `page` fixture in `conftest.py` (it runs automatically after
  every navigation). Individual tests and page objects never need to know
  about ads.
- **Test data lives in CSV** (`data/*.csv`) and is loaded via
  `utilities/csv_reader.py`, then fed straight into `pytest.mark.parametrize`.
- **Configuration lives in YAML** (`config/config.yaml`) and is loaded via
  `utilities/yaml_reader.py` through a session-scoped `config` fixture.
- **Credentials never live in code or CSV.** The valid training-user
  credentials are read from environment variables in the `credentials`
  fixture. The CSV for login uses the sentinel values `ENV_EMAIL` /
  `ENV_PASSWORD`, which the test resolves at runtime.

---

## 2. Prerequisites

- Python 3.11+
- Google Chrome installed (the framework launches Playwright's Chromium
  using the `chrome` channel, i.e. your real installed Chrome binary)

---

## 3. Setup

```bash
# 1. Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers (only Chromium/Chrome is required here)
playwright install chromium
# If you don't have Google Chrome installed system-wide, you can instead let
# Playwright manage a Chrome build:
playwright install chrome
```

### Required environment variables

The valid training-user credentials must be provided via environment
variables — never hard-code them.

```bash
export AUTOMATION_EXERCISE_EMAIL="TestQA@test.com"
export AUTOMATION_EXERCISE_PASSWORD="testqa@ae26"
```

On Windows PowerShell:

```powershell
$env:AUTOMATION_EXERCISE_EMAIL="TestQA@test.com"
$env:AUTOMATION_EXERCISE_PASSWORD="testqa@ae26"
```

A `.env.example` file is provided as a template — copy it to `.env` and load
it with your shell/CI of choice (e.g. `export $(cat .env | xargs)`), or set
the variables directly. `.env` is git-ignored.

> **Note:** The account above must already be registered on
> automationexercise.com for the "valid login" scenario to pass. Register it
> once manually via the site's Signup form if it doesn't exist yet.

---

## 4. Running the Tests

Run the full suite:

```bash
pytest
```

Run a single business scenario using markers:

```bash
pytest -m search        # Product Search
pytest -m login         # Login Validation
pytest -m cart          # Add Product to Cart
pytest -m smoke         # Smoke subset
pytest -m regression    # Full regression subset
```

Run a specific test file or a specific parametrized case:

```bash
pytest tests/test_login.py
pytest tests/test_login.py -k "TC_LOGIN_01_valid_credentials"
```

Run headed (see the browser) or in a different browser channel:

```bash
pytest --headed
```

> Headless/headed and the Chrome channel are configured by default in
> `config/config.yaml` (`browser.headless`, `browser.channel`). Toggle
> `headless: false` there for local debugging, or pass `--headed` /
> `--browser-channel` flags supported by pytest-playwright to override
> per run.

Run tests in parallel (optional, requires `pytest-xdist`):

```bash
pip install pytest-xdist
pytest -n auto
```

---

## 5. Reporting (Allure)

Allure results are written to `reports/allure-results` automatically (configured
in `pytest.ini` and `config/config.yaml`). Failure evidence (a full-page
screenshot and the page URL) is attached automatically via a Pytest hook in
`conftest.py`.

Generate and view the HTML report:

```bash
# Install the Allure command-line tool once (see https://allurereport.org/docs/install/)
allure generate reports/allure-results --clean -o reports/allure-report
allure open reports/allure-report
```

Or serve it directly without a separate generate step:

```bash
allure serve reports/allure-results
```

Each test in the report includes:

- A business-readable **title** and **description**
- **Feature** / **Story** grouping (e.g. Feature: "Authentication", Story: "Login Validation")
- Step-by-step **Allure steps** describing the user journey
- Screenshot + URL evidence attached automatically on failure

---

## 6. Code Quality (Ruff)

Lint the codebase:

```bash
ruff check .
```

Auto-fix lint issues where possible:

```bash
ruff check . --fix
```

Format the codebase:

```bash
ruff format .
```

Ruff configuration (rule set, line length, import sorting) lives in
`pyproject.toml`.

---

## 7. Extending the Framework

- **New business scenario:** add a CSV file under `data/`, a page object
  under `pages/` if new UI is involved, and a test module under `tests/`
  following the existing pattern (Allure feature/story/steps + CSV-driven
  parametrization).
- **New reusable helper:** only add it to `utilities/` if it is genuinely
  reusable across multiple tests/pages (e.g. another file-format reader).
  Avoid adding one-off logic there.
- **New ad/overlay pattern:** add its CSS selector to `ads.overlay_selectors`
  in `config/config.yaml` — no code changes required.
- **New environment/config value:** add it to `config/config.yaml` and read
  it via the existing `config` fixture; use environment variables only for
  secrets.

---

## 8. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `pytest.fail(...)` about missing env vars | Export `AUTOMATION_EXERCISE_EMAIL` / `AUTOMATION_EXERCISE_PASSWORD` before running |
| Browser fails to launch with `channel: chrome` | Install Google Chrome, or run `playwright install chrome` |
| Ads intercept a click intermittently | Add the new overlay's selector to `config/config.yaml` under `ads.overlay_selectors` |
| Allure CLI not found | Install it separately — it's a Java-based CLI, not a pip package (`allure-pytest` only produces raw results) |
