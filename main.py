from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

# ══════════════ Q6 MODELS ══════════════════════════════════════════
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0, le=10)
    delivery_address: str = Field(..., min_length=10)
    gift_wrap: bool = False
    season_sale: bool = False

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    sizes_available: list[str]
    in_stock: bool = True

class WishlistOrder(BaseModel):
    customer_name: str
    delivery_address: str


# ══════════════ Q2 DATA ════════════════════════════════════════════
products = [
    {'id': 1, 'name': 'Denim Shirt', 'brand': 'H&M', 'category': 'Shirt', 'price': 1200, 'sizes_available': ['S','M','L'], 'in_stock': True},
    {'id': 2, 'name': 'Wide-Leg Jeans', 'brand': 'Westside', 'category': 'Jeans', 'price': 2000, 'sizes_available': ['M','L'], 'in_stock': True},
    {'id': 3, 'name': 'Sneakers', 'brand': 'Adidas', 'category': 'Shoes', 'price': 3000, 'sizes_available': ['M','L'], 'in_stock': False},
    {'id': 4, 'name': 'Sun Dress', 'brand': 'Mango', 'category': 'Dress', 'price': 1800, 'sizes_available': ['S','M'], 'in_stock': True},
    {'id': 5, 'name': 'Leather Jacket', 'brand': 'Zara', 'category': 'Jacket', 'price': 5000, 'sizes_available': ['L'], 'in_stock': True},
    {'id': 6, 'name': 'Formal Shirt', 'brand': 'Peter England', 'category': 'Shirt', 'price': 2500, 'sizes_available': ['S','M','L'], 'in_stock': False},
]

orders = []
wishlist = []
order_counter = 1


