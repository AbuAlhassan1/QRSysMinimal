from typing import Any, Dict
from core import db
from models import ApartmentInfo, ClientInfo
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
import io
from reportlab.lib.pagesizes import A4
import tempfile
import os
import asyncio
from playwright.async_api import async_playwright
from api.deps import CurrentUser
from sqlmodel import Session, select
from utils import generate_qr_code_with_data

router = APIRouter(prefix="/pages", tags=["pages"])

templates = Jinja2Templates(directory="templates")

@router.get("/")
def read_pages(request : Request, no : int, apt_id : int) -> Any:
    with Session(db.engine) as session:
        apt_info = session.exec(select(ApartmentInfo).where(ApartmentInfo.id == apt_id)).first()
        if not apt_info:
            raise HTTPException(status_code=404, detail="Apartment not found")
        
        # Get client information
        client_info = session.exec(select(ClientInfo).where(ClientInfo.apt_id == apt_id)).first()
        if not client_info:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Prepare data for QR code - Client data first in Arabic
        client_data = {
            "معرف": client_info.id,
            "رقم": client_info.no,
            "الاسم": client_info.name,
            "رقم الهوية": client_info.id_no,
            "رقم الهاتف": client_info.phone_number,
            "المهنة": client_info.job_title,
            "تاريخ الإصدار": str(client_info.issue_date),
            "رقم السجل": client_info.registry_no,
            "رقم الصحيفة": client_info.newspaper_no,
            "المحلة": client_info.m,
            "الزقاق": client_info.z,
            "الدار": client_info.d,
            "اسم البديل": client_info.alt_name,
            "صلة القرابة": client_info.alt_kinship,
            "هاتف البديل": client_info.alt_phone,
            "تاريخ الإنشاء": str(client_info.created_at)
        }
        
        # Apartment data in Arabic
        apartment_data = {
            "معرف": apt_info.id,
            "العمارة": apt_info.building,
            "الطابق": apt_info.floor,
            "رقم الشقة": apt_info.apt_no,
            "المساحة": apt_info.area,
            "سعر المتر": apt_info.meter_price,
            "نوع الشقة": apt_info.apt_type,
            "السعر الكلي": apt_info.area * apt_info.meter_price
        }
        
        # Generate QR code with client data first
        qr_code_data_uri = generate_qr_code_with_data(client_data, apartment_data)
        
        data = {
            "id": str(no).zfill(3)+ " : " + "العدد",
            "buildng": str(apt_info.building)+ " | " + "العمارة",
            "floor": str(apt_info.floor)+ " | " + "الطابق",
            "apartment": str(apt_info.apt_no)+ " | " + "الشقة",
            "qr_code": qr_code_data_uri
        }
    return templates.TemplateResponse("page/page1.html", {"request": request, "data": data})

@router.get("/page2")
def read_page2(request : Request, client_id : int) -> Any:
    with Session(db.engine) as session:
        client_info = session.exec(select(ClientInfo).where(ClientInfo.id == client_id)).first()
        if not client_info:
            raise HTTPException(status_code=404, detail="Client not found")
        
        data = {
            "date": client_info.created_at,
            "id": str(client_info.no).zfill(3),
            "customer_name": client_info.name,
            "unified_card_number": client_info.id_no,
            "id_number": client_info.id_no,
            "registry_number": client_info.registry_no,
            "newspaper_number": client_info.newspaper_no,
            "issue_date": client_info.issue_date,
            "district": client_info.m,
            "street": client_info.z,
            "house": client_info.d,
            "alt_district": client_info.m,
            "alt_street": client_info.z,
            "alt_house": client_info.d,
            "phone_number": client_info.phone_number,
            "job_title": client_info.job_title,
            "alt_person_name": client_info.alt_name,
            "relationship": client_info.alt_kinship,
            "alt_person_number": client_info.alt_phone
    }
    return templates.TemplateResponse("page/page2.html", {"request": request, "data": data})

