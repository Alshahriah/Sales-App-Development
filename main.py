from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from database import SessionLocal, engine, Base
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Table, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(middleware=[Middleware(SessionMiddleware, secret_key="secret")])

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

Base.metadata.create_all(bind=engine)

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    product_description = Column(String, nullable=True)
    supplier_name = Column(String, index=True)
    sale_price = Column(Float)
    amazon_commission = Column(Float)
    quantity = Column(Integer)
    buy_price = Column(Float)
    estimated_delivery = Column(Date)
    sale_date = Column(Date)
    buyer_name = Column(String, index=True)
    buyer_address = Column(String, nullable=True)
    delivery_status = Column(String, nullable=True)
    manage_link = Column(String, nullable=True)
    amazon_link = Column(String, nullable=True)
    payment_link = Column(String, nullable=True)
    region_id = Column(Integer, ForeignKey('regions.id'))
    forex_fees = Column(Float, nullable=True)
    
    # Define relationship with Region
    region = relationship("Region", back_populates="sales")

class Region(Base):
    __tablename__ = 'regions'
    
    id = Column(Integer, primary_key=True, index=True)
    region_name = Column(String, unique=True, nullable=False)
    region_code = Column(String, unique=True, nullable=False)

    # Define relationship with Sale
    sales = relationship("Sale", back_populates="region")

class CRUDLog(Base):
    __tablename__ = "crud_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)  # e.g., CREATE, READ, UPDATE, DELETE
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = Column(String, nullable=True)
    record_id = Column(Integer)
    model = Column(String)  # The model affected, e.g., Sale
    details = Column(String, nullable=True)  # Optional field to store additional details

class UpdateStatusRequest(BaseModel):
    delivery_status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_crud_action(action: str, model: str, record_id: int, db: Session, user: str = None, details: str = None):
    log_entry = CRUDLog(action=action, model=model, record_id=record_id, user=user, details=details)
    db.add(log_entry)
    db.commit()

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    sales = db.query(Sale).order_by(desc(Sale.id)).all()
    total_sales = round(sum(sale.sale_price for sale in sales), 2)
    average_sales = round(total_sales / len(sales), 2) if sales else 0.00
    total_profit = round(sum((sale.sale_price - sale.buy_price) * sale.quantity for sale in sales), 2)
    shk_payment = round(total_profit * 0.50, 2)
    frn_payment = round(total_profit * 0.25, 2)
    ai_payment = round(total_profit * 0.25, 2)

    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "sales": sales,
            "total_sales": total_sales,
            "average_sales": average_sales,
            "total_profit": total_profit,
            "shk_payment": shk_payment,
            "frn_payment": frn_payment,
            "ai_payment": ai_payment
        }
    )

@app.get("/create_sale", response_class=HTMLResponse)
async def create_sale_form(request: Request, db: Session = Depends(get_db)):
    regions = db.query(Region).all()  # Fetch all regions from the database
    return templates.TemplateResponse("create_sale.html", {"request": request, "regions": regions})

