from fastapi import APIRouter, Request, Depends, HTTPException, Query, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import date, datetime, timedelta
from typing import Optional
from database import get_db
from models import Sale, CRUDLog, UpdateStatusRequest, Region
from pathlib import Path
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db), page: int = 1, per_page: int = 10):
    if request.cookies.get("authenticated") != "true":
        return RedirectResponse("/login")
    total_sales = db.query(Sale).count()
    sales = db.query(Sale).order_by(desc(Sale.id)).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total_sales + per_page - 1) // per_page
    return templates.TemplateResponse("admin.html", {"request": request, "sales": sales, "page": page, "total_pages": total_pages, "per_page": per_page})

@router.get("/admin/orders_by_region/{region_id}", response_class=HTMLResponse)
async def orders_by_region(region_id: int, request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("authenticated") != "true":
        return RedirectResponse("/login")
    
    sales = db.query(Sale).filter(Sale.region_id == region_id).order_by(desc(Sale.id)).all()
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    return templates.TemplateResponse("orders_by_region.html", {"request": request, "sales": sales, "region": region})

@router.get("/admin/countries", response_class=HTMLResponse)
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

    if sale_date_start:
        query = query.filter(Sale.sale_date >= sale_date_start)

    if sale_date_end:
        query = query.filter(Sale.sale_date <= sale_date_end)

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
