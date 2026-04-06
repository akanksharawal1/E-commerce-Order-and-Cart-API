# 🛒 E-commerce Order and Cart API

A backend REST API that allows users to register, authenticate, browse products, manage carts, and place orders. Built using **Flask**, **MySQL**, and **SQLAlchemy** with secure JWT-based authentication.

---

## 📌 Features

- 🔐 User Registration and Login (JWT Authentication)
- 🛍️ Product Management:
    ---> View products with pagination  
    ---> Add products (Admin only)  

- 🛒 Cart System:
    ---> Add items to cart  
    ---> View cart with total pricing  

- 📦 Order Management:
    ---> Place orders from cart  
    ---> Automatic stock deduction  
    ---> View user-specific orders  
    ---> Delete orders (authorized users only)  

- 🔑 Role-Based Access:
    ---> Admin users can manage products  
    ---> Normal users can manage cart and orders  

- ⚡ Secure API:
    ---> Password hashing  
    ---> Token-based authentication  
    ---> Protected routes  

---

## 🛠️ Tech Stack

- **Backend**: Flask, Python, MySQL, SQLAlchemy  
- **Authentication**: JWT (JSON Web Tokens)  
- **Database Migration**: Flask-Migrate (Alembic)  
- **Environment**: dotenv for secure configuration  

---

## 🚀 Setup Instructions

1. **Clone the repo**

   ```
   git clone https://github.com/akanksharawal1/E-commerce-Order-and-Cart-API.git
   cd E-commerce-Order-and-Cart-API
   ```

2. **Create and Activate Virtual Environment**

   For Windows:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```
   pip install -r requirements.txt
   ```

4. **Create .env File**

   Create a `.env` file in the root directory and add:

   ```
   SECRET_KEY=your_secret_key
   DB_HOST=localhost
   DB_USER=root
   DB_PASS=your_password
   DB_NAME=ecommerce_db
   ```

5. **Run the App**

   ```
   flask run
   ```

---

## 📡 API Endpoints

### Auth
- POST /register  
- POST /login  

### Products
- GET /products?page=1&per_page=10  
- POST /products (Admin only)  

### Cart
- POST /cart  
- GET /cart  

### Orders
- POST /orders  
- GET /orders  
- DELETE /orders/<id>  

---

## 🎯 Project Highlights

- Designed RESTful APIs with proper authentication and authorization.  
- Implemented cart-to-order workflow with real-time stock handling.  
- Structured scalable backend using Flask and SQLAlchemy.  
- Tested endpoints using Postman for reliable API behavior.  
