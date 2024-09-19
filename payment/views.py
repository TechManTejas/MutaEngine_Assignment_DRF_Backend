import os
import hmac
import hashlib
import json
import razorpay
import time
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Order

client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)


class CreateOrderViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"], url_path="create-order")
    def create_order(self, request, *args, **kwargs):
        # Razorpay requires the amount in paise
        amount = 1000 * 100

        # Create an order on Razorpay
        order_receipt = f"receipt_{int(time.time())}"
        order_currency = "INR"
        notes = {"user_id": request.user.id}

        razorpay_order = client.order.create(
            {
                "amount": amount,
                "currency": order_currency,
                "receipt": order_receipt,
                "notes": notes,
            }
        )

        # Store the Razorpay order details in the database
        Order.objects.create(
            order_id=razorpay_order["id"],
            user=request.user,
            amount=amount,
            completed=False,
        )

        return Response(
            {
                "order_id": razorpay_order["id"],
                "razorpay_key_id": os.getenv("RAZORPAY_KEY_ID"),
                "amount": amount,
                "currency": order_currency,
            },
            status=status.HTTP_200_OK,
        )


class PaymentWebhookViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="verify-payment")
    def verify_payment(self, request, *args, **kwargs):
        # Debugging headers and payload
        print("Headers:", request.headers)
        print("Payload:", request.data)

        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            return Response({"error": "Signature missing"}, status=status.HTTP_400_BAD_REQUEST)

        webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
        payload = json.dumps(request.data, separators=(",", ":"))  # Convert to JSON string
        expected_signature = hmac.new(
            webhook_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # Get payment and order details
        payment_data = request.data.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_data.get("order_id")

        if not order_id:
            return Response({"error": "Order ID missing from payload"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the order in the database
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the payment was captured successfully
        if payment_data.get("status") != "captured":
            return Response({"error": "Payment not captured"}, status=status.HTTP_400_BAD_REQUEST)

        # Update order status and user's subscription
        order.completed = True
        order.save()

        # Payment successful now create invoice and send to email
        self.process_order(order)

        return Response({"status": "Payment successful"}, status=status.HTTP_200_OK)

    def process_order(self, order):
        pass