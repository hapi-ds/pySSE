# Sample Size Estimator

A Python-based web application for determining statistically valid sample sizes for medical device design verification and process validation. Built with Streamlit and designed for Quality Management Systems (QMS) compliance per ISO/TR 80002-2.

## Overview

The Sample Size Estimator provides four specialized statistical analysis modules:

- **Attribute Data Analysis**: Calculate sample sizes for binary pass/fail testing with zero or allowable failures using Success Run Theorem and binomial distributions
- **Variables Data Analysis**: Determine tolerance limits and process capability (Ppk) for continuous measurements following normal distributions
- **Non-Normal Data Handling**: Transform non-normal data using Box-Cox, logarithmic, or square root transformations, with outlier detection and normality testing
- **Reliability Life Testing**: Calculate test durations for zero-failure demonstrations with optional Arrhenius acceleration factors

### Key Features

- **Validated Calculations**: Comprehensive test suite with 100+ property-based tests ensures mathematical correctness
- **Regulatory Compliance**: Full traceability with PDF reports, audit logging, and hash-based validation state tracking
- **User-Friendly Interface**: Tab-based Streamlit UI with contextual help, tooltips, and clear error messages
- **Extensible Architecture**: Modular design using functional programming and Pydantic models for easy extension
- **Complete Documentation**: User guide, developer guide, and validation protocol included

## Requirements

- **Python**: 3.11 or higher
- **Package Manager**: uv (recommended) or pip
- **Operating System**: Windows, macOS, or Linux

## Installation

### Using uv (Recommended)

1. **Install uv** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sample-size-estimator
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```
   
   **Install test browser**:
   ```bash
   uv run playwright install chromium chromium-headless-shell
   ```

   This command:
   - Creates a virtual environment automatically
   - Installs all dependencies with locked versions from `uv.lock`
   - Ensures reproducible installations across environments

4. **Verify installation** (Installation Qualification):
   ```bash
   uv run python scripts/check_environment.py
   ```
   
   This verification script checks:
   - Python version ≥ 3.11
   - All core dependencies installed at correct versions
   - Development dependencies available
   - Project structure complete

5. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (see Configuration section)
   ```

### Using pip

If you prefer pip over uv:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .

# Verify installation
python scripts/check_environment.py
```

## Quick Start

### Running the Application

Start the Streamlit web application:

```bash
# Using uv (recommended)
uv run streamlit run src/sample_size_estimator/app.py

# Using activated virtual environment
streamlit run src/sample_size_estimator/app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

### Basic Usage Example

**Scenario**: Calculate sample size for 95% confidence, 90% reliability, zero failures allowed

1. Open the application
2. Navigate to the **"Attribute (Binomial)"** tab
3. Enter:
   - Confidence Level: `95`
   - Reliability: `90`
   - Allowable Failures: `0`
4. Click **"Calculate Sample Size"**
5. Result: **Sample Size = 29 units**
6. Click **"Download Calculation Report"** to generate PDF documentation

**Interpretation**: Test 29 units. If all pass (zero failures), you have demonstrated 90% reliability with 95% confidence.

## Sample Data and Examples

The `examples/` directory contains sample datasets and quick-start guides to help you get started with the application.

### Available Sample Files

- **sample_data_normal.csv**: Normally distributed data for Variables tab testing
- **sample_data_skewed.csv**: Right-skewed (log-normal) data for transformation testing
- **sample_data_with_outliers.csv**: Dataset with outliers for outlier detection testing
- **sample_data_bimodal.csv**: Bimodal distribution for non-parametric methods
- **sample_data_uniform.csv**: Uniformly distributed data for Box-Cox transformation

### Quick Start Guide

See `examples/QUICK_START.md` for copy-paste examples for each module:
- Attribute calculations with various scenarios
- Variables analysis with process capability
- Non-normal data transformation workflows
- Reliability testing with acceleration factors

### Generating Custom Test Data

Use the included data generator to create custom test datasets:

```bash
uv run python examples/generate_test_data.py
```

