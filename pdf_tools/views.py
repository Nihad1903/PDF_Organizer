from django.shortcuts import render, redirect
from django.http import HttpResponse
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader  
from io import BytesIO
from PIL import Image
import re
from .utils import *

def choicePage(request):
    return render(request, 'pdf_tools/choice.html')

def mergePdfs(request):
    if request.method == "POST":
        try:
            pdfs = request.FILES.getlist('pdfs')
            if not pdfs:
                return render(request, 'pdf_tools/error.html', {'error': 'No PDF files uploaded.'})

            merger = PdfWriter()
            for pdf in pdfs:
                if pdf.content_type != 'application/pdf':
                    return render(request, 'pdf_tools/error.html', {'error': 'Invalid file type. Please upload PDF files only.'})
                merger.append(pdf)

            buffer = BytesIO()
            merger.write(buffer)
            merger.close()
            buffer.seek(0)

            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="merged-pdf.pdf"'
            return response
        except Exception as e:
            return render(request, 'pdf_tools/error.html', {'error': str(e)})
    return render(request, 'pdf_tools/upload.html')


def splitPdfs(request):
    if request.method == "POST":
        try:
            if 'pdf' not in request.FILES:
                return render(request, 'pdf_tools/error.html', 
                            {'error': 'No PDF file uploaded'})
                
            pdf_file = request.FILES['pdf']
            if not pdf_file.content_type == 'application/pdf':
                return render(request, 'pdf_tools/error.html', 
                            {'error': 'Invalid file type. Please upload a PDF file'})
                
            if 'pages' not in request.POST or not request.POST['pages'].strip():
                return render(request, 'pdf_tools/error.html', 
                            {'error': 'Please specify page ranges'})
                
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            if total_pages == 0:
                return render(request, 'pdf_tools/error.html', 
                            {'error': 'The uploaded PDF file is empty'})
                
            try:
                page_numbers = parse_page_ranges(request.POST['pages'], total_pages)
            except ValueError as e:
                return render(request, 'pdf_tools/error.html', {'error': str(e)})
                
            if not page_numbers:
                return render(request, 'pdf_tools/error.html', 
                            {'error': 'No valid pages selected'})
                
            buffer = split_pdf(pdf_file, page_numbers)
            
            filename = f"split-pdf-pages-{request.POST['pages'].replace(' ', '')}.pdf"
            filename = re.sub(r'[^a-zA-Z0-9._-]', '-', filename)
            
            buffer.seek(0)
            request.session['pdf_data'] = {
                'file': buffer.getvalue().decode('latin-1'),
                'type': 'split_pdf',
                'filename': filename
            }
            
            return render(request, 'pdf_tools/split_success.html', {
                'success': True,
                'message': 'PDF successfully split!'
            })
            
        except Exception as e:
            return render(request, 'pdf_tools/error.html', 
                        {'error': f'An error occurred: {str(e)}'})
            
    return render(request, 'pdf_tools/split.html')


def imageToPdf(request):
    if request.method == "POST":
        try:
            images = request.FILES.getlist('images')

            for image in images:
                if not image.content_type.startswith('image/'):
                    return render(request, 'pdf_tools/error.html', {'error': 'Invalid file type. Please upload image files only.'})

            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)

            for image in images:
                img = Image.open(image)
                img_width, img_height = img.size

                pdf.setPageSize((img_width, img_height))

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img_reader = ImageReader(img)

                pdf.drawImage(img_reader, 0, 0, width=img_width, height=img_height)
                pdf.showPage()

            pdf.save()

            buffer.seek(0)
            request.session['pdf_data'] = {
                'file': buffer.getvalue().decode('latin-1'),
                'type': 'image_to_pdf',
                'filename': 'images-to-pdf.pdf'
            }

            return render(request, 'pdf_tools/image_success.html', {
                'success': True,
                'message': 'Images successfully converted to PDF!'
            })
        
        except Exception as e:
            return render(request, 'pdf_tools/error.html', {'error': str(e)})
    return render(request, 'pdf_tools/image_to_pdf.html')

def download_pdf(request):
    if 'pdf_data' in request.session:
        try:
            pdf_data = request.session['pdf_data']
            file_content = pdf_data['file'].encode('latin-1')
            filename = pdf_data['filename']
            
            del request.session['pdf_data']
            
            response = HttpResponse(file_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return render(request, 'pdf_tools/error.html', 
                        {'error': f'Download error: {str(e)}'})
    
    return HttpResponse('No PDF found', status=404)