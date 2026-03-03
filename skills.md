# skills.md - Datarock Geoscience Data Scientist

## About Me
- Data scientist at Datarock, a company operating in the resources and mining industry
- Primary focus is geosciences - working across exploration, geology, and resource estimation
- Work closely with geologists, mining engineers, and technical stakeholders
- Regularly productionise and templatise repeated workflows for efficiency

## My Tech Stack

### Languages
- Python (primary)
- SQL
- R

### Core Libraries
- pandas, numpy, scipy
- scikit-learn, xgboost, imbalanced-learn
- matplotlib, seaborn, plotly

### Geoscience-Specific Libraries
- striplog (interval/lithology logs)
- pygslib (geostatistics)
- gempy (3D geological modelling)

### Environment & Tools
- VS Code (primary IDE)
- Jupyter Notebooks
- GitHub / Git (version control)
- GitHub Copilot (AI coding assistant)
- Claude / ChatGPT (AI planning and problem solving)

### Data Formats I Work With
- CSV, Excel
- Shapefiles (.shp)
- Drill hole databases (collar, survey, assay, geology tables)
- Block model formats

## Domain Terminology & Concepts

### Drill Hole Data
- Collar table (drill hole location and metadata)
- Survey table (downhole directional survey)
- Assay table (geochemical sample results)
- Geology table (lithological/domain logging)
- Interval data and depth consistency

### Geochemistry
- Multi-element geochemical datasets
- Compositional data (sum to constant)
- Log-ratio transformations (CLR, ILR, ALR)
- QA/QC workflows (duplicates, standards, blanks)
- Anomaly detection and pathfinder elements

### Geology & Classification
- Lithology (rock type classification)
- Geological domaining (defining zones for estimation)
- Alteration mapping
- Automated mineralogy (MLA, QEMSCAN)
- Hyperspectral / SWIR core scanning data

### Geostatistics & Resource Estimation
- Variography (experimental and modelled variograms)
- Kriging and co-kriging
- Block models and grade estimation
- Downhole compositing
- Cross-validation of estimates

### Industry Software Context
- Geoscience Analyst
- Iogas (geochemical analysis)

## Common Workflows I Repeat

### 1. Drill Hole Data Ingestion & Validation
- Loading collar, survey, assay, and geology tables
- Checking for depth gaps, overlaps, and missing intervals
- Survey desurveying (converting depth to 3D coordinates)
- Merging tables into a single working dataset
- Flagging data quality issues before analysis

### 2. Geochemical EDA & QA/QC
- Exploratory data analysis on multi-element datasets
- Log-ratio transformations for compositional data
- Correlation matrices, biplots, PCA
- Duplicate analysis, standards and blanks review
- Outlier detection and population analysis

### 3. Lithology / Domain Classification (ML)
- Feature engineering from assay, spectral, and geophysical data
- Training classifiers (Random Forest, XGBoost primary)
- Handling class imbalance in geological datasets
- Validating predictions against geologist interpretations
- Probability outputs for uncertainty mapping

### 4. Downhole & Spatial Visualisation
- Strip log plots (downhole visualisation)
- Plan maps and cross-section plots
- 3D visualisation of drill hole traces and block models
- Dashboards for non-technical stakeholder reporting

### 5. Workflow Templatisation
- Converting repeated notebook workflows into reusable Python modules
- Building project templates for consistent project structure
- Documenting functions for use by team members

## Code Preferences

### Style
- Python functions over monolithic scripts
- Modular, reusable code organised into logical src/ modules
- Clear docstrings on all functions (NumPy docstring style)
- Inline comments where domain logic needs explanation
- Readable and explicit over clever one-liners

### File & Path Handling
- Always use pathlib for file paths
- Never hardcode absolute paths
- Raw data is never modified after ingestion
- Use .env files for environment variables and sensitive config

### Error Handling
- Always include error handling on file I/O operations
- Validate inputs at function entry (data shape, column names, dtypes)
- Raise informative errors with context e.g. which file, which column

### Dependencies
- Prefer open-source libraries
- Avoid deprecated methods (e.g. pandas .append())
- Pin versions in requirements.txt

## How I Want AI Responses

### General
- Lead with the solution, explain reasoning after
- Keep geoscience and mining industry context in mind at all times
- Do not oversimplify domain-specific nuance
- Flag when a decision is influenced by geological context

### Code Responses
- Code blocks must be copy-paste ready
- Follow my code style preferences above
- Include docstrings and comments in all function suggestions
- Show example usage after function definitions
- If multiple approaches exist, give a clear recommendation first
  then explain alternatives

### Problem Solving
- Clearly state any assumptions made
- If data structure is ambiguous, ask a clarifying question
  rather than assuming
- Suggest validation steps after major data transformations
- Flag potential data quality issues common in drill hole datasets

## Things to Avoid
- Overwriting or mutating raw data
- Hardcoded file paths
- Deprecated pandas/numpy methods
- Returning code without error handling on I/O
- Ignoring compositional data constraints in geochemistry
- Treating geological class labels as having ordinal relationships