This generates additional sample files with various statistical distributions (normal, log-normal, exponential, uniform, bimodal) for comprehensive testing.

### Documentation

- **examples/README.md**: Detailed explanation of each sample file, expected results, and usage instructions
- **examples/QUICK_START.md**: Quick copy-paste examples for immediate testing

## Configuration

Configuration is managed through environment variables for flexible deployment across different environments.

### Configuration File

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Application Settings
APP_TITLE="Sample Size Estimator"
APP_VERSION="1.0.0"

# Logging Configuration
LOG_LEVEL="INFO"                    # DEBUG, INFO, WARNING, ERROR
LOG_FILE="logs/app.log"
LOG_FORMAT="json"                   # json or text

# Validation Settings
VALIDATED_HASH=""                   # SHA-256 hash from validation certificate
CALCULATIONS_FILE="src/sample_size_estimator/calculations/__init__.py"

# Report Settings
REPORT_OUTPUT_DIR="reports"
REPORT_AUTHOR="Sample Size Estimator System"

# Statistical Defaults
DEFAULT_CONFIDENCE=95.0
DEFAULT_RELIABILITY=90.0
```

### Configuration Options

| Parameter | Description | Default | Valid Values |
|-----------|-------------|---------|--------------|
| `APP_TITLE` | Application title displayed in UI | "Sample Size Estimator" | Any string |
| `LOG_LEVEL` | Logging verbosity | "INFO" | DEBUG, INFO, WARNING, ERROR |
| `LOG_FILE` | Path to log file | "logs/app.log" | Any valid file path |
| `VALIDATED_HASH` | SHA-256 hash of validated calculation engine | None | 64-character hex string |
| `REPORT_OUTPUT_DIR` | Directory for generated PDF reports | "reports" | Any valid directory path |

### Setting Validated Hash

After running validation tests and generating the validation certificate:

1. Run validation: `uv run python scripts/generate_validation_certificate.py`
2. Copy the validated hash from the certificate
3. Update `.env`: `VALIDATED_HASH=<hash_value>`
4. Restart the application

The validated hash ensures calculation engine integrity and enables regulatory compliance tracking.

## Usage Guide

### Tab 1: Attribute (Binomial) Analysis

**Use for**: Pass/fail testing, acceptance sampling, reliability demonstrations

**Key Inputs**:
- **Confidence Level (%)**: Statistical confidence (typically 90-95%)
- **Reliability (%)**: Minimum acceptable proportion of conforming units (typically 90-95%)
- **Allowable Failures**: Maximum failures permitted (leave empty for sensitivity analysis)

**Examples**:
- Zero-failure demonstration: C=95%, R=90%, c=0 → n=29
- Sensitivity analysis: C=95%, R=90%, c=empty → Shows n for c=0,1,2,3
- Acceptance sampling: C=95%, R=95%, c=2 → n=93

### Tab 2: Variables (Normal) Analysis

**Use for**: Process capability studies, tolerance limit calculations, continuous measurements

**Key Inputs**:
- **Sample Statistics**: Mean, standard deviation, sample size
- **Confidence/Reliability**: For tolerance limit calculation
- **Specification Limits**: LSL and USL for capability assessment (optional)
- **Sided**: One-sided or two-sided tolerance limits

**Outputs**:
- Tolerance factor (k)
- Upper and lower tolerance limits
- Process performance index (Ppk)
- PASS/FAIL comparison to specifications
- Margins to specification limits

### Tab 3: Non-Normal Distribution Analysis

**Use for**: Data that fails normality tests, skewed distributions, outlier detection

**Workflow**:
1. Enter raw data (comma-separated or one per line)
2. Detect outliers using IQR method
3. Test normality (Shapiro-Wilk and Anderson-Darling tests)
4. View Q-Q plot for visual assessment
5. Apply transformation (Box-Cox, Log, or Square Root)
6. Verify normality of transformed data
7. Calculate tolerance limits on transformed data
8. View back-transformed results in original units

**Transformations**:
- **Box-Cox**: Automatic optimization (best for most cases)
- **Log**: For right-skewed data (requires positive values)
- **Square Root**: For count data or mild skewness

### Tab 4: Reliability Life Testing

**Use for**: Time-dependent reliability testing, accelerated life testing

**Key Inputs**:
- **Confidence/Reliability**: For test duration calculation
- **Number of Failures**: Typically 0 for zero-failure demonstration
- **Acceleration Parameters** (optional):
  - Activation Energy (eV)
  - Use Temperature (K)
  - Test Temperature (K)

**Outputs**:
- Required test duration
- Acceleration factor (if acceleration parameters provided)
- Equivalent test time at use conditions

**Temperature Conversion**: K = °C + 273.15

## Running Tests

The application includes a comprehensive test suite with unit tests, property-based tests, and integration tests.

### Test Execution

```bash
# Run all tests (quiet mode)
uv run pytest -q

