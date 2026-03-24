from sqlalchemy import text
from rocca_app import create_app, db

def alter_db():
    app = create_app()
    with app.app_context():
        with db.engine.begin() as conn:
            try:
                # Alter table Carts
                try:
                    conn.execute(text("ALTER TABLE carts ADD COLUMN coupon_id INTEGER REFERENCES coupons(id);"))
                    print("Added coupon_id columns to carts")
                except Exception as e:
                    print("carts coupon_id error:", e)
                    
                try:
                    conn.execute(text("ALTER TABLE carts ADD COLUMN discount_amount NUMERIC(10, 2) DEFAULT 0.00;"))
                    print("Added discount_amount columns to carts")
                except Exception as e:
                    print("carts discount_amount error:", e)
                    
                # Alter table Orders
                try:
                    conn.execute(text("ALTER TABLE orders ADD COLUMN coupon_id INTEGER REFERENCES coupons(id);"))
                    print("Added coupon_id columns to orders")
                except Exception as e:
                    print("orders coupon_id error:", e)
                    
                try:
                    conn.execute(text("ALTER TABLE orders ADD COLUMN discount_amount NUMERIC(10, 2) DEFAULT 0.00;"))
                    print("Added discount_amount columns to orders")
                except Exception as e:
                    print("orders discount_amount error:", e)

            except Exception as e:
                print(f"Erro principal: {e}")

if __name__ == "__main__":
    alter_db()
