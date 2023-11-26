# Python Web Scraping Project

## Overview
This project is a Python-based web scraping tool that utilizes Beautiful Soup to scrape data from specified websites daily. It is designed to update a database in Turso with fresh data each day. The primary focus is on identifying cheap car deals. The repository includes a "notebooks" folder where analysis and search for inexpensive cars are conducted and a "terraform" folder for AWS deployment.

## Features
- **Daily Data Scraping:** Automated scraping to fetch the latest data every day.
- **Database Integration:** Connects with a Turso database for data storage and retrieval.
- **Car Deal Analysis:** Jupyter notebooks for analyzing and identifying cheap car deals.

## Requirements
- Python 3.x
- Beautiful Soup 4
- Database client for Turso
- Jupyter Notebook (for analysis in the "notebooks" folder)
- Terraform

## Setup
1. **Clone the Repository:**
   ```
   git clone [https://github.com/rlopezvera/cheap-cars-finder.git]
   ```
2. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Database Configuration:**
   - Configure your Turso database credentials in a `.env` files (see `src/database`).

## Usage
1. **Running the Scraper:**
   - Execute the main script to start the scraping process:
     ```
     python src/main.py
     ```
   - This will scrape the websites and update the Turso database daily.
   
2. **Analyzing Car Deals:**
   - Navigate to the "notebooks" folder.
   - Open the Jupyter Notebook `TBD`. #TODO
   - Run the cells to analyze the data and find cheap car deals.
3. **Deploying to AWS:**
   - Navigate to "terraform" folder.
   - Initialize Terraform:
   ```
   terraform init
   ```
   - Apply the Terraform plan:
   ```
   terraform apply
   ```

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License
[MIT License](LICENSE)