# Run all tests with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=src/sample_size_estimator --cov-report=html

# Run specific test file
uv run pytest tests/test_attribute_calcs.py -q

# Run property-based tests only
uv run pytest -k "property" -q

# Run tests for specific URS requirement
uv run pytest -m urs -k "URS-FUNC_A-02" -v

# Run integration tests
uv run pytest tests/test_integration.py -v

# Run UI workflow tests
uv run pytest tests/test_ui_workflows.py -v
```

### Test Coverage

View coverage report after running tests with coverage:

```bash
# Generate HTML coverage report
uv run pytest --cov=src/sample_size_estimator --cov-report=html

# Open report in browser
# Windows:
start htmlcov/index.html
# macOS:
open htmlcov/index.html
# Linux:
xdg-open htmlcov/index.html
```

Target coverage: >85% overall, >90% for calculation modules

### Test Types

- **Unit Tests**: Verify specific examples with known reference values
- **Property-Based Tests**: Verify universal properties across 100+ random inputs using Hypothesis
- **Integration Tests**: Verify complete workflows end-to-end
- **UI Tests**: Verify Streamlit interface behavior using Playwright browser automation

## Code Quality

### Type Checking

Run static type analysis with mypy:

```bash
uv run mypy src/sample_size_estimator
```

The codebase uses comprehensive type hints for all functions and Pydantic models for runtime validation.

### Linting

Check code style and potential issues:

```bash
# Check for issues
uv run ruff check src/

# Check with auto-fix
uv run ruff check --fix src/

# Format code
uv run ruff format src/
```

### Code Standards

- **Style Guide**: PEP 8 with 88-character line length (Black-compatible)
- **Type Hints**: All functions have complete type annotations
- **Docstrings**: Google-style docstrings for all public functions
- **Pure Functions**: All calculation functions are pure (no side effects)

## Deployment

### Local Deployment

For single-user or development use:

```bash
# Start application
uv run streamlit run src/sample_size_estimator/app.py

# Access at http://localhost:8501
```

### Network Deployment

For multi-user access on a network:

```bash
# Start with network access
uv run streamlit run src/sample_size_estimator/app.py --server.address 0.0.0.0 --server.port 8501

# Access from other machines at http://<server-ip>:8501
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose Streamlit port
EXPOSE 8501

# Run application
CMD ["uv", "run", "streamlit", "run", "src/sample_size_estimator/app.py", "--server.address", "0.0.0.0"]
```

Build and run:

```bash
# Build image
docker build -t sample-size-estimator .

# Run container
docker run -p 8501:8501 sample-size-estimator
```

### Production Considerations

For production deployment:

1. **Environment Configuration**: Use environment variables for all configuration
2. **Logging**: Set appropriate log level (INFO or WARNING for production)
3. **Validation State**: Configure validated hash for regulatory compliance
4. **Access Control**: Implement authentication if required
5. **Backup**: Regular backups of logs and generated reports
6. **Monitoring**: Monitor application logs for errors

## Validation

The application includes comprehensive validation testing for regulatory compliance.

### Validation Phases

#### 1. Installation Qualification (IQ)

Verify correct installation of all dependencies:

```bash
uv run python scripts/check_environment.py
```

**Checks**:
- Python version ≥ 3.11
- All dependencies installed at correct versions
- Project structure complete

#### 2. Operational Qualification (OQ)

Verify all calculations produce correct results:

```bash
# Run complete test suite
uv run pytest -q

