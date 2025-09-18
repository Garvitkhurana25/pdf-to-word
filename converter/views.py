from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadPDFForm
import pdfplumber
from docx import Document
import os
import tempfile
import uuid

def convert_pdf_2_word(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']

            temp_pdf_path = os.path.join(tempfile.gettempdir(),f"temp_{uuid.uuid4().hex}.pdf")
            output_word_path = os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4().hex}.docx")

            try:
                with open(temp_pdf_path,'wb') as temp_file:
                    for chunk in pdf_file.chunks():
                        temp_file.write(chunk)
                full_text = ""

                with pdfplumber.open(temp_pdf_path) as pdf:
                    for page in pdf.pages:
                        full_text += page.extract_text() + "\n"
                
                document = Document()
                for line in full_text.split("\n"):
                    document.add_paragraph(line.strip())
                document.save(output_word_path)

                with open(output_word_path,"rb") as docx_file:
                    response = HttpResponse(docx_file.read(),content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.docmuent")
                    response['Content-Disposition'] = f"attachment; filename={os.path.basename(output_word_path)}"
                
                os.remove(temp_pdf_path)
                os.remove(output_word_path)
                return response
            except Exception as e:
                return HttpResponse("An Error Occurred: ",str(e),status=500)
    else:
        form = UploadPDFForm()
    return render(request, "converter/upload.html",{"form":form})
