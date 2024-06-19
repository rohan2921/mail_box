# Project Title

## Overview
This project leverages the Gmail API and a database to play with your emails. This README will guide you through the prerequisites, installation, and setup process to get the project running on your local machine.

## Prerequisites
Before you begin, ensure you have met the following requirements:

1. **Gmail API Setup**:
   - Follow the instructions provided at the [Gmail API Quickstart for Python](https://developers.google.com/gmail/api/quickstart/python) to set up the Gmail API.
   - Ensure you have the `credentials.json` file, which is required for authentication. Keep a note of the path of the file.

2. **Database Setup**:
   - Create a database and a role with login permission and note the host, username, password, port and database name. 
3. **Install Python Package**:
   - Clone the repository from GitHub:
     ```sh
     git clone https://github.com/rohan2921/mail_box.git
     ```
   - Navigate to the project directory:
     ```sh
     cd mail_box
     ```
   - Install the required Python packages using pip:
     ```sh
     pip install -r requirements.txt
     ```

## Usage
To run the project, follow these steps:

1. **Initialize the Database**:
   - Add the database url E.g: "postgresql://scp:scp@172.18.0.2:5432/mail_box" to DATABASE_URL in db_helpers module in mail_box package.
   - Then run the following command from teh root
     ```sh
     alembic upgrade head
     ```

2. **Using the functionality**:
   - Look at the example.py to understand the usage of the package.
