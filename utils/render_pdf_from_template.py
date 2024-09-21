from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa


def render_pdf_from_template(template_src, context_dict):
    html_string = render_to_string(template_src, context_dict)
    result = BytesIO()

    # Create PDF using pisa
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None
