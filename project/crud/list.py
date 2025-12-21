import sqlite3

def table():
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            total_price INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price INTEGER,
            is_purchased INTEGER DEFAULT 0,
            FOREIGN KEY (list_id) REFERENCES lists(id)
    )""")
    db.commit()
    db.close()

def check_list_id(id, user_id):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    c.execute("SELECT EXISTS (SELECT 1 FROM lists WHERE id = ? AND user_id = ?)", (id, user_id))
    result = c.fetchall()[0][0]
    db.close()
    return result

def check_item_id(id, user_id):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    c.execute("""SELECT EXISTS (
        SELECT 1 FROM list_items li 
        JOIN lists l ON li.list_id = l.id 
        WHERE li.id = ? AND l.user_id = ?
    )""", (id, user_id))
    result = c.fetchall()[0][0]
    db.close()
    return result

def create_list(list):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    c.execute("INSERT INTO lists (user_id, name) VALUES (?, ?)", (list['user_id'], list['name']))
    list_id = c.lastrowid
    db.commit()
    db.close()
    return list_id  

def add_item(item):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    c.execute("INSERT INTO list_items (list_id, product_name, quantity, price) VALUES (?,?,?,?)", 
              (item['list_id'], item['product_name'], item['quantity'], item['price']))
    
    c.execute("""SELECT SUM(quantity * price) 
                 FROM list_items 
                 WHERE list_id = ? AND is_purchased = 0""", (item['list_id'],))
    total = c.fetchone()[0] or 0
    c.execute("UPDATE lists SET total_price = ? WHERE id = ?", (total, item['list_id']))
    
    db.commit()
    db.close()

def toggle_purchased(item_id):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    
    c.execute("SELECT is_purchased FROM list_items WHERE id = ?", (item_id,))
    current = c.fetchone()[0]
    new_status = 0 if current else 1
    c.execute("UPDATE list_items SET is_purchased = ? WHERE id = ?", (new_status, item_id))
    

    c.execute("SELECT list_id FROM list_items WHERE id = ?", (item_id,))
    list_id = c.fetchone()[0]
    
    c.execute("""SELECT SUM(quantity * price) 
                 FROM list_items 
                 WHERE list_id = ? AND is_purchased = 0""", (list_id,))
    total = c.fetchone()[0] or 0
    c.execute("UPDATE lists SET total_price = ? WHERE id = ?", (total, list_id))
    
    db.commit()
    db.close()

def delete_item(item_id):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    
    c.execute("SELECT list_id FROM list_items WHERE id = ?", (item_id,))
    list_id = c.fetchone()[0]
    
    c.execute("DELETE FROM list_items WHERE id = ?", (item_id,))
    
    c.execute("""SELECT SUM(quantity * price) 
                 FROM list_items 
                 WHERE list_id = ? AND is_purchased = 0""", (list_id,))
    total = c.fetchone()[0] or 0
    c.execute("UPDATE lists SET total_price = ? WHERE id = ?", (total, list_id))
    
    db.commit()
    db.close()

def delete_list(list_id):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()


    c.execute("DELETE FROM list_items WHERE list_id = ?", (list_id,))

    c.execute("DELETE FROM lists WHERE id = ?", (list_id,))


    db.commit()
    db.close()

def read_lists(user_id):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    c.execute("SELECT * FROM lists WHERE user_id = ?", (user_id,))
    lists_data = c.fetchall()
    lists = []
    for lst in lists_data:
        one_list = {}
        one_list['id'] = lst[0]
        one_list['user_id'] = lst[1]
        one_list['name'] = lst[2]
        one_list['total_price'] = lst[3]
        lists.append(one_list)
    db.close()
    return lists

def read_list(list_id, user_id):
    db = sqlite3.connect("list_bot.db")
    c = db.cursor()
    
    c.execute("SELECT * FROM lists WHERE id = ? AND user_id = ?", (list_id, user_id))
    list_data = c.fetchone()
    
    if not list_data:
        db.close()
        return None
    
    one_list = {}
    one_list['id'] = list_data[0]
    one_list['user_id'] = list_data[1]
    one_list['name'] = list_data[2]
    one_list['total_price'] = list_data[3]
    
    c.execute("SELECT * FROM list_items WHERE list_id = ?", (list_id,))
    items_data = c.fetchall()
    
    items = []
    for item in items_data:
        one_item = {}
        one_item['id'] = item[0]
        one_item['list_id'] = item[1]
        one_item['product_name'] = item[2]
        one_item['quantity'] = item[3]
        one_item['price'] = item[4]
        one_item['is_purchased'] = item[5]
        one_item['total'] = item[3] * item[4]
        items.append(one_item)
    
    one_list['items'] = items
    db.close()
    return one_list