@app.post("/create_sale", response_class=HTMLResponse)
async def create_sale(
    request: Request,
    product_name: str = Form(...),
    product_description: str = Form(None),
    supplier_name: str = Form(...),
    sale_price: str = Form(...),
    amazon_commission: str = Form(...),
    quantity: int = Form(...),
    buy_price: str = Form(...),
    estimated_delivery: str = Form(...),
    sale_date: str = Form(...),
    buyer_name: str = Form(...),
    buyer_address: str = Form(None),
    delivery_status: str = Form(None),
    manage_link: str = Form(None),
    payment_link: str = Form(None),
    amazon_link: str = Form(None),  # Added amazon_link field
    forex_fees: str = Form(...),
    region_id: int = Form(...),  # Existing field for region
    db: Session = Depends(get_db)
):
    new_sale = Sale(
        product_name=product_name,
        product_description=product_description,
        supplier_name=supplier_name,
        sale_price=float(sale_price),
        amazon_commission=float(amazon_commission),
        quantity=quantity,
        buy_price=float(buy_price),
        estimated_delivery=date.fromisoformat(estimated_delivery),
        sale_date=date.fromisoformat(sale_date),
        buyer_name=buyer_name,
        buyer_address=buyer_address,
        delivery_status=delivery_status,
        manage_link=manage_link,
        payment_link=payment_link,
        forex_fees=float(forex_fees),
        region_id=region_id,  # Existing field for region
        amazon_link=amazon_link  # Added amazon_link field
    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    log_crud_action(
        action="CREATE",
        model="Sale",
        record_id=new_sale.id,
        db=db,
        details=f"Created sale for product '{product_name}' from order <a href='/orderdetails/{new_sale.id}'>{buyer_name}</a>"
    )
    return RedirectResponse("/", status_code=303)


@app.get("/edit/{sale_id}", response_class=HTMLResponse)
async def edit_sale_form(sale_id: int, request: Request, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    regions = db.query(Region).all()  # Fetch all regions from the database
    return templates.TemplateResponse("edit_sale.html", {"request": request, "sale": sale, "regions": regions})

@app.post("/edit/{sale_id}", response_class=HTMLResponse)
async def edit_sale(
    sale_id: int, request: Request, db: Session = Depends(get_db),
    product_name: str = Form(...),
    product_description: str = Form(None),
    supplier_name: str = Form(...),
    sale_price: str = Form(...),
    amazon_commission: str = Form(...),
    quantity: int = Form(...),
    buy_price: str = Form(...),
    estimated_delivery: str = Form(...),
    sale_date: str = Form(...),
    buyer_name: str = Form(...),
    buyer_address: str = Form(None),
    delivery_status: str = Form(None),
    manage_link: str = Form(None),
    payment_link: str = Form(None),
    amazon_link: str = Form(None),  # Added amazon_link field
    forex_fees: str = Form(...),
    region_id: int = Form(...),  # Existing field for region
    referrer: str = Form(None)
):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    sale.product_name = product_name
    sale.product_description = product_description if product_description else sale.product_description
    sale.supplier_name = supplier_name
    sale.sale_price = float(sale_price)
    sale.amazon_commission = float(amazon_commission) if amazon_commission else sale.amazon_commission
    sale.quantity = quantity
    sale.buy_price = float(buy_price)
    sale.estimated_delivery = date.fromisoformat(estimated_delivery)
    sale.sale_date = date.fromisoformat(sale_date)
    sale.buyer_name = buyer_name
    sale.buyer_address = buyer_address if buyer_address else sale.buyer_address
    sale.delivery_status = delivery_status if delivery_status else sale.delivery_status
    sale.manage_link = manage_link if manage_link else sale.manage_link
    sale.payment_link = payment_link if payment_link else sale.payment_link
    sale.forex_fees = float(forex_fees)
    sale.amazon_link = amazon_link if amazon_link else sale.amazon_link  # Update amazon_link
    sale.region_id = region_id  # Update region_id
    db.commit()
    log_crud_action(
        action="UPDATE",
        model="Sale",
        record_id=sale.id,
        db=db,
        details=f"Updated sale <a href='/orderdetails/{sale.id}'>{buyer_name}</a> for product '{product_name}'"
    )
    return RedirectResponse(referrer or "/admin", status_code=303)


@app.post("/delete/{sale_id}", response_class=HTMLResponse)
async def delete_sale(sale_id: int, request: Request, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    db.delete(sale)
    db.commit()
    log_crud_action(
        action="DELETE",
        model="Sale",
        record_id=sale.id,
        db=db,
        details=f"Deleted sale <a href='/orderdetails/{sale.id}'>{sale.buyer_name}</a> for product '{sale.product_name}'"
    )
    return RedirectResponse("/admin", status_code=303)

@app.post("/update_status/{sale_id}", response_class=JSONResponse)
async def update_status(sale_id: int, request: UpdateStatusRequest, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    sale.delivery_status = request.delivery_status
    db.commit()
    log_crud_action(
        action="UPDATE",
        model="Sale",
        record_id=sale.id,
        db=db,
        details=f"Updated delivery status for sale <a href='/orderdetails/{sale.id}'>{sale.buyer_name}</a> to '{request.delivery_status}'"
    )
    return JSONResponse(content={"message": "Status updated successfully"})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, password: str = Form(...)):
    if password == "yolobunda":  # Set your password here
        response = RedirectResponse("/success_redirect", status_code=303)
        response.set_cookie(key="authenticated", value="true")
        return response
    return RedirectResponse("/login?error=incorrect_password", status_code=303)

@app.get("/success_redirect", response_class=HTMLResponse)
async def success_redirect(request: Request):
    return templates.TemplateResponse("success_redirect.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db), page: int = 1, per_page: int = 10):
    if request.cookies.get("authenticated") != "true":
        return RedirectResponse("/login")
    total_sales = db.query(Sale).count()
    sales = db.query(Sale).order_by(desc(Sale.id)).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total_sales + per_page - 1) // per_page
    return templates.TemplateResponse("admin.html", {"request": request, "sales": sales, "page": page, "total_pages": total_pages, "per_page": per_page})

@app.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request, db: Session = Depends(get_db)):
    logs = db.query(CRUDLog).order_by(desc(CRUDLog.timestamp)).all()
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs})

