from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.payments.models import Payment
from apps.jobs.models import Job
from .serializers import PaymentSerializer

class PaymentHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(customer=self.request.user).order_by('-created_at')

class InitializePaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, customer=request.user)
        payment = job.payments.filter(payment_type='commitment_fee', status='pending').first()

        if not payment:
            return Response({"error": "No pending payment found for this job"}, status=400)

        # TODO: Integrate with Paystack when you get API keys
        # import requests
        # headers = {
        #     'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        #     'Content-Type': 'application/json'
        # }
        # data = {
        #     'email': request.user.email,
        #     'amount': int(payment.amount * 100),
        #     'reference': payment.paystack_reference,
        #     'callback_url': f'{settings.FRONTEND_URL}/payment/callback'
        # }
        # response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)
        # paystack_data = response.json()
        #
        # if paystack_data['status']:
        #     payment.paystack_access_code = paystack_data['data']['access_code']
        #     payment.paystack_authorization_url = paystack_data['data']['authorization_url']
        #     payment.status = 'processing'
        #     payment.save()
        #
        #     return Response({
        #         "payment_reference": payment.payment_reference,
        #         "authorization_url": payment.paystack_authorization_url,
        #         "amount": payment.amount,
        #         "job_id": str(job.id)
        #     })

        return Response({
            "payment_reference": payment.payment_reference,
            "authorization_url": "https://checkout.paystack.com/mock",
            "amount": float(payment.amount),
            "job_id": str(job.id),
            "message": "TODO: Complete Paystack integration with your API keys"
        })

class PaymentVerificationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference):
        try:
            payment = Payment.objects.get(payment_reference=reference)

            # TODO: Integrate with Paystack when you get API keys
            # import requests
            # headers = {
            #     'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'
            # }
            # response = requests.get(
            #     f'https://api.paystack.co/transaction/verify/{payment.paystack_reference}',
            #     headers=headers
            # )
            #
            # if response.status_code == 200:
            #     data = response.json()
            #
            #     if data['data']['status'] == 'success':
            #         payment.status = 'completed'
            #         payment.completed_at = timezone.now()
            #         payment.payment_method = data['data']['channel']
            #         payment.paystack_callback_data = data['data']
            #         payment.save()
            #
            #         return Response({
            #             "status": "success",
            #             "message": "Payment verified",
            #             "amount": float(payment.amount),
            #             "job_id": str(payment.job.id)
            #         })
            #     else:
            #         payment.status = 'failed'
            #         payment.failure_reason = data['data']['gateway_response']
            #         payment.save()
            #
            #         return Response({
            #             "status": "failed",
            #             "message": data['data']['gateway_response']
            #         }, status=400)

            return Response({
                "status": "pending",
                "message": "TODO: Complete Paystack verification with your API keys",
                "amount": float(payment.amount)
            })

        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

