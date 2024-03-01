Project explanation:
All UST related data processing and figures are in this repository. apps in src directory run scripts for generating figures, tables, and website. 

Project structure
UST/
│
├── data/                     # For now everything in main data directory, can split later
│   ├── raw/                  # Raw data files
│   ├── processed/            # Processed data files
│   └── Shapefile/            # Shapefile data files
│
├── src/                      # Main apps and scripts including Shiny app
│   ├── functions/            # Functions used in scripts
│   ├── exploratory_analysis/ # Scripts for exploratory data analysis
│   └── modeling/             # Scripts for building and evaluating models
│
├── notebooks/                # R Markdown or Jupyter notebooks for documenting analyses
│
├── output/                   # Output files
│
├── environment.yml           # Conda environment file (if using Conda) --not using
├── requirements.txt          # Python dependencies file (if using virtualenv or pip) --what is R equivalent?
├── .gitignore                # Version control
├── README.md                 # Project overview, instructions, and documentation
└── project.Rproj             # RStudio project file --we should make one
