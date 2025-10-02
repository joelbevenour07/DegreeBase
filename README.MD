# DegreeBase

This project aims to handle student registry and management process.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them. For example:

- Python 3.6-3.11
- pip
- virtualenv (optional but recommended)

### Installing

A step-by-step series of examples that tell you how to get a development environment running.

1. Clone the repository:
```git clone https://github.com/joelbevenour07/DegreeBase```

2. Navigate to the project directory:
    ```
    cd DegreeBase
    ```

3. Create a virtual environment (optional but recommended):
- On Windows:
  ```
  py -3 -m venv .venv
  ```
- On Unix or MacOS:
  ```
  python3 -m venv .venv
  ```

4. Activate the virtual environment:
- On Windows:
  ```
  .\\.venv\Scripts\activate
  ```
- On Unix or MacOS:
  ```
  source .venv/bin/activate
  ```

5. Install the required packages:
    ```
    pip install -r requirements.txt
    ```

6. Set environment variables:
- Copy `.env.example` to `.env` and fill it with the appropriate values.
- On Windows:
    ```
    SECRET_KEY="your_secret_key"
    DATABASE_URI="sqlite:///your_db_name.db"
    FLASK_ENV="development"
    ```

7. Run the application:
    ```
    flask run
    ```

## Deployment

Add additional notes about how to deploy this on a live system.

## Built With

- [Flask](http://flask.pocoo.org/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Jinja2](https://jinja.palletsprojects.com/) - Templating Engine


## Authors

- **Kidanewold Demesie** - *Initial work* 
- **Joel Bevenour** - *Backend Development*
- **Nigist Legesse** - *Backend Development*
