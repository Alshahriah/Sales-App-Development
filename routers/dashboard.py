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
    # Create base query excluding returned and cancelled orders
    active_sales = db.query(Sale).filter(~Sale.delivery_status.in_(["Returned", "Cancelled"]))

    # Total Sales and Profit Calculations
    total_sales = active_sales.with_entities(func.sum(Sale.sale_price)).scalar() or 0
    total_buy_price = active_sales.with_entities(func.sum(Sale.buy_price)).scalar() or 0
    total_amazon_commission = active_sales.with_entities(func.sum(Sale.sale_price * Sale.amazon_commission / 100)).scalar() or 0
    total_profit = total_sales - (total_buy_price + total_amazon_commission)
    total_orders = active_sales.count()
    average_sales = round(total_sales / total_orders if total_orders > 0 else 0, 2)

    # Order Summaries
    received_orders = db.query(Sale).filter(Sale.delivery_status == "Received").count()
    returned_orders = db.query(Sale).filter(Sale.delivery_status == "Returned").count()
    delivered_orders = db.query(Sale).filter(Sale.delivery_status == "Delivered").count()  # Change from "Pending" to "Delivered"
    shipped_orders = db.query(Sale).filter(Sale.delivery_status == "Shipped").count()
    cancelled_orders_count = db.query(Sale).filter(Sale.delivery_status == "Cancelled").count()

    # Sales by Region and Supplier (excluding returned and cancelled)
    sales_by_region = (
        db.query(Region.region_name, func.sum(Sale.sale_price))
        .join(Sale)
        .filter(~Sale.delivery_status.in_(["Returned", "Cancelled"]))
        .group_by(Region.id)
        .all()
    )
    
    sales_by_supplier = (
        db.query(Sale.supplier_name, func.count(Sale.id).label('order_count'))
        .filter(~Sale.delivery_status.in_(["Returned", "Cancelled"]))
        .group_by(Sale.supplier_name)
        .all()
    )

    # Sales values over months (excluding returned and cancelled)
    sales_value = (
        db.query(func.strftime('%Y-%m', Sale.sale_date), func.sum(Sale.sale_price))
        .filter(~Sale.delivery_status.in_(["Returned", "Cancelled"]))
        .group_by(func.strftime('%Y-%m', Sale.sale_date))
        .all()
    )
    
    performance_orders = (
        db.query(func.strftime('%Y-%m', Sale.sale_date), func.count(Sale.id))
        .filter(~Sale.delivery_status.in_(["Returned", "Cancelled"]))
        .group_by(func.strftime('%Y-%m', Sale.sale_date))
        .all()
    )

    # Calculate Top Products (excluding returned and cancelled)
    top_products = (
        db.query(
            Sale.product_name,
            func.sum(Sale.sale_price).label('total_sales'),
            func.count(Sale.id).label('units_sold')
        )
        .filter(~Sale.delivery_status.in_(["Returned", "Cancelled"]))
        .group_by(Sale.product_name)
        .order_by(func.sum(Sale.sale_price).desc())
        .limit(5)
        .all()
    )

    context = {
        "request": request,
        "total_sales": total_sales,
        "average_sales": average_sales,
        "total_profit": total_profit,
        "total_buy_price": total_buy_price,
        "total_amazon_commission": total_amazon_commission,
        "received_orders": received_orders,
        "returned_orders": returned_orders,
        "delivered_orders": delivered_orders,  # Change from "Pending" to "Delivered"
        "shipped_orders": shipped_orders,
        "cancelled_orders_count": cancelled_orders_count,
        "sales_by_region": sales_by_region,
        "sales_by_supplier": sales_by_supplier,
        "sales_value": sales_value,
        "performance_orders": performance_orders,
        "top_products": top_products
    }

    return templates.TemplateResponse("dashboard.html", context)