# ══════════════ Q7 HELPERS ══════════════════════════════════════════
def get_product_by_id(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None

def calculate_order_total(price, quantity, gift_wrap, season_sale):
    base = price * quantity

    season_discount = base * 0.15 if season_sale else 0
    bulk_discount = base * 0.05 if quantity >= 5 else 0

    gift_charge = 50 * quantity if gift_wrap else 0

    total = base - season_discount - bulk_discount + gift_charge

    return {
        "base_price": base,
        "season_discount": season_discount,
        "bulk_discount": bulk_discount,
        "gift_wrap_charge": gift_charge,
        "final_total": total
    }

def apply_filters(data, category=None, brand=None, max_price=None, in_stock=None):
    result = data
    if category is not None:
        result = [p for p in result if p['category'] == category]
    if brand is not None:
        result = [p for p in result if p['brand'] == brand]
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return result

# ══════════ Q1 HOME ════════════════════════════════════════════
@app.get('/')
def home():
    return {'message': 'Welcome to TrendZone Fashion Store'}

# ════════ Q2 GET ALL PRODUCTS ════════════════════════════════════════════════
@app.get('/products')
def get_products():
    return {
        "products": products,
        "total": len(products),
        "in_stock_count": sum(p['in_stock'] for p in products)
    }

# ══════════ Q5 SUMMARY ══════════════════════════════════════════════
@app.get('/products/summary')
def summary():
    brands = list(set(p['brand'] for p in products))
    category_count = {}

    for p in products:
        category_count[p['category']] = category_count.get(p['category'], 0) + 1

    return {
        "total": len(products),
        "in_stock": sum(p['in_stock'] for p in products),
        "out_of_stock": sum(not p['in_stock'] for p in products),
        "brands": brands,
        "category_count": category_count
    }

# ══════════ Q4 GET ORDERS ══════════════════════════════════════════════
@app.get('/orders')
def get_orders():
    total_revenue = sum(o['total_price'] for o in orders)
    return {
        "orders": orders,
        "total": len(orders),
        "total_revenue": total_revenue
    }


# ═════════ Q8 & Q9 POST ORDER ═══════════════════════════════════════════════
@app.post('/orders')
def place_order(data: OrderRequest):
    global order_counter
    product = get_product_by_id(data.product_id)
    if not product:
        return {"error": "Product not found"}
    if not product['in_stock']:
        return {"error": "Out of stock"}
    if data.size not in product['sizes_available']:
        return {"error": f"Available sizes: {product['sizes_available']}"}
    bill = calculate_order_total(product['price'], data.quantity, data.gift_wrap, data.season_sale)
    order = {
        "order_id": order_counter,
        "customer_name": data.customer_name,
        "product": product['name'],
        "brand": product['brand'],
        "size": data.size,
        "quantity": data.quantity,
        "total_price": bill["final_total"]
    }
    orders.append(order)
    order_counter += 1
    return {
        "message": "Order successful",
        "order_details": order,
        "pricing": bill
    }

# ════════ Q10 FILTER ════════════════════════════════════════════════
@app.get('/products/filter')
def filter_products(category: str = None, brand: str = None, max_price: int = None, in_stock: bool = None):
    result = apply_filters(products, category, brand, max_price, in_stock)
    return {"results": result}

# ═════════ Q11 CREATE PRODUCT ═══════════════════════════════════════════════
@app.post('/products')
def add_product(p: NewProduct, response: Response):
    if any(prod['name'] == p.name and prod['brand'] == p.brand for prod in products):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Product exists"}
    new_product = p.dict()
    new_product['id'] = max(prod['id'] for prod in products) + 1
    products.append(new_product)
    response.status_code = status.HTTP_201_CREATED
    return new_product

# ═══════ Q12 UPDATE ═════════════════════════════════════════════════
@app.put('/products/{product_id}')
def update_product(product_id: int, response: Response, price: int = None, in_stock: bool = None):
    product = get_product_by_id(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Not found"}
    if price is not None:
        product['price'] = price
    if in_stock is not None:
        product['in_stock'] = in_stock
    return product

# ═════════  Q13 DELETE ═══════════════════════════════════════════════
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = get_product_by_id(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Not found"}

    if any(o['product'] == product['name'] for o in orders):
        return {"error": "Cannot delete product with orders"}

    products.remove(product)
    return {"message": "Deleted"}

# ════════════ Q14 WISHLIST ADD + VIEW ════════════════════════════════════════════
@app.post('/wishlist/add')
def add_to_wishlist(customer_name: str, product_id: int, size: str):
    product = get_product_by_id(product_id)

    if not product:
        return {"error": "Product not found"}

    if size not in product['sizes_available']:
        return {"error": "Invalid size"}

    item = {"customer": customer_name, "product_id": product_id, "size": size}

    if item in wishlist:
        return {"error": "Already added"}

    wishlist.append(item)
    return {"message": "Added to wishlist"}

@app.get('/wishlist')
def view_wishlist():
    total = sum(get_product_by_id(i['product_id'])['price'] for i in wishlist)
    return {"wishlist": wishlist, "total_value": total}

# ═════════ Q15 REMOVE + ORDER ALL ═══════════════════════════════════════════════
@app.delete('/wishlist/remove')
def remove_wishlist(customer_name: str, product_id: int):
    for item in wishlist:
        if item['customer'] == customer_name and item['product_id'] == product_id:
            wishlist.remove(item)
            return {"message": "Removed"}
    return {"error": "Not found"}

@app.post('/wishlist/order-all')
def order_all(data: WishlistOrder, response: Response):
    global order_counter
    customer_items = [i for i in wishlist if i['customer'] == data.customer_name]
    if not customer_items:
        return {"error": "No items"}
    placed = []
    total = 0
    for item in customer_items:
        product = get_product_by_id(item['product_id'])
        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "product": product['name'],
            "quantity": 1,
            "total_price": product['price']
        }
        orders.append(order)
        placed.append(order)
        total += product['price']
        order_counter += 1
    wishlist[:] = [i for i in wishlist if i['customer'] != data.customer_name]
    response.status_code = status.HTTP_201_CREATED
    return {"orders": placed, "grand_total": total}

# ═════ Q16 SEARCH═══════════════════════════════════════════════════
@app.get('/products/search')
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p['name'].lower()
              or keyword.lower() in p['brand'].lower()
              or keyword.lower() in p['category'].lower()]
    if not result:
        return {"message": "No products found"}
    return {"results": result, "total_found": len(result)}

# ═════  Q17 SORT ═══════════════════════════════════════════════════
@app.get('/products/sort')
def sort_products(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ['price', 'name', 'brand', 'category']:
        return {"error": "Invalid sort field"}
    if order not in ['asc', 'desc']:
        return {"error": "Invalid order"}
    sorted_data = sorted(products, key=lambda x: x[sort_by], reverse=(order == 'desc'))
    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_data
    }

# ══════════ Q18 PAGINATION ══════════════════════════════════════════════
@app.get('/products/page')
def paginate(page: int = Query(1, ge=1), limit: int = Query(3, ge=1)):
    start = (page - 1) * limit
    return {
        "page": page,
        "total_pages": -(-len(products)//limit),
        "data": products[start:start+limit]
    }

# ════════  Q19 ORDERS SEARCH + SORT + PAGE ═══════════════════════════════════════════
@app.get('/orders/search')
def search_orders(customer_name: str):
    return [o for o in orders if customer_name.lower() in o['customer_name'].lower()]

@app.get('/orders/sort')
def sort_orders(sort_by: str = "total_price"):
    if sort_by not in ["total_price", "quantity"]:
        return {"error": "Invalid field"}
    return {
    "sort_by": sort_by,
    "orders": sorted(orders, key=lambda x: x[sort_by])
}

@app.get('/orders/page')
def paginate_orders(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return {
        "page": page,
        "total_pages": -(-len(orders)//limit),
        "orders": orders[start:start+limit]
    }

# ══════════ BONUS ENDPOINT ════════════════════════════════════════════
@app.get('/orders/customer-summary')
def customer_summary(customer_name: str = Query(...)):
    customer_orders = [
        o for o in orders
        if customer_name.lower() in o['customer_name'].lower()
    ]
    if not customer_orders:
        return {"message": f"No orders found for {customer_name}"}
    total_spent = sum(o['total_price'] for o in customer_orders)
    total_orders = len(customer_orders)
    avg_value = total_spent / total_orders
    return {
        "customer_name": customer_name,
        "total_orders": total_orders,
        "total_spent": total_spent,
        "average_order_value": round(avg_value, 2)
    }

# ═══════════ Q20 BROWSE ═════════════════════════════════════════════
@app.get('/products/browse')
def browse(keyword: str = None, category: str = None, brand: str = None,
           in_stock: bool = None, max_price: int = None,
           sort_by: str = "price", order: str = "asc",
           page: int = 1, limit: int = 3):
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p['name'].lower()]
    result = apply_filters(result, category, brand, max_price, in_stock)
    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == 'desc'))
    start = (page - 1) * limit
    return {
        "total": len(result),
        "page": page,
        "data": result[start:start+limit]
    }

# ═════════ Q3 GET PRODUCT BY ID ═══════════════════════════════════════════════
@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        return {'error': 'Product not found'}
    return product