# Run with coverage
uv run pytest --cov=src/sample_size_estimator --cov-report=html
```

**Coverage**:
- 100+ unit tests with known reference values
- 30+ property-based tests with 100 iterations each
- All URS requirements tested and traced

#### 3. Performance Qualification (PQ)

Verify complete system functionality:

```bash
# Run UI workflow tests
# Run UI tests with Playwright
uv run pytest tests/test_ui_playwright_*.py -v

# Run specific UI test
uv run pytest tests/test_ui_playwright_attribute.py::test_attribute_tab_renders -v

# Interactive debugging with Playwright Inspector
PWDEBUG=1 uv run pytest tests/test_ui_playwright_attribute.py::test_attribute_tab_renders

# Start application for manual exploration
uv run streamlit run src/sample_size_estimator/app.py
```

### Generate Validation Certificate

After successful validation testing:

```bash
uv run python scripts/generate_validation_certificate.py
```

**Certificate Contents**:
- Test execution date and system information
- All URS requirement test results (PASS/FAIL)
- Validated hash of calculation engine
- Overall validation status

**Post-Generation**:
1. Review certificate PDF in `reports/` directory
2. Copy validated hash from certificate
3. Update `.env.example` and `.env` files with the validated hash
4. Store certificate in quality records

For detailed hash update procedures, see [Validation Protocol - Section 9.4](docs/VALIDATION_PROTOCOL.md#94-validated-hash-update-procedure).

### Validation Maintenance

**When to Re-Validate**:
- After any code changes to calculation modules
- After dependency updates
- Periodically per regulatory requirements (e.g., annually)

**Re-Validation Process**:
1. Run complete test suite: `uv run pytest -q`
2. Generate new validation certificate
3. Update validated hash in configuration (see Section 9.4 in Validation Protocol)
4. Document changes in validation records

## Project Structure

```
sample-size-estimator/
├── src/
│   └── sample_size_estimator/
│       ├── __init__.py
│       ├── app.py                    # Main Streamlit application
│       ├── config.py                 # Pydantic settings management
│       ├── models.py                 # Data models with validation
│       ├── logger.py                 # Structured JSON logging
│       ├── validation.py             # SHA-256 hash verification
│       ├── reports.py                # PDF report generation
│       ├── calculations/             # Pure calculation functions
│       │   ├── __init__.py
│       │   ├── attribute_calcs.py   # Binomial sample size
│       │   ├── variables_calcs.py   # Tolerance limits and Ppk
│       │   ├── non_normal_calcs.py  # Transformations and outliers
│       │   └── reliability_calcs.py # Life testing and acceleration
│       └── ui/                       # Streamlit UI components
│           ├── __init__.py
│           ├── attribute_tab.py     # Attribute analysis UI
│           ├── variables_tab.py     # Variables analysis UI
│           ├── non_normal_tab.py    # Non-normal analysis UI
│           └── reliability_tab.py   # Reliability analysis UI
├── tests/                            # Comprehensive test suite
│   ├── conftest.py                  # Pytest configuration and fixtures
│   ├── test_attribute_calcs.py      # Attribute calculation tests
│   ├── test_variables_calcs.py      # Variables calculation tests
│   ├── test_non_normal_calcs.py     # Non-normal calculation tests
│   ├── test_reliability_calcs.py    # Reliability calculation tests
│   ├── test_validation.py           # Hash verification tests
│   ├── test_reports.py              # PDF generation tests
│   ├── test_config.py               # Configuration tests
│   ├── test_logger.py               # Logging tests
│   ├── test_models.py               # Data model tests
│   ├── test_integration.py          # End-to-end workflow tests
│   ├── test_ui_playwright_attribute.py    # Playwright UI tests
│   ├── test_ui_playwright_variables.py
│   ├── test_ui_playwright_non_normal.py
│   └── test_ui_playwright_reliability.py
├── scripts/
│   ├── check_environment.py         # IQ verification script
│   └── generate_validation_certificate.py  # Validation certificate generator
├── docs/
│   ├── USER_GUIDE.md                # Detailed usage instructions
│   ├── DEVELOPER_GUIDE.md           # Architecture and extension guide
│   └── VALIDATION_PROTOCOL.md       # IQ/OQ/PQ procedures
├── logs/                            # Application logs (created at runtime)
├── reports/                         # Generated PDF reports (created at runtime)
├── pyproject.toml                   # Project configuration and dependencies
├── uv.lock                          # Locked dependency versions
├── .env.example                     # Example environment configuration
├── .gitignore                       # Git ignore patterns
└── README.md                        # This file
```

### Key Directories

- **`src/sample_size_estimator/`**: Main application code
  - **`calculations/`**: Pure calculation functions (no UI, no I/O)
  - **`ui/`**: Streamlit UI components (one file per tab)
- **`tests/`**: All test files (unit, property, integration, UI)
- **`scripts/`**: Utility scripts for validation and environment checks
- **`docs/`**: User and developer documentation
- **`logs/`**: Application logs (JSON format for audit trail)
- **`reports/`**: Generated PDF calculation reports and validation certificates

## Documentation

Comprehensive documentation is provided for different audiences:

### For Users

**[User Guide](docs/USER_GUIDE.md)** - Complete usage instructions including:
- Detailed explanation of each analysis module
- Step-by-step examples with real scenarios
- Interpretation of results
- Report generation and validation state
- Troubleshooting common issues

### For Developers

**[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Technical documentation including:
- Architecture overview and design principles
- Component interfaces and data flow
- Adding new analysis modules
- Testing approach (unit + property-based + Playwright UI tests)
- Configuration management
- Code style and standards

### For Quality/Validation

**[Validation Protocol](docs/VALIDATION_PROTOCOL.md)** - Regulatory compliance documentation including:
- IQ/OQ/PQ procedures
- URS requirements traceability matrix
- Test execution instructions
- Validation certificate generation
- Validation maintenance procedures

## Troubleshooting

### Common Issues

**Issue**: Application won't start
```bash
# Check Python version
python --version  # Should be ≥ 3.11

