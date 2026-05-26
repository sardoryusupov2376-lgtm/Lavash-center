import json
import os
from config import MENU_FILE, ORDERS_FILE, USERS_FILE

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── MENU ──────────────────────────────────────────
def get_menu():
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_categories():
    return get_menu()["categories"]

def get_items_by_category(cat_id):
    return [i for i in get_menu()["items"] if i["category"] == cat_id]

def get_item_by_id(item_id):
    for item in get_menu()["items"]:
        if item["id"] == item_id:
            return item
    return None

def add_menu_item(item):
    menu = get_menu()
    new_id = max((i["id"] for i in menu["items"]), default=0) + 1
    item["id"] = new_id
    menu["items"].append(item)
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2)

def delete_menu_item(item_id):
    menu = get_menu()
    menu["items"] = [i for i in menu["items"] if i["id"] != item_id]
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2)

# ── ORDERS ────────────────────────────────────────
def get_orders():
    return load_json(ORDERS_FILE)

def save_order(order):
    orders = get_orders()
    new_id = max((o["id"] for o in orders), default=0) + 1
    order["id"] = new_id
    orders.append(order)
    save_json(ORDERS_FILE, orders)
    return new_id

def update_order_status(order_id, status):
    orders = get_orders()
    for o in orders:
        if o["id"] == order_id:
            o["status"] = status
            break
    save_json(ORDERS_FILE, orders)

def get_user_orders(user_id):
    return [o for o in get_orders() if o["user_id"] == user_id]

# ── USERS ─────────────────────────────────────────
def get_users():
    return load_json(USERS_FILE)

def register_user(user):
    users = get_users()
    ids = [u["id"] for u in users]
    if user["id"] not in ids:
        users.append(user)
        save_json(USERS_FILE, users)
