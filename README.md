
# Flywire Tokenization Integration

This project provides an integration with Flywire for payment tokenization. It allows users to start a tokenization process, display Flywire's hosted form, and handle the confirmation process to save relevant data like `token`, `mandate`, `student_id`, `recipient_id`, and other related information into a database.

---

## Features

1. **Start Tokenization Process**:
   - Captures the `student_id` provided by the user.
   - Sends a payload to Flywire to generate a `session_id` and displays the hosted form.

2. **Confirmation Process**:
   - Processes confirmation from Flywire and updates the database with `token`, `mandate`, and other payment-related details.

3. **Environment Variables**:
   - Uses a `.env` file to configure sensitive values such as `recipient_id` and API keys.

4. **Error Handling**:
   - Robust error handling for incomplete data or issues with Flywire's API.

---

## Technical Requirements

### Software
- **Python 3.8+**
- **Flask 2.0+**
- **SQL Server**
- **Python Libraries**:
  - `pytz`
  - `requests`
  - `python-dotenv`
  - `pyodbc`

### Database Table Structure
Ensure that the `transactions` table in your database has the following structure:

```sql
CREATE TABLE transactions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    student_id NVARCHAR(255) NOT NULL,
    payor_id NVARCHAR(255) NOT NULL,
    session_id NVARCHAR(255) NULL,
    recipient_id NVARCHAR(255) NULL,
    token NVARCHAR(255) NULL,
    mandate NVARCHAR(255) NULL,
    payment_type NVARCHAR(255) NULL,
    brand NVARCHAR(255) NULL,
    card_classification NVARCHAR(255) NULL,
    card_expiration NVARCHAR(10) NULL,
    last_four_digits NVARCHAR(4) NULL,
    country NVARCHAR(10) NULL,
    issuer NVARCHAR(255) NULL,
    transaction_datetime DATETIME NULL
);
```

---

## Setup Instructions

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/gppsys/formflywiretoken.git
cd formflywiretoken
```

### 2. Create a `.env` File
Create a `.env` file in the root of the project with the following variables:

```env
FLYWIRE_API_URL=https://api-platform-sandbox.flywire.com/payments/v1/checkout/sessions
FLYWIRE_CONFIRM_URL=https://api-platform-sandbox.flywire.com/payments/v1/checkout/sessions/{session_id}/confirm
FLYWIRE_API_KEY=your_flywire_api_key
RECIPIENT_ID= 
```

### 3. Install Dependencies
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

### 4. Initialize the Database
If running the project for the first time, initialize the database:
```bash
flask init-db
```

---

## Running the Project

1. Start the Flask development server:
   ```bash
   flask run
   ```

2. Open the application in your browser:
   - Default URL: `http://127.0.0.1:5000`

---

## Repository Structure

```plaintext
.
├── app/
│   ├── __init__.py          # Flask application initialization
│   ├── routes.py            # Routes for Flywire integration
│   ├── utils.py             # Helper functions (e.g., database connection)
├── .env                     # Environment variables (not included in the repo)
├── requirements.txt         # Project dependencies
├── README.md                # Documentation
```

---

## Usage

### 1. Starting the Tokenization Process
- Access the home page (`/`).
- Enter a `student_id` to begin the tokenization process.
- A Flywire-hosted form will be displayed for the user.

### 2. Confirming the Tokenization Process
- Flywire sends confirmation data, which the app processes via the `/confirm` endpoint.
- Data such as `token`, `mandate`, and payment details are saved in the database.

### 3. Verifying Data
To view saved data in your database, run:
```sql
SELECT * FROM transactions;
```

---

## Notes

1. **Production Deployment**:
   - Use a production WSGI server like `gunicorn` or `uwsgi`.
   - Configure HTTPS and other security measures.

2. **Security**:


3. **Error Handling**:
   - If Flywire's API fails, the application redirects the user to a failure page (`/failure`).

---

## Contribution
Feel free to submit issues or pull requests to improve this project.

---