@router.get("/page3")
def read_page3(request : Request, apt_id : int) -> Any:
    with Session(db.engine) as session:
        apartment_info = session.exec(select(ApartmentInfo).where(ApartmentInfo.id == apt_id)).first()
        if not apartment_info:
            raise HTTPException(status_code=404, detail="Apartment not found")
        client_info = session.exec(select(ClientInfo).where(ClientInfo.apt_id == apt_id)).first()
        if not client_info:
            raise HTTPException(status_code=404, detail="Client not found")
        data = {
            "id": str(client_info.no).zfill(3),
            "date": client_info.created_at,
            "apartment_number": apartment_info.apt_no,
            "building": apartment_info.building,
            "floor": apartment_info.floor,
            "apartment": apartment_info.apt_type,
            "area": apartment_info.area
        }
    return templates.TemplateResponse("page/page3.html", {"request": request, "data": data})

@router.get("/page4")
def read_page4(request : Request) -> Any:
    return templates.TemplateResponse("page/page4.html", {"request": request})

@router.get("/page5")
def read_page5(request : Request) -> Any:
    return templates.TemplateResponse("page/page5.html", {"request": request})

@router.get("/page6")
def read_page6(request : Request) -> Any:
    return templates.TemplateResponse("page/page6.html", {"request": request})

@router.get("/page7")
def read_page7(request : Request) -> Any:
    return templates.TemplateResponse("page/page7.html", {"request": request})

@router.get("/page8")
def read_page8(request : Request, apt_id : int) -> Any:
    with Session(db.engine) as session:
        apartment_info = session.exec(select(ApartmentInfo).where(ApartmentInfo.id == apt_id)).first()
        if not apartment_info:
            raise HTTPException(status_code=404, detail="Apartment not found")
        data = {
            'aptType' : apartment_info.apt_type
        }
    return templates.TemplateResponse("page/page8.html", {"request": request , 'data': data})

@router.get("/page9")
def read_page9(request : Request, apt_id : int) -> Any:
    with Session(db.engine) as session:
        apartment_info = session.exec(select(ApartmentInfo).where(ApartmentInfo.id == apt_id)).first()
        if not apartment_info:
            raise HTTPException(status_code=404, detail="Apartment not found")
        data = {
            'aptType' : apartment_info.apt_type
        }
    return templates.TemplateResponse("page/page9.html", {"request": request , 'data': data})

@router.get("/page10")
def read_page10(request : Request, apt_id : int) -> Any:
    with Session(db.engine) as session:
        apartment_info = session.exec(select(ApartmentInfo).where(ApartmentInfo.id == apt_id)).first()
        if not apartment_info:
            raise HTTPException(status_code=404, detail="Apartment not found")
        data = {
            'price' : apartment_info.meter_price,
            'area' : apartment_info.area
        }
    return templates.TemplateResponse("page/page10.html", {"request": request , 'data': data})

# async def capture_page_pdfs(base_url: str, page_endpoints: list[str], output_dir: str) -> list[str]:
#     """
#     Capture PDFs of each page directly using Playwright.
    
#     Args:
#         base_url: The base URL of the application
#         page_endpoints: List of page endpoints to capture
#         output_dir: Directory to save the PDFs
        
#     Returns:
#         List of paths to the saved PDFs
#     """
#     pdf_paths = []
    
#     async with async_playwright() as p:
#         # Launch browser
#         browser = await p.chromium.launch(headless=True)
        
#         # Create a high-quality context
#         context = await browser.new_context(
#             viewport={"width": 1280, "height": 1696},  # Wide enough for A4
#             device_scale_factor=2.0,  # Higher quality rendering
#             is_mobile=False,
#             has_touch=False,
#             ignore_https_errors=True
#         )
        
#         # Enable console logging
#         page = await context.new_page()
#         page.on("console", lambda msg: print(f"BROWSER LOG: {msg.text}"))
#         page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err}"))
        
#         for i, endpoint in enumerate(page_endpoints):
#             try:
#                 full_url = f"{base_url.rstrip('/')}{endpoint}"
#                 print(f"Navigating to: {full_url}")
                
