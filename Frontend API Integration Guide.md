# Frontend API Integration Guide

A step\-by\-step guide to connect your frontend to our nutrition management backend\. This doc covers everything you need to build the UI, from local setup to API calls and error handling\.

---

## Table of Contents

1. \[Quick Start: Run Local Backend\]\(\#quick\-start\-run\-local\-backend\)

2. \[Core Setup\]\(\#core\-setup\)

3. \[Authentication\]\(\#authentication\)

4. \[API Endpoints\]\(\#api\-endpoints\)

5. \[Frontend Request Examples\]\(\#frontend\-request\-examples\)

6. \[Error Handling\]\(\#error\-handling\)

7. \[Pagination \&amp; Filtering\]\(\#pagination\-\-filtering\)

8. \[Development Tips\]\(\#development\-tips\)

9. \[Troubleshooting\]\(\#troubleshooting\)

---

## Quick Start: Run Local Backend

First, set up the local backend so your frontend can connect to it during development:

1. Clone the project repo \(if you haven\&\#39;t already\)

2. Install Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Start the backend dev server:

    ```bash
    uvicorn main:app --reload
    ```

4. The backend will run at `http://127\.0\.0\.1:8000`

5. **Interactive API Docs**: Visit `http://127\.0\.0\.1:8000/docs` to see all endpoints, test requests, and check request/response schemas directly in your browser\. This is the fastest way to debug API calls while you build the frontend\.

---

## Core Setup

### Base URL

Use this base URL to build your API requests:

|Environment|Base URL|
|---|---|
|Local Development|`http://127\.0\.0\.1:8000`|
|Production|`https://api\.nutrition\-app\.com`|

### CORS Configuration

The backend is pre\-configured to allow cross\-origin requests from common frontend development ports:

- `http://localhost:3000` \(Create React App default\)

- `http://localhost:5173` \(Vite default\)

- `http://127\.0\.0\.1:3000`

- `http://127\.0\.0\.1:5173`

If you\&\#39;re using a different port for your frontend, just let me know and I\&\#39;ll update the CORS allowlist\.

### Environment Variables

We recommend using environment variables to configure your API base URL, so you can switch between environments without changing code:

- For React: Add `REACT\_APP\_API\_BASE\_URL` to your `\.env` file

- For Vue: Add `VUE\_APP\_API\_BASE\_URL` to your `\.env` file

- For Vite: Add `VITE\_API\_BASE\_URL` to your `\.env` file

Example:

```env
# .env.development (local dev)
VITE_API_BASE_URL=http://127.0.0.1:8000

# .env.production (production deploy)
VITE_API_BASE_URL=https://api.nutrition-app.com
```

---

## Authentication

All endpoints except `/login` require a valid bearer token\. Here\&\#39;s how to handle auth in your frontend:

### 1\. Login to Get Access Token

First, call the public `/login` endpoint with user credentials to get an access token\.

**Login Request Example**:

```javascript
const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  
  // Save token and user info to localStorage for persistence
  localStorage.setItem('authToken', data.access_token);
  localStorage.setItem('currentUser', JSON.stringify(data.user));
  
  return data;
};
```

**Login Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "John Doe",
    "email": "john@example.com",
    "daily_calorie_target": 2000 // User's custom nutrition goal
  }
}
```

### 2\. Auto\-Add Token to All Requests

Use a request interceptor to automatically attach the auth token to every API request, so you don\&\#39;t have to add it manually for every call\.

**Axios Interceptor Example**:

```javascript
// src/api/client.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Automatically add auth token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Automatically handle auth errors
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    // If token is invalid/expired, clear auth data and redirect to login
    if (err.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('currentUser');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default apiClient;
```

With this setup, you can call any protected endpoint without manually adding the token\!

---

## API Endpoints

All endpoints return JSON data\. Below are the core endpoints you\&\#39;ll use for the frontend:

---

### Authentication

|Method|Endpoint|Description|Auth Required?|
|---|---|---|---|
|POST|`/login`|Authenticate user, get access token|❌ No|

---

### User Profile

|Method|Endpoint|Description|Auth Required?|
|---|---|---|---|
|GET|`/me`|Get current logged\-in user\&\#39;s info \(name, email, calorie target\)|✅ Yes|
|PUT|`/me`|Update user\&\#39;s profile or nutrition goals|✅ Yes|

---

### Foods \(Nutrition Data\)

These endpoints let you fetch food nutrition information \(calories, protein, carbs, etc\.\)

|Method|Endpoint|Description|Auth Required?|
|---|---|---|---|
|GET|`/foods`|Get paginated list of foods, with optional search|✅ Yes|
|GET|`/foods/\{food\_id\}`|Get detailed nutrition info for a single food|✅ Yes|

**Query Parameters for ****`/foods`**:

- `page`: Page number \(default: 1\)

- `limit`: Items per page \(default: 20\)

- `search`: Search term to filter foods by name \(e\.g\., `?search=apple` to find apple\-related foods\)

**Food Object Example**:

```json
{
  "id": "f1234567-e89b-12d3-a456-426614174000",
  "name": "Raw Apple",
  "calories": 52, // per 100g
  "protein": 0.3, // grams per 100g
  "carbs": 14, // grams per 100g
  "fat": 0.2, // grams per 100g
  "fiber": 2.4 // grams per 100g
}
```

---

### Diet Records

These endpoints let users manage their daily food intake records\. All records are automatically linked to the current logged\-in user \(no need to send user ID\!\)\.

|Method|Endpoint|Description|Auth Required?|
|---|---|---|---|
|GET|`/diet\-records`|Get user\&\#39;s diet records, filtered by date|✅ Yes|
|POST|`/diet\-records`|Add a new diet record|✅ Yes|
|DELETE|`/diet\-records/\{record\_id\}`|Delete a diet record|✅ Yes|

**Query Parameters for ****`/diet\-records`**:

- `date`: Filter records by date \(ISO format, e\.g\., `?date=2024\-05\-20` to get records for May 20, 2024\)

**Create Diet Record Request Body**:

```json
{
  "food_id": "f1234567-e89b-12d3-a456-426614174000",
  "quantity": 150, // Quantity in grams
  "date": "2024-05-20" // Date of the meal (ISO date string)
}
```

**Diet Record Response Example**:

```json
{
  "id": "r7890123-e89b-12d3-a456-426614174000",
  "food": {
    "id": "f1234567-e89b-12d3-a456-426614174000",
    "name": "Raw Apple"
  },
  "quantity": 150,
  "date": "2024-05-20",
  "calculated_nutrition": {
    "calories": 78, // Auto-calculated: (52 / 100) * 150
    "protein": 0.45,
    "carbs": 21,
    "fat": 0.3
  }
}
```

---

## Frontend Request Examples

With the `apiClient` we set up earlier, you can call endpoints easily:

### 1\. Get Current User

```javascript
// Load user info when the app starts
const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/me');
    return response.data;
  } catch (err) {
    console.error('Failed to load user:', err);
    throw err;
  }
};
```

### 2\. Search Foods

```javascript
// Search for foods with the term "banana"
const searchFoods = async (searchTerm) => {
  const response = await apiClient.get(`/foods?search=${searchTerm}`);
  return response.data; // { data: foods, pagination: ... }
};
```

### 3\. Get Today\&\#39;s Diet Records

```javascript
// Get all diet records for the current day
const getTodaysRecords = async () => {
  const today = new Date().toISOString().split('T')[0]; // Format: YYYY-MM-DD
  const response = await apiClient.get(`/diet-records?date=${today}`);
  return response.data;
};
```

### 4\. Add a New Diet Record

```javascript
// Add a new apple entry to today's records
const addAppleRecord = async () => {
  const today = new Date().toISOString().split('T')[0];
  const response = await apiClient.post('/diet-records', {
    food_id: 'f1234567-e89b-12d3-a456-426614174000',
    quantity: 150,
    date: today
  });
  return response.data;
};
```

---

## Error Handling

All errors follow a consistent format, so you can handle them uniformly in your frontend:

### Error Response Format

```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error"
    }
  ]
}
```

### Common Error Codes \&amp; Frontend Handling

|Status Code|Meaning|What to do in Frontend|
|---|---|---|
|400|Bad Request \(validation error\)|Show the error message to the user, e\.g\., highlight the invalid form field|
|401|Unauthorized|Token is invalid/expired\. The interceptor will automatically redirect to login|
|403|Forbidden|You don\&\#39;t have permission to access this resource\. Show an error message|
|404|Not Found|The resource you requested doesn\&\#39;t exist\. Show a \&\#34;not found\&\#34; page|
|422|Unprocessable Entity|Invalid input data\. Same as 400, show validation errors to the user|
|500|Server Error|Something went wrong on our end\. Show a generic error message, ask the user to try again later|

---

## Pagination \&amp; Filtering

All list endpoints \(`/foods`, `/diet\-records`\) support pagination\. The response includes pagination metadata to help you build pagination UI:

```json
{
  "data": [...items], // The list of items for the current page
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 156,
    "total_pages": 8
  }
}
```

You can use this to:

- Disable the \&\#34;next\&\#34; button when `page === total\_pages`

- Show the total number of items to the user

- Build a page number selector

---

## Development Tips

1. **Use Swagger UI for Debugging**: Visit `http://127\.0\.0\.1:8000/docs` to test API requests directly\. You can even log in there to get a token, then test protected endpoints without writing any frontend code\. This is perfect for checking what data the API returns before you build the UI\.

2. **Mock Data for Development**: If the backend is down, you can use mock data to build the UI\. Just copy the response examples from this doc to mock your API calls\.

3. **Token Persistence**: The token is stored in `localStorage`, so it will persist even if the user closes the browser\. That means users won\&\#39;t have to log in every time they visit the app\.

4. **Frontend Validation**: The backend will validate all input data, but we recommend adding frontend validation too, to give users faster feedback\.

---

## Troubleshooting

- **CORS Error**: If you see a CORS error in the console, that means your frontend port isn\&\#39;t in the backend\&\#39;s allowlist\. Let me know what port you\&\#39;re using, and I\&\#39;ll update it\.

- **401 Error on App Load**: That usually means the token in localStorage is expired or invalid\. The interceptor will automatically redirect you to login, so that\&\#39;s expected\.

- **Can\&\#39;t Find a Food?**: Use the `search` parameter on `/foods` to filter the list\. If the food you want isn\&\#39;t there, just let me know and we can add it to the database\.

- **Slow API Response?**: In development, the backend runs on your local machine, so it should be fast\. If it\&\#39;s slow, check if you\&\#39;re sending too many requests at once\.

---

## Need Help?

If you have any questions about the API, or need a new endpoint added to support your frontend features, just ping me\! I can update the backend quickly to support whatever you need\.