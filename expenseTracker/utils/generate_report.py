from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
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



def generate_overall_balance_sheet_pdf(response_data):
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="overall_balance_sheet.pdf"'
    
    # Create PDF document
    pdf = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Fetch data from response_data
    user_id = response_data['user_id']
    total_expenses_created = response_data['total_expenses_created']
    total_owed_by_user = response_data['total_owed_by_user']
    total_paid_by_user = response_data['total_paid_by_user']
    give_expenses = response_data['give_expenses']
    get_expenses = response_data['get_expenses']
    
    # Define a stylesheet
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']

    # Title
    title = Paragraph(f"Overall Balance Sheet for User ID: {user_id}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Summary
    total_created_paragraph = Paragraph(f"<b>Total Expenses Created:</b> {total_expenses_created:.2f}", normal_style)
    elements.append(total_created_paragraph)
    total_paid_paragraph = Paragraph(f"<b>Total Paid by User:</b> {total_paid_by_user:.2f}", normal_style)
    elements.append(total_paid_paragraph)
    total_owed_paragraph = Paragraph(f"<b>Total Owed by User:</b> {total_owed_by_user:.2f}", normal_style)
    elements.append(total_owed_paragraph)
    elements.append(Spacer(1, 12))

    # Expenses where user has to give (Owes money)
    elements.append(Paragraph("<b>Expenses where you owe money:</b>", styles['Heading2']))
    if give_expenses:
        give_data = [['Expense ID', 'Description', 'Created By', 'Amount Owed']]
        for expense in give_expenses:
            give_data.append([
                expense['expense_id'],
                expense['description'],
                expense['created_by'],
                f"{expense['total_owed']:.2f}"
            ])

        # Create give expenses table
        give_table = Table(give_data)
        give_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(give_table)
    else:
        elements.append(Paragraph("You don't owe any money.", normal_style))
    elements.append(Spacer(1, 12))

    # Expenses where user gets (Others owe them money)
    elements.append(Paragraph("<b>Expenses where others owe you money:</b>", styles['Heading2']))
    if get_expenses:
        get_data = [['Expense ID', 'Description', 'Amount Paid', 'Participants Who Owe You']]
        for expense in get_expenses:
            participants_owe = ", ".join([f"{p['user_name']}: {p['amount_owed']:.2f}" for p in expense['owes']])
            get_data.append([
                expense['expense_id'],
                expense['description'],
                f"{expense['total_paid']:.2f}",
                participants_owe
            ])

        # Create get expenses table
        get_table = Table(get_data)
        get_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(get_table)
    else:
        elements.append(Paragraph("No one owes you money.", normal_style))

    # Build the PDF
    pdf.build(elements)

    return response