#                 # Navigate to the page with longer timeout
#                 response = await page.goto(full_url, wait_until="networkidle", timeout=30000)
                
#                 # Check if the navigation was successful
#                 if response.status >= 400:
#                     print(f"Error loading page {endpoint}: HTTP {response.status}")
#                     # Create a simple error PDF
#                     pdf_path = os.path.join(output_dir, f"page_{i+1}_error.pdf")
#                     # Use reportlab to create an error PDF
#                     from reportlab.pdfgen import canvas
#                     c = canvas.Canvas(pdf_path, pagesize=A4)
#                     c.drawString(100, 500, f"Error loading page: HTTP {response.status}")
#                     c.save()
#                     pdf_paths.append(pdf_path)
#                     continue
                
#                 # Wait a bit for any JavaScript to finish rendering
#                 await asyncio.sleep(2)
                
#                 # Optimize the page for PDF printing
#                 await page.evaluate("""() => {
#                     document.body.style.width = '210mm';
#                     document.body.style.height = '297mm';
#                     document.body.style.margin = '0';
#                     document.body.style.padding = '0';
#                     document.documentElement.style.width = '210mm';
#                     document.documentElement.style.height = '297mm';
#                     document.documentElement.style.margin = '0';
#                     document.documentElement.style.padding = '0';
                    
#                     // Force all elements to properly fit
#                     const allElements = document.querySelectorAll('*');
#                     for (const el of allElements) {
#                         if (el.style.position === 'fixed' || el.style.position === 'absolute') {
#                             el.style.maxWidth = '210mm';
#                         }
#                     }
                    
#                     // Set print-specific CSS
#                     const style = document.createElement('style');
#                     style.textContent = `
#                         @media print {
#                             body {
#                                 width: 210mm;
#                                 height: 297mm;
#                                 margin: 0;
#                                 padding: 0;
#                             }
#                             * {
#                                 page-break-inside: avoid;
#                             }
#                         }
#                     `;
#                     document.head.appendChild(style);
#                 }""")
                
#                 # Generate a PDF directly
#                 pdf_path = os.path.join(output_dir, f"page_{i+1}.pdf")
#                 await page.pdf(
#                     path=pdf_path,
#                     format="A4",
#                     print_background=True,
#                     prefer_css_page_size=True,
#                     margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
#                     scale=1.0  # No scaling
#                 )
                
#                 pdf_paths.append(pdf_path)
#                 print(f"PDF saved: {pdf_path}")
                
#             except Exception as e:
#                 print(f"Error capturing {endpoint}: {str(e)}")
#                 # Create a simple error PDF
#                 pdf_path = os.path.join(output_dir, f"page_{i+1}_error.pdf")
#                 # Use reportlab to create an error PDF
#                 from reportlab.pdfgen import canvas
#                 c = canvas.Canvas(pdf_path, pagesize=A4)
#                 c.drawString(100, 500, f"Error: {str(e)}")
#                 c.save()
#                 pdf_paths.append(pdf_path)
        
#         await browser.close()
    
#     return pdf_paths