@app.get("/orderdetails/{id}", response_class=HTMLResponse)
async def order_details(id: int, request: Request, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return templates.TemplateResponse("order_details.html", {"request": request, "sale": sale})

@app.get("/admin/addregion", response_class=HTMLResponse)
async def add_region_form(request: Request):
    return templates.TemplateResponse("add_region.html", {"request": request})

@app.post("/admin/addregion", response_class=HTMLResponse)
async def add_region(region_name: str = Form(...), region_code: str = Form(...), db: Session = Depends(get_db)):
    if db.query(Region).filter((Region.region_name == region_name) | (Region.region_code == region_code)).first():
        raise HTTPException(status_code=400, detail="Region name or code already exists")
    new_region = Region(region_name=region_name, region_code=region_code)
    db.add(new_region)
    db.commit()
    return RedirectResponse("/admin/countries", status_code=303)

@app.get("/admin/orders_by_region/{region_id}", response_class=HTMLResponse)
async def orders_by_region(region_id: int, request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("authenticated") != "true":
        return RedirectResponse("/login")
    
    sales = db.query(Sale).filter(Sale.region_id == region_id).order_by(desc(Sale.id)).all()
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    return templates.TemplateResponse("orders_by_region.html", {"request": request, "sales": sales, "region": region})


@app.get("/admin/countries", response_class=HTMLResponse)
async def list_regions(request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("authenticated") != "true":
        return RedirectResponse("/login")
    
    regions = db.query(Region).all()

    # Calculate total orders per region
    region_orders = []
    total_orders = 0
    for region in regions:
        orders_count = db.query(Sale).filter(Sale.region_id == region.id).count()
        region_orders.append({"region_id": region.id, "region_name": region.region_name, "region_code": region.region_code, "orders_count": orders_count})
        total_orders += orders_count
    
    return templates.TemplateResponse("countries.html", {"request": request, "regions": region_orders, "total_orders": total_orders})

@app.get("/admin/view_orders", response_class=HTMLResponse)
async def view_orders(
    request: Request,
    db: Session = Depends(get_db),
    period: Optional[str] = Query(None, description="Filter period: 'days', 'months', 'years'"),
    value: int = Query(1, description="Value for the period filter"),
    delivery_status: Optional[str] = Query(None, description="Delivery status filter"),
    ship_by: Optional[str] = Query(None, description="Ship by date filter"),
    delivery_by: Optional[str] = Query(None, description="Delivery by date filter"),
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Number of orders per page"),
    search: Optional[str] = Query(None, description="Search term")
):
    if request.cookies.get("authenticated") != "true":
        return RedirectResponse("/login")

    now = datetime.now()
    
    if period == "days":
        filter_date = now - timedelta(days=value)
    elif period == "months":
        filter_date = now - timedelta(days=value * 30)
    elif period == "years":
        filter_date = now - timedelta(days=value * 365)
    else:
        filter_date = now - timedelta(days=365)

    query = db.query(Sale).filter(Sale.sale_date >= filter_date)
    
    if delivery_status:
        query = query.filter(Sale.delivery_status == delivery_status)

    if ship_by:
        query = query.filter(Sale.estimated_delivery <= ship_by)

    if delivery_by:
        query = query.filter(Sale.estimated_delivery <= delivery_by)

    if search:
        query = query.filter(Sale.product_name.ilike(f"%{search}%") | Sale.buyer_name.ilike(f"%{search}%"))

    total_orders = query.count()
    sales = query.order_by(desc(Sale.sale_date)).offset((page - 1) * page_size).limit(page_size).all()

    return templates.TemplateResponse("view_orders.html", {
        "request": request,
        "sales": sales,
        "period": period,
        "value": value,
        "delivery_status": delivery_status,
        "ship_by": ship_by,
        "delivery_by": delivery_by,
        "page": page,
        "page_size": page_size,
        "total_orders": total_orders,
        "search": search
    })

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Total Sales and Profit Calculations
    total_sales = db.query(func.sum(Sale.sale_price)).scalar()
    total_buy_price = db.query(func.sum(Sale.buy_price)).scalar()
    total_amazon_commission = db.query(func.sum(Sale.sale_price * Sale.amazon_commission / 100)).scalar()
    total_profit = total_sales - (total_buy_price + total_amazon_commission)
    total_orders = db.query(Sale).count()
    average_sales = round(total_sales / total_orders if total_orders > 0 else 0, 2)

    # Order Summaries
    received_orders = db.query(Sale).filter(Sale.delivery_status == "Received").count()
    returned_orders = db.query(Sale).filter(Sale.delivery_status == "Returned").count()
    pending_orders = db.query(Sale).filter(Sale.delivery_status == "Pending").count()
    shipped_orders = db.query(Sale).filter(Sale.delivery_status == "Shipped").count()
    cancelled_orders_count = db.query(Sale).filter(Sale.delivery_status == "Cancelled").count()

    # Sales by Region and Supplier
    sales_by_region = db.query(Region.region_name, func.sum(Sale.sale_price)).join(Sale).group_by(Region.id).all()
    sales_by_supplier = db.query(Sale.supplier_name, func.count(Sale.id).label('order_count')).group_by(Sale.supplier_name).all()

    # Actual data for sales values over months
    sales_value = db.query(func.strftime('%Y-%m', Sale.sale_date), func.sum(Sale.sale_price)).group_by(func.strftime('%Y-%m', Sale.sale_date)).all()
    performance_orders = db.query(func.strftime('%Y-%m', Sale.sale_date), func.count(Sale.id)).group_by(func.strftime('%Y-%m', Sale.sale_date)).all()

    # Calculate Top Products
    top_products = db.query(Sale.product_name,func.sum(Sale.sale_price).label('total_sales'),func.count(Sale.id).label('units_sold')).group_by(Sale.product_name).order_by(func.sum(Sale.sale_price).desc()).limit(5).all()

    context = {
        "request": request,
        "total_sales": total_sales,
        "average_sales": average_sales,
        "total_profit": total_profit,
        "total_buy_price": total_buy_price,  # Add this line
        "total_amazon_commission": total_amazon_commission,  # Add this line
        "received_orders": received_orders,
        "returned_orders": returned_orders,
        "pending_orders": pending_orders,
        "shipped_orders": shipped_orders,
        "cancelled_orders_count": cancelled_orders_count,
        "sales_by_region": sales_by_region,
        "sales_by_supplier": sales_by_supplier,
        "sales_value": sales_value,
        "performance_orders": performance_orders,
        "top_products": top_products
    }

    return templates.TemplateResponse("dashboard.html", context)
