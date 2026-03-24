from sqlalchemy import text
from rocca_app import create_app, db

app = create_app()
with app.app_context():
    with db.engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE orders MODIFY COLUMN payment_id VARCHAR(100);"))
            print("payment_id modified")
        except Exception as e:
            print("payment_id error:", e)
        
        try:
            conn.execute(text("ALTER TABLE orders ADD COLUMN payment_method VARCHAR(50) DEFAULT NULL;"))
            print("payment_method added")
        except Exception as e:
            print("payment_method error:", e)
            
        try:
            conn.execute(text("ALTER TABLE orders ADD COLUMN installments INT DEFAULT 1;"))
            print("installments added")
        except Exception as e:
            print("installments error:", e)