@router.get("/Generate-pdf/{client_id}")
async def generate_direct_pdf(request: Request, client_id: int, current_user: CurrentUser) -> Any:
    """
    Endpoint that renders templates directly to PDFs.
    Uses in-memory rendering and Playwright to generate PDFs.
    """
    with Session(db.engine) as session:
        client_info = session.exec(select(ClientInfo).where(ClientInfo.id == client_id)).first()
        if not client_info:
            raise HTTPException(status_code=404, detail="Client not found")
        apartment_info = session.exec(select(ApartmentInfo).where(ApartmentInfo.id == client_info.apt_id)).first()
        if not apartment_info:
            raise HTTPException(status_code=404, detail="Apartment not found")
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # List of functions and parameters to render each page
        page_renderers = [
            (read_pages, {"no": client_info.no, "apt_id": apartment_info.id}),
            (read_page2, {"client_id": client_info.id}),
            (read_page3, {"apt_id": apartment_info.id}),
            (read_page4, {}),
            (read_page5, {}),
            (read_page6, {}),
            (read_page7, {}),
            (read_page8, {"apt_id": apartment_info.id}),
            (read_page9, {"apt_id": apartment_info.id}),
            (read_page10, {"apt_id": apartment_info.id})
        ]
        
        # Generate HTML and PDFs for each page
        pdf_paths = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 1696},
                device_scale_factor=2.0,
                ignore_https_errors=True
            )
            page = await context.new_page()
            
            for i, (renderer_func, params) in enumerate(page_renderers):
                try:
                    # Call the function that would normally render the template
                    response = renderer_func(request, **params)
                    
                    # If the response is a TemplateResponse, get the rendered HTML
                    if hasattr(response, "template") and hasattr(response, "context"):
                        # Render the template to HTML
                        rendered_html = templates.get_template(response.template.name).render(**response.context)
                        
                        # Add proper CSS for print
                        html_with_css = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <style>
                                @page {{
                                    size: A4;
                                    margin: 0;
                                }}
                                @media print {{
                                    body {{
                                        width: 210mm;
                                        height: 297mm;
                                        margin: 0;
                                        padding: 0;
                                    }}
                                }}
                                body {{
                                    width: 210mm;
                                    height: 297mm;
                                    margin: 0;
                                    padding: 0;
                                }}
                            </style>
                        </head>
                        <body>
                        {rendered_html}
                        </body>
                        </html>
                        """
                        
                        # Create a temporary HTML file
                        html_path = os.path.join(temp_dir, f"page_{i+1}.html")
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(html_with_css)
                        
                        # Navigate to the file
                        await page.goto(f"file://{html_path}", wait_until="networkidle")
                        
                        # Wait for JavaScript rendering
                        await asyncio.sleep(1)
                        
                        # Optimize for PDF print
                        await page.evaluate("""() => {
                            document.body.style.width = '210mm';
                            document.body.style.height = '297mm';
                            document.body.style.margin = '0';
                            document.body.style.padding = '0';
                            document.documentElement.style.width = '210mm';
                            document.documentElement.style.height = '297mm';
                            document.documentElement.style.margin = '0';
                            document.documentElement.style.padding = '0';
                        }""")
                        
                        # Generate PDF
                        pdf_path = os.path.join(temp_dir, f"page_{i+1}.pdf")
                        await page.pdf(
                            path=pdf_path,
                            format="A4",
                            print_background=True,
                            prefer_css_page_size=True,
                            margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
                            scale=1.0
                        )
                        
                        pdf_paths.append(pdf_path)
                        print(f"PDF saved: {pdf_path}")
                    else:
                        print(f"Skipping page {i+1}: Not a template response")
                        
                except Exception as e:
                    print(f"Error rendering page {i+1}: {str(e)}")
                    # Create a simple error PDF
                    pdf_path = os.path.join(temp_dir, f"page_{i+1}_error.pdf")
                    from reportlab.pdfgen import canvas
                    c = canvas.Canvas(pdf_path, pagesize=A4)
                    c.drawString(100, 500, f"Error rendering page {i+1}")
                    c.drawString(100, 480, str(e))
                    c.save()
                    pdf_paths.append(pdf_path)
            
            await browser.close()
        
        # Combine all PDFs
        if pdf_paths:
            # Use PyPDF2 to merge PDFs
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    merger.append(pdf_path)
            
            merged_path = os.path.join(temp_dir, "combined.pdf")
            merger.write(merged_path)
            merger.close()
            
            # Read the merged PDF
            with open(merged_path, "rb") as f:
                pdf_bytes = f.read()
            
            # Return the PDF as a streaming response
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=combined_pages.pdf"}
            )
        else:
            # Return an empty PDF if no pages were rendered
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.drawString(100, 750, "No pages were rendered successfully")
            c.save()
            buffer.seek(0)
            return StreamingResponse(
                buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=error.pdf"}
            )