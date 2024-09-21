import uuid
from django.db import models
from django.contrib.auth.models import User
from utils.render_pdf_from_template import render_pdf_from_template
from utils.send_email import send_email

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    detailed_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image = models.ImageField(upload_to='products/covers/')

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')

    def __str__(self):
        return f"Image {self.id} for {self.product.name}"


class UserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchased_by')
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_details = models.JSONField()
    invoice_no = models.CharField(max_length=100, unique=True, editable=False)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} (Purchased on {self.purchase_date})"

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = str(uuid.uuid4())  # Generate a unique invoice number
        super().save(*args, **kwargs)
        self.post_save_action()

    def post_save_action(self):
        # Define the context for the invoice
        context = {
            'invoice_no': self.invoice_no,
            'purchase_date': self.purchase_date.strftime('%B %d, %Y'),
            'user': self.user,
            'product': self.product,
        }

        pdf = render_pdf_from_template('store/email_templates/invoice.html', context)

        if pdf:
            # Email subject and body
            subject = f"Invoice for your purchase of {self.product.name}"
            message = f"Dear {self.user.username},\n\nThank you for your purchase. Please find your invoice attached.\n\nBest regards,\nYour Company"

            # Attachment for the PDF
            attachments = [
                {
                    'name': f'Invoice_{self.invoice_no}.pdf',
                    'content': pdf,
                    'mime_type': 'application/pdf'
                }
            ]

            # Send email with attachment
            send_email(subject, message, [self.user.email], attachments=attachments)