# Verify installation
uv run python scripts/check_environment.py

# Reinstall dependencies
uv sync
```

**Issue**: Tests failing
```bash
# Run tests with verbose output to see details
uv run pytest -v

# Check specific failing test
uv run pytest tests/test_attribute_calcs.py::test_name -v
```

**Issue**: Validation state shows "NOT VALIDATED"
- This is normal if validated hash is not configured
- Run validation and set validated hash in `.env` file
- See Validation section above

**Issue**: Import errors
```bash
# Ensure you're using uv run or activated virtual environment
uv run python -c "import sample_size_estimator"

# Or activate virtual environment first
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Getting Help

For issues and questions:

1. Check the [User Guide](docs/USER_GUIDE.md) for usage questions
2. Check the [Developer Guide](docs/DEVELOPER_GUIDE.md) for technical questions
3. Review test output for specific error messages
4. Check application logs in `logs/app.log`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Code Style**: Follow PEP 8 and use type hints
2. **Testing**: Add tests for new functionality (unit + property tests)
3. **Documentation**: Update relevant documentation
4. **Validation**: Ensure all tests pass before submitting

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/new-analysis-module

# Make changes and add tests
# ...

# Run tests
uv run pytest -q

# Run type checking
uv run mypy src/sample_size_estimator

# Run linting
uv run ruff check src/

# Commit changes
git commit -m "Add new analysis module"

# Push and create pull request
git push origin feature/new-analysis-module
```

## License

[Add your license information here]

## Acknowledgments

This application implements statistical methods from:
- ISO/TR 80002-2: Medical device software validation
- NIST/SEMATECH e-Handbook of Statistical Methods
- Statistical Quality Control literature

## Support

For technical support or validation questions:
- Contact your Quality Assurance department
- Review documentation in `docs/` directory
- Check application logs for error details

---

**Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: [Add maintainer information]
