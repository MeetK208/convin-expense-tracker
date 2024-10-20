from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

def generate_balance_sheet_pdf(response_data):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="balance_sheet.pdf"'
    
    # Create PDF document
    pdf = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Fetch the data from response_data
    user_id = response_data['user_id']
    total_expenses = response_data['total_expenses']
    expenses = response_data['expenses']
    total_user_expenses = response_data['total_user_expenses']
    total_owed_to_user = response_data['total_owed_to_user']
    
    # Define a stylesheet
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']

    # Title
    title = Paragraph(f"Balance Sheet for User ID: {user_id}", title_style)
    elements.append(title)

    # Total expenses summary
    total_expenses_paragraph = Paragraph(f"<b>Total Expenses:</b> {total_expenses}", normal_style)
    elements.append(total_expenses_paragraph)
    total_user_expenses_paragraph = Paragraph(f"<b>Total User Expenses:</b> {total_user_expenses}", normal_style)
    elements.append(total_user_expenses_paragraph)
    total_owed_to_user_paragraph = Paragraph(f"<b>Total Owed to User:</b> {total_owed_to_user}", normal_style)
    elements.append(total_owed_to_user_paragraph)
    
    # Add some space
    elements.append(Paragraph("<br/><br/>", normal_style))

    # Table header and data
    data = [['Expense ID', 'Description', 'User Expense']]
    for expense in expenses:
        data.append([expense['expense_id'], expense['description'], f"{expense['user_expense']:.2f}"])

    # Create the table
    table = Table(data)
    
    # Table style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Append table to elements
    elements.append(table)

    # Build the PDF
    pdf.build(elements)

    return response
