from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Sale, CRUDLog, UpdateStatusRequest, Region
from pathlib import Path
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

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
