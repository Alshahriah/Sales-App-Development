from fastapi import APIRouter, Request, Depends, HTTPException, Query, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import date, datetime, timedelta
from typing import Optional
from database import get_db
from models import Sale, CRUDLog, UpdateStatusRequest, Region, DeletedSale
from pathlib import Path
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/admin/deleted_orders", response_class=HTMLResponse)
async def deleted_orders(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Number of orders per page")
):
    # if request.cookies.get("authenticated") != "true":
    #     return RedirectResponse("/login")

    query = db.query(DeletedSale)
    total_orders = query.count()
    sales = query.order_by(desc(DeletedSale.sale_date)).offset((page - 1) * page_size).limit(page_size).all()

    return templates.TemplateResponse("deleted_orders.html", {
        "request": request,
        "sales": sales,
        "page": page,
        "page_size": page_size,
        "total_orders": total_orders
    })

@router.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db), page: int = 1, per_page: int = 10):
    # if request.cookies.get("authenticated") != "true":
    #     return RedirectResponse("/login")
    total_sales = db.query(Sale).count()
    sales = db.query(Sale).order_by(desc(Sale.id)).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total_sales + per_page - 1) // per_page
    return templates.TemplateResponse("admin.html", {"request": request, "sales": sales, "page": page, "total_pages": total_pages, "per_page": per_page})

@router.get("/admin/orders_by_region/{region_id}", response_class=HTMLResponse)
async def orders_by_region(region_id: int, request: Request, db: Session = Depends(get_db)):
    # if request.cookies.get("authenticated") != "true":
    #     return RedirectResponse("/login")
    
    sales = db.query(Sale).filter(Sale.region_id == region_id).order_by(desc(Sale.id)).all()
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    return templates.TemplateResponse("orders_by_region.html", {"request": request, "sales": sales, "region": region})

@router.get("/admin/countries", response_class=HTMLResponse)
async def list_regions(request: Request, db: Session = Depends(get_db)):
    # if request.cookies.get("authenticated") != "true":
    #     return RedirectResponse("/login")
    
    regions = db.query(Region).all()

    # Calculate total orders per region
    region_orders = []
    total_orders = 0
    for region in regions:
        orders_count = db.query(Sale).filter(Sale.region_id == region.id).count()
        region_orders.append({"region_id": region.id, "region_name": region.region_name, "region_code": region.region_code, "orders_count": orders_count})
        total_orders += orders_count
    
    return templates.TemplateResponse("countries.html", {"request": request, "regions": region_orders, "total_orders": total_orders})

@router.get("/admin/view_orders", response_class=HTMLResponse)
async def view_orders(
    request: Request,
    db: Session = Depends(get_db),
    period: Optional[str] = Query(None, description="Filter period: 'days', 'months', 'years'"),
    value: int = Query(1, description="Value for the period filter"),
    delivery_status: Optional[str] = Query(None, description="Delivery status filter"),
    ship_by: Optional[str] = Query(None, description="Ship by date filter"),
    delivery_by: Optional[str] = Query(None, description="Delivery by date filter"),
    sale_date_start: Optional[date] = Query(None, description="Start date for sale date filter"),
    sale_date_end: Optional[date] = Query(None, description="End date for sale date filter"),
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Number of orders per page"),
    search: Optional[str] = Query(None, description="Search term")
):
    # if request.cookies.get("authenticated") != "true":
    #     return RedirectResponse("/login")

    query = db.query(Sale)

    # Apply date filters
    now = datetime.now().date()
    if period and value:
        if period == "days":
            filter_date = now - timedelta(days=value)
        elif period == "months":
            filter_date = now - timedelta(days=value * 30)
        elif period == "years":
            filter_date = now - timedelta(days=value * 365)
        else:
            filter_date = now - timedelta(days=365)
        query = query.filter(func.date(Sale.sale_date) >= filter_date)

    if delivery_status:
        query = query.filter(Sale.delivery_status == delivery_status)

    try:
        if ship_by:
            ship_by_date = datetime.strptime(ship_by, '%Y-%m-%d').date()
            query = query.filter(func.date(Sale.estimated_delivery) <= ship_by_date)

        if delivery_by:
            delivery_by_date = datetime.strptime(delivery_by, '%Y-%m-%d').date()
            query = query.filter(func.date(Sale.estimated_delivery) <= delivery_by_date)

        if sale_date_start:
            query = query.filter(func.date(Sale.sale_date) >= sale_date_start)

        if sale_date_end:
            query = query.filter(func.date(Sale.sale_date) <= sale_date_end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if search:
        search = search.strip()
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
        "sale_date_start": sale_date_start,
        "sale_date_end": sale_date_end,
        "page": page,
        "page_size": page_size,
        "total_orders": total_orders,
        "search": search
    })


@router.get("/admin/addregion", response_class=HTMLResponse)
async def add_region_form(request: Request):
    return templates.TemplateResponse("add_region.html", {"request": request})

