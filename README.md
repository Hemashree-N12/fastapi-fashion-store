# fastapi-fashion-store
# 🛍️ TrendZone Fashion Store API

##  Project Overview
This project is a FastAPI-based backend for a fashion store where users can browse products, place orders, manage wishlists, and explore advanced features like filtering, sorting, and pagination.

---

##  Features

###  Basic APIs
- Home route
- Get all products
- Get product by ID
- Orders summary

###  Data Validation
- Implemented using Pydantic
- Field constraints like min length, max values, etc.

### CRUD Operations
- Add new product
- Update product details
- Delete product (with validation)

###  Multi-Step Workflow
- Wishlist → Order system
- Add items to wishlist
- Order all wishlist items at once

###  Advanced APIs
- Search products by keyword
- Sort products (price, name, brand, category)
- Pagination for products and orders
- Combined browsing endpoint

### Additional Feature
- Customer order summary endpoint to analyze total spending and average order value

---

## Tech Stack
- Python
- FastAPI
- Pydantic
- Uvicorn
- Browser
- Terminal
  
---
## How to Run
```in command prompt or terminal
pip install -r requirements.txt
uvicorn main:app --reload
