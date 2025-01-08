from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Sale, CRUDLog, UpdateStatusRequest, Region
from pathlib import Path
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/", response_class=HTMLResponse)
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
    top_products = db.query(Sale.product_name, func.sum(Sale.sale_price).label('total_sales'), func.count(Sale.id).label('units_sold')).group_by(Sale.product_name).order_by(func.sum(Sale.sale_price).desc()).limit(5).all()

    context = {
        "request": request,
        "total_sales": total_sales,
        "average_sales": average_sales,
        "total_profit": total_profit,
        "total_buy_price": total_buy_price,
        "total_amazon_commission": total_amazon_commission,
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
