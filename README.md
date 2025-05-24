# CardinalCarts

CardinalCart is a web application that we proposed and developed to make purchasing school materials and university merchandise at Mapúa University simpler and more convenient for students, faculty, and staff. Built with Python, Django, and PostgreSQL, this platform aims to provide a seamless online shopping experience tailored to the Mapúa community.

![Description of the image](https://raw.githubusercontent.com/sethlagman/cardinalcarts/main/logo.png)

## Features

- **Easy Browsing**: Browse a wide variety of school materials, merchandise, and other university essentials.
- **Secure Payment**: Use a secure payment system for hassle-free transactions.
- **User-Friendly Interface**: Navigate through the platform effortlessly with an intuitive interface designed for students, faculty, and staff.
- **Personalized Accounts**: Create an account to manage your orders and track your purchase history. Students, faculty, and staff also have different account permissions.
- **Real-time Availability**: Check live availability of items to make sure they’re in stock before placing an order.

## Tech Stack

- **Python**: Main programming language used.
- **Django**: This is the web framework that the app is running on.
- **PostgreSQL**: One of the best DBMS to use with Django.

## Installation

- [X]  [Download Python](https://www.python.org/downloads/release/python-3130/)
- [X]  Clone or download this repository
- [X]  Go to the project directory via CLI or any IDE of your choice
- [X]  Create a virtual environment
    - For Linux or macOS: `python3 -m venv venv`
    - For Windows: `python -m venv venv`
- [X]  Activate the virtual environment
    - For Linux or macOS: `source venv/bin/activate`
    - For Windows: `venv\Scripts\activate`
- [X]  Install the dependencies
    - `pip install -r requirements.txt`
- [X]  Set up environment variables
    - Create .env file
    - Input your keys
    ```
    SECRET_KEY=<django key>
    DB_USER=<db username>
    DB_PASSWORD=<db password>
    DB_NAME=<db name>
    DB_HOST=<db host>
    DB_PORT=<db port>
    ```
- [X]  Change directory to cardinalcarts app
    - `cd cardinalcarts`
- [X]  Run the django app
    - `python manage.py runserver`
- [X]  Navigate to
    - http://127.0.0.1:8000/ or http://127.0.0.1:8000/docs/
- [X]  To deactivate virtual environment
    - `deactivate`

## Setup PostgreSQL

- [X]  Install PostgreSQL
    - For Linux: Use your package manager (e.g., `sudo apt-get install postgresql postgresql-contrib`)
    - For macOS: Use Homebrew (`brew install postgresql`)
    - For Windows: Download the installer from the [official PostgreSQL website](https://www.postgresql.org/download/windows/)
- [X]  Start the PostgreSQL service
    - For Linux: `sudo service postgresql start`
    - For macOS: `brew services start postgresql`
    - For Windows: Start the PostgreSQL service from the Services application or via command line.
- [X]  Access the PostgreSQL shell
    - `psql -U postgres`
- [X]  Create a new database
    - `CREATE DATABASE <db name>;`
- [X]  Create a new user
    - `CREATE USER <db username> WITH PASSWORD '<db password>';`
- [X]  Grant privileges to the user
    - `GRANT ALL PRIVILEGES ON DATABASE <db name> TO <db username>;`
- [X]  Exit the PostgreSQL shell
    - `\q`
- [X]  Update your `.env` file with the database credentials
    - Input your keys
    ```
    SECRET_KEY=<django key>
    DB_USER=<db username>
    DB_PASSWORD=<db password>
    DB_NAME=<db name>
    DB_HOST=<db host>
    DB_PORT=<db port>
    ```
- [X]  Change directory to cardinalcarts app
    - `cd cardinalcarts`
- [X]  Run database migrations
    - `python manage.py makemigrations`
    - `python manage.py migrate`