@router.post("/admin/addregion", response_class=HTMLResponse)
async def add_region(region_name: str = Form(...), region_code: str = Form(...), db: Session = Depends(get_db)):
    if db.query(Region).filter((Region.region_name == region_name) | (Region.region_code == region_code)).first():
        raise HTTPException(status_code=400, detail="Region name or code already exists")
    new_region = Region(region_name=region_name, region_code=region_code)
    db.add(new_region)
    db.commit()
    return RedirectResponse("/admin/countries", status_code=303)

@router.post("/delete/{sale_id}")
async def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if sale:
        deleted_sale = DeletedSale(
            id=sale.id,
            product_name=sale.product_name,
            product_description=sale.product_description,
            supplier_name=sale.supplier_name,
            order_datetime=sale.order_datetime,
            sale_price=sale.sale_price,
            amazon_commission=sale.amazon_commission,
            quantity=sale.quantity,
            buy_price=sale.buy_price,
            estimated_delivery=sale.estimated_delivery,
            sale_date=sale.sale_date,
            buyer_name=sale.buyer_name,
            buyer_address=sale.buyer_address,
            delivery_status=sale.delivery_status,
            manage_link=sale.manage_link,
            amazon_link=sale.amazon_link,
            payment_link=sale.payment_link,
            region_id=sale.region_id,
            forex_fees=sale.forex_fees
        )
        db.add(deleted_sale)
        db.delete(sale)
        db.commit()
    return RedirectResponse("/admin/view_orders", status_code=303)

@router.get("/admin/restore_order/{sale_id}")
async def restore_sale(sale_id: int, db: Session = Depends(get_db)):
    deleted_sale = db.query(DeletedSale).filter(DeletedSale.id == sale_id).first()
    if deleted_sale:
        sale = Sale(
            id=deleted_sale.id,
            product_name=deleted_sale.product_name,
            product_description=deleted_sale.product_description,
            supplier_name=deleted_sale.supplier_name,
            order_datetime=deleted_sale.order_datetime,
            sale_price=deleted_sale.sale_price,
            amazon_commission=deleted_sale.amazon_commission,
            quantity=deleted_sale.quantity,
            buy_price=deleted_sale.buy_price,
            estimated_delivery=deleted_sale.estimated_delivery,
            sale_date=deleted_sale.sale_date,
            buyer_name=deleted_sale.buyer_name,
            buyer_address=deleted_sale.buyer_address,
            delivery_status=deleted_sale.delivery_status,
            manage_link=deleted_sale.manage_link,
            amazon_link=deleted_sale.amazon_link,
            payment_link=deleted_sale.payment_link,
            region_id=deleted_sale.region_id,
            forex_fees=deleted_sale.forex_fees
        )
        db.add(sale)
        db.delete(deleted_sale)
        db.commit()
    return RedirectResponse("/admin/deleted_orders", status_code=303)

@router.post("/delete/{sale_id}")
async def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if sale:
        deleted_sale = DeletedSale(
            id=sale.id,
            product_name=sale.product_name,
            product_description=sale.product_description,
            supplier_name=sale.supplier_name,
            order_datetime=sale.order_datetime,
            sale_price=sale.sale_price,
            amazon_commission=sale.amazon_commission,
            quantity=sale.quantity,
            buy_price=sale.buy_price,
            estimated_delivery=sale.estimated_delivery,
            sale_date=sale.sale_date,
            buyer_name=sale.buyer_name,
            buyer_address=sale.buyer_address,
            delivery_status=sale.delivery_status,
            manage_link=sale.manage_link,
            amazon_link=sale.amazon_link,
            payment_link=sale.payment_link,
            region_id=sale.region_id,
            forex_fees=sale.forex_fees
        )
        db.add(deleted_sale)
        db.delete(sale)
        db.commit()
    return RedirectResponse("/admin/view_orders", status_code=303)

@router.get("/admin/restore_order/{sale_id}")
async def restore_sale(sale_id: int, db: Session = Depends(get_db)):
    deleted_sale = db.query(DeletedSale).filter(DeletedSale.id == sale_id).first()
    if deleted_sale:
        sale = Sale(
            id=deleted_sale.id,
            product_name=deleted_sale.product_name,
            product_description=deleted_sale.product_description,
            supplier_name=deleted_sale.supplier_name,
            order_datetime=deleted_sale.order_datetime,
            sale_price=deleted_sale.sale_price,
            amazon_commission=deleted_sale.amazon_commission,
            quantity=deleted_sale.quantity,
            buy_price=deleted_sale.buy_price,
            estimated_delivery=deleted_sale.estimated_delivery,
            sale_date=deleted_sale.sale_date,
            buyer_name=deleted_sale.buyer_name,
            buyer_address=deleted_sale.buyer_address,
            delivery_status=deleted_sale.delivery_status,
            manage_link=deleted_sale.manage_link,
            amazon_link=deleted_sale.amazon_link,
            payment_link=deleted_sale.payment_link,
            region_id=deleted_sale.region_id,
            forex_fees=deleted_sale.forex_fees
        )
        db.add(sale)
        db.delete(deleted_sale)
        db.commit()
    return RedirectResponse("/admin/deleted_orders", status_code=303)
