<!-- Thanks for sharing the first set of APIs! I’ll create the API documentation for the endpoints you’ve provided so far. Let’s break down the APIs, explaining their purpose, request/response format, and error handling.

### 1. **Get Users API**

**Endpoint:** `/api/get-users/`
**Method:** `GET`
**Description:** Fetches a list of all registered users except the authenticated user.

**Request Headers:**

- Cookies:
  - `user_id`: The authenticated user's ID.
  - `email`: The authenticated user's email.

**Response:**

- **Success:**
  Status: 200 OK
  ```json
  {
    "status": "success",
    "message": "All Registered Data",
    "status_code": 200,
    "available_user_count": 5,
    "data": [
      {
        "user_id": 2,
        "name": "John Doe",
        "email": "john@example.com",
        ...
      },
      ...
    ]
  }
  ```
- **Error (Authentication Failed):**
  Status: 400 Bad Request
  ```json
  {
    "status": "error",
    "message": "Authentication Failed",
    "status_code": 400
  }
  ```

### 2. **User Registration API**

**Endpoint:** `/api/register/`
**Method:** `POST`
**Description:** Registers a new user by saving their data after encrypting the password.

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "mobile_no": "1234567890"
}
```

**Response:**

- **Success:**
  Status: 200 OK
  ```json
  {
    "status": "success",
    "message": "User Registered successfully",
    "encrypted_password": "<encrypted_password>",
    "user": {
      "user_id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "mobile_no": "1234567890"
    }
  }
  ```
- **Error (Validation Failed):**
  Status: 400 Bad Request
  ```json
  {
    "status": "error",
    "message": {
      "email": ["This field is required."],
      "password": ["This field is required."]
    }
  }
  ```

### 3. **User Login API**

**Endpoint:** `/api/login/`
**Method:** `POST`
**Description:** Authenticates the user by verifying email and password.

**Request Body:**

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**

- **Success:**
  Status: 200 OK

  ```json
  {
    "status": "success",
    "message": "Login successful",
    "user": {
      "user_id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    },
    "status": 200
  }
  ```

  Cookies:

  - `user_id`: User ID
  - `email`: User email

- **Error (User Does Not Exist):**
  Status: 204 No Content

  ```json
  {
    "status": "error",
    "message": "User does not exist",
    "status_code": 204
  }
  ```

- **Error (Invalid Credentials):**
  Status: 400 Bad Request
  ```json
  {
    "status": "error",
    "message": "Invalid password or check email id",
    "status_code": 400
  }
  ```

### 4. **User Logout API**

**Endpoint:** `/api/logout/`
**Method:** `POST`
**Description:** Logs the user out by clearing their session.

**Response:**

- **Success:**
  Status: 200 OK
  ```json
  {
    "status": "success",
    "message": "Logout successful",
    "status_code": 200
  }
  ```

---

# Expense Management API

## Base URL
```
/expenses/
```

## Endpoints

### 1. Get Expense Details
- **Endpoint:** `/getexpensesbyid`
- **Method:** `GET`
- **Description:** Retrieves the details of an expense for a specific expense ID, ensuring the user has access to it.

#### Request Parameters
| Parameter     | Type   | Description                               |
|---------------|--------|-------------------------------------------|
| expense_id    | string | The unique identifier of the expense.    |

#### Request Headers
| Header        | Type   | Description                               |
|---------------|--------|-------------------------------------------|
| Cookie        | string | Must include `user_id` and `email`.      |

#### Response Format
- **Success Response (200 OK)**:
```json
{
    "status": "success",
    "message": "Expense retrieved successfully.",
    "status_code": 200,
    "data": {
        "description": "Expense description",
        "total_amount": 100.00,
        "split_method": "EQUAL",
        "created_at": "2024-10-21T10:00:00Z",
        "total_participants": 3,
        "participants": [
            {
                "user_id": 1,
                "amount_paid": 50.00,
                "amount_owed": 50.00
            },
            ...
        ]
    }
}
```

- **Error Responses**:
    - **403 Forbidden**:
    ```json
    {
        "status": "error",
        "message": "You do not have access to this expense.",
        "status_code": 403
    }
    ```
    - **404 Not Found**:
    ```json
    {
        "status": "error",
        "message": "Expense not found.",
        "status_code": 404
    }
    ```

### 2. Equal Distribution
- **Endpoint:** `/equal`
- **Method:** `POST`
- **Description:** Creates an expense and splits the total amount equally among specified users.

#### Request Body
```json
{
    "user_list": [
        {"user_id": 1},
        {"user_id": 2}
    ],
    "total_amount": 100.00,
    "description": "Group Dinner"
}
```

#### Request Headers
| Header        | Type   | Description                               |
|---------------|--------|-------------------------------------------|
| Cookie        | string | Must include `user_id` and `email`.      |

#### Response Format
- **Success Response (201 Created)**:
```json
{
    "status": "success",
    "message": "Expense successfully added and split equally.",
    "expense_id": 1,
    "description": "Group Dinner",
    "total_amount": 100.00,
    "split_method": "EQUAL",
    "each_user_share": 50.00,
    "no_of_participants": 2,
    "participants": [
        {
            "user_id": 1,
            "user_name": "Alice",
            "amount_paid": 100.00,
            "amount_owed": 0.00
        },
        ...
    ]
}
```

- **Error Responses**:
    - **404 Not Found**:
    ```json
    {
        "status": "error",
        "message": "User not found.",
        "status_code": 404
    }
    ```
    - **400 Bad Request**:
    ```json
    {
        "status": "error",
        "message": "Authentication Failed",
        "status_code": 400
    }
    ```

### 3. Unequal Distribution
- **Endpoint:** `/unequal`
- **Method:** `POST`
- **Description:** Creates an expense with specified amounts for each user, ensuring the total matches the specified amount.

#### Request Body
```json
{
    "user_list": [
        {"user_id": 1, "amount": 30.00},
        {"user_id": 2, "amount": 70.00}
    ],
    "total_amount": 100.00,
    "description": "Team Lunch"
}
```

#### Response Format
- **Success Response (201 Created)**:
```json
{
    "status": "success",
    "message": "Expense successfully added with custom splits.",
    "expense_id": 2,
    "description": "Team Lunch",
    "total_amount": 100.00,
    "split_method": "UNEQUAL",
    "participants": [
        {
            "user_id": 1,
            "user_name": "Bob",
            "amount_paid": 0.00,
            "amount_owed": 30.00,
            "split_expenses": 30.00
        },
        ...
    ]
}
```

- **Error Responses**:
    - **400 Bad Request**:
    ```json
    {
        "status": "error",
        "message": "Split does not sum up to the total amount. Please check.",
        "status_code": 400
    }
    ```

### 4. Percentage Distribution
- **Endpoint:** `/percentage`
- **Method:** `POST`
- **Description:** Creates an expense with specified percentage splits for each user, validating that the total percentages sum to 100.

#### Request Body
```json
{
    "user_list": [
        {"user_id": 1, "percentage": 40},
        {"user_id": 2, "percentage": 60}
    ],
    "total_amount": 100.00,
    "description": "Project Dinner"
}
```

#### Response Format
- **Success Response (201 Created)**:
```json
{
    "status": "success",
    "message": "Expense successfully added with percentage-based splits.",
    "expense_id": 3,
    "description": "Project Dinner",
    "total_amount": 100.00,
    "split_method": "PERCENTAGE",
    "participants": [
        {
            "user_id": 1,
            "user_name": "Charlie",
            "percentage": 40,
            "amount_paid": 0.00,
            "amount_owed": 40.00,
            "split_expenses": 40.00
        },
        ...
    ]
}
```

- **Error Responses**:
    - **400 Bad Request**:
    ```json
    {
        "status": "error",
        "message": "Total percentages must add up to 100.",
        "status_code": 400
    }
    ```

---

### General Error Responses
- **400 Bad Request**:
```json
{
    "status": "error",
    "message": "Error description.",
    "status_code": 400
}
```
- **404 Not Found**:
```json
{
    "status": "error",
    "message": "Resource not found.",
    "status_code": 404
}
```
- **403 Forbidden**:
```json
{
    "status": "error",
    "message": "Access denied.",
    "status_code": 403
}
```
- **500 Internal Server Error**:
```json
{
    "status": "error",
    "message": "An error occurred.",
    "status_code": 500
}
```
Here’s a documentation template for the provided Django views, including details about their functionality, parameters, and expected responses.

---

# API Documentation for Balance Sheet

## Overview
This document outlines the API endpoints for managing balance sheets in a daily expenses sharing application. The application allows users to track their expenses and generate balance sheets that can be viewed or downloaded as PDF reports.

## Endpoints

### 1. Overall Balance Sheet

**URL:** `/api/overall-balance-sheet/`
**Method:** `GET`
**Authentication:** Required (through middleware)

#### Description
This endpoint retrieves the overall balance sheet for the authenticated user, showing total expenses created, amounts owed, and amounts paid. It also provides details on expenses where the user is involved, either as a creator or a participant.

#### Request Parameters
- `download` (optional): A boolean value (`true` or `false`) to indicate if the response should be in PDF format.

#### Response
- **Status Code:** `200 OK` - On success, with the following JSON structure:
  ```json
  {
    "user_id": "string",
    "total_expenses_created": "float",
    "total_owed_by_user": "float",
    "total_paid_by_user": "float",
    "give_expenses": [
      {
        "expense_id": "string",
        "description": "string",
        "created_by": "string",
        "is_creator": "boolean",
        "total_owed": "float",
        "give_to": {
          "user_name": "string",
          "amount": "float"
        }
      }
    ],
    "get_expenses": [
      {
        "expense_id": "string",
        "description": "string",
        "created_by": "string",
        "is_creator": "boolean",
        "total_paid": "float",
        "owes": [
          {
            "user_name": "string",
            "amount_owed": "float"
          }
        ]
      }
    ]
  }
  ```

- **Status Code:** `404 NOT FOUND` - If the user is not found:
  ```json
  {
    "status": "error",
    "message": "User not found.",
    "status_code": 404
  }
  ```

- **Status Code:** `500 INTERNAL SERVER ERROR` - On unexpected errors:
  ```json
  {
    "status": "error",
    "message": "string",
    "status_code": 500
  }
  ```

---

### 2. Individual Balance Sheet

**URL:** `/api/individual-balance-sheet/`
**Method:** `GET`
**Authentication:** Required (through middleware)

#### Description
This endpoint retrieves the individual balance sheet for the authenticated user. It displays the total expenses paid by the user, a detailed list of those expenses, and the total amount owed to the user by others.

#### Request Parameters
- `download` (optional): A boolean value (`true` or `false`) to indicate if the response should be in PDF format.

#### Response
- **Status Code:** `200 OK` - On success, with the following JSON structure:
  ```json
  {
    "user_id": "string",
    "total_expenses": "float",
    "expenses": [
      {
        "expense_id": "string",
        "description": "string",
        "user_expense": "float"
      }
    ],
    "total_user_expenses": "float",
    "total_owed_to_user": "float"
  }
  ```

- **Status Code:** `400 BAD REQUEST` - If authentication fails (no user_id in cookies):
  ```json
  {
    "status": "error",
    "message": "Authentication Failed",
    "status_code": 400
  }
  ```

- **Status Code:** `404 NOT FOUND` - If the user is not found:
  ```json
  {
    "status": "error",
    "message": "User not found.",
    "status_code": 404
  }
  ```

- **Status Code:** `500 INTERNAL SERVER ERROR` - On unexpected errors:
  ```json
  {
    "status": "error",
    "message": "string",
    "status_code": 500
  }
  ```

---

## Error Handling
Each endpoint provides detailed error messages for various failure scenarios. Common status codes include:
- `200 OK` for successful requests.
- `400 BAD REQUEST` for client-side errors, such as authentication failures.
- `404 NOT FOUND` for missing users.
- `500 INTERNAL SERVER ERROR` for server-side issues.

## Middleware
Authentication is enforced using a custom middleware (`AuthenticationMiddleware`), which verifies that the user is authenticated before processing the request.

## Logging
The application uses a console logger (`setup_console_logger()`) to log important events and errors, aiding in debugging and monitoring.

---

Feel free to modify or expand upon this template as needed to fit your project requirements! -->

Here's a structured and detailed API documentation based on your provided endpoints:

---

# API Documentation for Daily Expenses Sharing Application

## Overview

This document outlines the API endpoints for managing user accounts and expenses in a daily expenses sharing application. The application allows users to register, log in, manage expenses, and generate balance sheets, which can be viewed or downloaded as PDF reports.

## User Management APIs

### 1. Get Users API

- **Endpoint:** `/api/get-users/`
- **Method:** `GET`
- **Description:** Fetches a list of all registered users except the authenticated user.

#### Request Headers:

- **Cookies:**
  - `user_id`: The authenticated user's ID.
  - `email`: The authenticated user's email.

#### Response:

- **Success (200 OK):**
  ```json
  {
    "status": "success",
    "message": "All Registered Data",
    "status_code": 200,
    "available_user_count": 5,
    "data": [
      {
        "user_id": 2,
        "name": "John Doe",
        "email": "john@example.com"
      }
    ]
  }
  ```
- **Error (Authentication Failed, 400 Bad Request):**
  ```json
  {
    "status": "error",
    "message": "Authentication Failed",
    "status_code": 400
  }
  ```

### 2. User Registration API

- **Endpoint:** `/api/register/`
- **Method:** `POST`
- **Description:** Registers a new user by saving their data after encrypting the password.

#### Request Body:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "mobile_no": "1234567890"
}
```

#### Response:

- **Success (200 OK):**
  ```json
  {
    "status": "success",
    "message": "User Registered successfully",
    "user": {
      "user_id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "mobile_no": "1234567890"
    }
  }
  ```
- **Error (Validation Failed, 400 Bad Request):**
  ```json
  {
    "status": "error",
    "message": {
      "email": ["This field is required."],
      "password": ["This field is required."]
    }
  }
  ```

### 3. User Login API

- **Endpoint:** `/api/login/`
- **Method:** `POST`
- **Description:** Authenticates the user by verifying email and password.

#### Request Body:

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

#### Response:

- **Success (200 OK):**

  ```json
  {
    "status": "success",
    "message": "Login successful",
    "user": {
      "user_id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
  ```

  **Cookies:**

  - `user_id`: User ID
  - `email`: User email

- **Error (User Does Not Exist, 204 No Content):**
  ```json
  {
    "status": "error",
    "message": "User does not exist",
    "status_code": 204
  }
  ```
- **Error (Invalid Credentials, 400 Bad Request):**
  ```json
  {
    "status": "error",
    "message": "Invalid password or check email id",
    "status_code": 400
  }
  ```

### 4. User Logout API

- **Endpoint:** `/api/logout/`
- **Method:** `POST`
- **Description:** Logs the user out by clearing their session.

#### Response:

- **Success (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Logout successful",
    "status_code": 200
  }
  ```

---

## Expense Management APIs

### Base URL

```
/expenses/
```

### 1. Get Expense Details

- **Endpoint:** `/getexpensesbyid`
- **Method:** `GET`
- **Description:** Retrieves the details of an expense for a specific expense ID, ensuring the user has access to it.

#### Request Parameters:

- **Query Parameter:** `expense_id` (string) - The unique identifier of the expense.

#### Request Headers:

- **Cookie:** Must include `user_id` and `email`.

#### Response:

- **Success (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Expense retrieved successfully.",
    "status_code": 200,
    "data": {
      "description": "Expense description",
      "total_amount": 100.0,
      "split_method": "EQUAL",
      "participants": [
        {
          "user_id": 1,
          "amount_paid": 50.0,
          "amount_owed": 50.0
        }
      ]
    }
  }
  ```
- **Error (403 Forbidden):**
  ```json
  {
    "status": "error",
    "message": "You do not have access to this expense.",
    "status_code": 403
  }
  ```
- **Error (404 Not Found):**
  ```json
  {
    "status": "error",
    "message": "Expense not found.",
    "status_code": 404
  }
  ```

### 2. Equal Distribution

- **Endpoint:** `/equal`
- **Method:** `POST`
- **Description:** Creates an expense and splits the total amount equally among specified users.

#### Request Body:

```json
{
  "user_list": [{ "user_id": 1 }, { "user_id": 2 }],
  "total_amount": 100.0,
  "description": "Group Dinner"
}
```

#### Response:

- **Success (201 Created):**
  ```json
  {
    "status": "success",
    "message": "Expense successfully added and split equally.",
    "expense_id": 1,
    "description": "Group Dinner",
    "total_amount": 100.0,
    "each_user_share": 50.0,
    "participants": [
      {
        "user_id": 1,
        "user_name": "Alice",
        "amount_paid": 100.0,
        "amount_owed": 0.0
      }
    ]
  }
  ```
- **Error (404 Not Found):**
  ```json
  {
    "status": "error",
    "message": "User not found.",
    "status_code": 404
  }
  ```
- **Error (400 Bad Request):**
  ```json
  {
    "status": "error",
    "message": "Authentication Failed",
    "status_code": 400
  }
  ```

### 3. Unequal Distribution

- **Endpoint:** `/unequal`
- **Method:** `POST`
- **Description:** Creates an expense with specified amounts for each user, ensuring the total matches the specified amount.

#### Request Body:

```json
{
  "user_list": [
    { "user_id": 1, "amount": 30.0 },
    { "user_id": 2, "amount": 70.0 }
  ],
  "total_amount": 100.0,
  "description": "Team Lunch"
}
```

#### Response:

- **Success (201 Created):**
  ```json
  {
    "status": "success",
    "message": "Expense successfully added with custom splits.",
    "expense_id": 2,
    "description": "Team Lunch",
    "total_amount": 100.0,
    "participants": [
      {
        "user_id": 1,
        "user_name": "Bob",
        "amount_paid": 0.0,
        "amount_owed": 30.0
      }
    ]
  }
  ```
- **Error (400 Bad Request):**
  ```json
  {
    "status": "error",
    "message": "Split does not sum up to the total amount. Please check.",
    "status_code": 400
  }
  ```

### 4. Percentage Distribution

- **Endpoint:** `/percentage`
- **Method:** `POST`
- **Description:** Creates an expense with specified percentage splits for each user, validating that the total percentages sum to 100.

#### Request Body:

```json
{
  "user_list": [
    { "user_id": 1, "percentage": 40 },
    { "user_id": 2, "percentage": 60 }
  ],
  "total_amount": 100.0,
  "description": "Project Dinner"
}
```

#### Response:

- **Success (201 Created):**
  ```json
  {
    "status": "success",
    "message": "Expense successfully added with percentage-based splits.",
    "expense_id": 3,
    "description": "Project Dinner",
    "total_amount": 100.0,
    "participants": [
      {
        "user_id": 1,
        "user_name": "Charlie",
        "percentage": 40,
        "amount_paid": 0.0,
        "amount_owed": 40.0
      }
    ]
  }
  ```
- **Error (400 Bad Request):**
  ```json
  {
    "status": "error",
    "message": "Total percentages must add up to 100.",
    "status_code":
  ```
