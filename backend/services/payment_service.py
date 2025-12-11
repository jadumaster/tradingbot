"""
Payment Service
Handles Stripe subscriptions and payments
"""

import stripe
import logging
from datetime import datetime, timedelta
from models.user import SubscriptionTier


class PaymentService:
    """Payment processing and subscription management"""
    
    def __init__(self, stripe_api_key, db_manager):
        stripe.api_key = stripe_api_key
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Subscription pricing (in cents)
        self.pricing = {
            'pro_monthly': 2999,      # $29.99/month
            'pro_yearly': 29999,      # $299.99/year (17% discount)
            'enterprise_monthly': 9999,  # $99.99/month
            'enterprise_yearly': 99999   # $999.99/year (17% discount)
        }
    
    def create_customer(self, user_id, email, payment_method_id):
        """Create Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                payment_method=payment_method_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                },
                metadata={'user_id': user_id}
            )
            
            # Update user with Stripe customer ID
            user = self.db.get_user_by_id(user_id)
            user.stripe_customer_id = customer.id
            self.db.update_user(user)
            
            self.logger.info(f"Stripe customer created for user {user_id}")
            
            return {
                'success': True,
                'customer_id': customer.id
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe customer creation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def create_subscription(self, user_id, plan_type, billing_cycle='monthly'):
        """Create subscription for user"""
        try:
            user = self.db.get_user_by_id(user_id)
            
            if not user.stripe_customer_id:
                return {'success': False, 'message': 'No payment method on file'}
            
            # Determine price ID based on plan
            plan_key = f"{plan_type}_{billing_cycle}"
            price_amount = self.pricing.get(plan_key)
            
            if not price_amount:
                return {'success': False, 'message': 'Invalid plan type'}
            
            # Create Stripe price if not exists
            price = stripe.Price.create(
                unit_amount=price_amount,
                currency='usd',
                recurring={
                    'interval': 'month' if billing_cycle == 'monthly' else 'year'
                },
                product_data={
                    'name': f'Trading Bot {plan_type.title()} Plan'
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{'price': price.id}],
                metadata={
                    'user_id': user_id,
                    'plan_type': plan_type
                }
            )
            
            # Update user subscription
            tier = SubscriptionTier.PRO if plan_type == 'pro' else SubscriptionTier.ENTERPRISE
            user.subscription_tier = tier
            user.stripe_subscription_id = subscription.id
            user.subscription_start = datetime.utcnow()
            
            if billing_cycle == 'monthly':
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
            else:
                user.subscription_end = datetime.utcnow() + timedelta(days=365)
            
            self.db.update_user(user)
            
            self.logger.info(f"Subscription created for user {user_id}: {plan_type}")
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'status': subscription.status
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Subscription creation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def cancel_subscription(self, user_id):
        """Cancel user subscription"""
        try:
            user = self.db.get_user_by_id(user_id)
            
            if not user.stripe_subscription_id:
                return {'success': False, 'message': 'No active subscription'}
            
            # Cancel Stripe subscription
            subscription = stripe.Subscription.delete(user.stripe_subscription_id)
            
            # Update user
            user.subscription_tier = SubscriptionTier.FREE
            user.stripe_subscription_id = None
            self.db.update_user(user)
            
            self.logger.info(f"Subscription cancelled for user {user_id}")
            
            return {
                'success': True,
                'message': 'Subscription cancelled successfully'
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Subscription cancellation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def update_payment_method(self, user_id, payment_method_id):
        """Update customer payment method"""
        try:
            user = self.db.get_user_by_id(user_id)
            
            if not user.stripe_customer_id:
                return {'success': False, 'message': 'No customer found'}
            
            # Attach payment method
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=user.stripe_customer_id
            )
            
            # Update default payment method
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
            
            self.logger.info(f"Payment method updated for user {user_id}")
            
            return {
                'success': True,
                'message': 'Payment method updated'
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Payment method update error: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_billing_history(self, user_id):
        """Get billing history for user"""
        try:
            user = self.db.get_user_by_id(user_id)
            
            if not user.stripe_customer_id:
                return {'success': True, 'invoices': []}
            
            # Get invoices
            invoices = stripe.Invoice.list(
                customer=user.stripe_customer_id,
                limit=20
            )
            
            invoice_list = []
            for invoice in invoices.data:
                invoice_list.append({
                    'id': invoice.id,
                    'amount': invoice.amount_paid / 100,
                    'currency': invoice.currency,
                    'status': invoice.status,
                    'date': datetime.fromtimestamp(invoice.created).isoformat(),
                    'pdf_url': invoice.invoice_pdf
                })
            
            return {
                'success': True,
                'invoices': invoice_list
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Billing history error: {e}")
            return {'success': False, 'message': str(e)}
    
    def handle_webhook(self, payload, sig_header, webhook_secret):
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            # Handle different event types
            if event.type == 'customer.subscription.updated':
                self._handle_subscription_updated(event.data.object)
            elif event.type == 'customer.subscription.deleted':
                self._handle_subscription_deleted(event.data.object)
            elif event.type == 'invoice.payment_succeeded':
                self._handle_payment_succeeded(event.data.object)
            elif event.type == 'invoice.payment_failed':
                self._handle_payment_failed(event.data.object)
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Webhook error: {e}")
            return {'success': False, 'message': str(e)}
    
    def _handle_subscription_updated(self, subscription):
        """Handle subscription update"""
        user_id = subscription.metadata.get('user_id')
        if user_id:
            user = self.db.get_user_by_id(int(user_id))
            # Update subscription status
            self.logger.info(f"Subscription updated for user {user_id}")
    
    def _handle_subscription_deleted(self, subscription):
        """Handle subscription deletion"""
        user_id = subscription.metadata.get('user_id')
        if user_id:
            user = self.db.get_user_by_id(int(user_id))
            user.subscription_tier = SubscriptionTier.FREE
            self.db.update_user(user)
            self.logger.info(f"Subscription deleted for user {user_id}")
    
    def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        self.logger.info(f"Payment succeeded: {invoice.id}")
    
    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        self.logger.warning(f"Payment failed: {invoice.id}")
