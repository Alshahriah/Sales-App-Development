from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, datetime
from database import get_db
from models import Sale, CRUDLog, UpdateStatusRequest, Region, DeletedSale
from pathlib import Path
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

def log_crud_action(action: str, model: str, record_id: int, db: Session, user: str = None, details: str = None):
    log_entry = CRUDLog(action=action, model=model, record_id=record_id, user=user, details=details)
    db.add(log_entry)
    db.commit()

@router.get("/create_sale", response_class=HTMLResponse)
async def create_sale_form(request: Request, db: Session = Depends(get_db)):
    regions = db.query(Region).all()  # Fetch all regions from the database
    return templates.TemplateResponse("create_sale.html", {"request": request, "regions": regions})

@router.post("/create_sale", response_class=HTMLResponse)
async def create_sale(
    request: Request,
    product_name: str = Form(...),
    product_description: str = Form(None),
    supplier_name: str = Form(...),
    order_datetime: str = Form(None),
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
    user = request.cookies.get("username")
    new_sale = Sale(
        product_name=product_name,
        product_description=product_description,
        supplier_name=supplier_name,
        order_datetime=datetime.utcnow() if order_datetime is None else datetime.fromisoformat(order_datetime),
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
        user=user,
        details=f"Created sale for product '{product_name}' from order <a href='/orderdetails/{new_sale.id}'>{buyer_name}</a>"
    )
    return RedirectResponse("/", status_code=303)

@router.get("/edit/{sale_id}", response_class=HTMLResponse)
async def edit_sale_form(sale_id: int, request: Request, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    regions = db.query(Region).all()  # Fetch all regions from the database
    return templates.TemplateResponse("edit_sale.html", {"request": request, "sale": sale, "regions": regions})

@router.post("/edit/{sale_id}", response_class=HTMLResponse)
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
    user = request.cookies.get("username")
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
        user=user,
        details=f"Updated sale <a href='/orderdetails/{sale.id}'>{buyer_name}</a> for product '{product_name}'"
    )
    return RedirectResponse(referrer or "/admin", status_code=303)

@router.post("/delete/{sale_id}", response_class=HTMLResponse)
async def delete_sale(sale_id: int, request: Request, db: Session = Depends(get_db)):
    user = request.cookies.get("username")
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Create a DeletedSale record
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

    # Add DeletedSale record and delete original sale
    db.add(deleted_sale)
    db.delete(sale)
    db.commit()
    
    log_crud_action(
        action="DELETE",
        model="Sale",
        record_id=sale.id,
        db=db,
        user=user,
        details=f"Deleted sale <a href='/orderdetails/{sale.id}'>{sale.buyer_name}</a> for product '{sale.product_name}'"
    )
    return RedirectResponse("/admin", status_code=303)

@router.get("/orderdetails/{id}", response_class=HTMLResponse)
async def order_details(id: int, request: Request, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return templates.TemplateResponse("order_details.html", {"request": request, "sale": sale})

@router.post("/update_status/{sale_id}", response_class=RedirectResponse)
async def update_status(request: Request, sale_id: int, delivery_status: str = Form(...), redirect_url: str = Form(...), db: Session = Depends(get_db)):
    user = request.cookies.get("username")
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    sale.delivery_status = delivery_status
    db.commit()
    log_crud_action(
        action="UPDATE",
        model="Sale",
        record_id=sale.id,
        db=db,
        user=user,
        details=f"Updated delivery status for sale <a href='/orderdetails/{sale.id}'>{sale.buyer_name}</a> to '{delivery_status}'"
    )
    return RedirectResponse(url=redirect_url, status_code=303)
