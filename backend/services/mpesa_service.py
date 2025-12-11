"""
M-Pesa Payment Service
Handles M-Pesa STK Push, Pochi la Biashara, and payment verification
"""

import requests
import base64
import logging
from datetime import datetime
from requests.auth import HTTPBasicAuth
import json


class MPesaService:
    """M-Pesa Daraja API integration for payments"""
    
    def __init__(self, config, db_manager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # M-Pesa Configuration
        self.consumer_key = config.get('MPESA_CONSUMER_KEY')
        self.consumer_secret = config.get('MPESA_CONSUMER_SECRET')
        self.business_shortcode = config.get('MPESA_SHORTCODE', '174379')  # Your Till Number
        self.passkey = config.get('MPESA_PASSKEY')
        self.callback_url = config.get('MPESA_CALLBACK_URL')
        
        # Pochi la Biashara Configuration
        self.pochi_number = '+254718982047'  # Your business number
        self.till_number = '9508133'  # Your Till Number (if you have one)
        
        # API Endpoints
        self.sandbox = config.get('MPESA_SANDBOX', True)
        if self.sandbox:
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
        
        # Subscription Pricing in KES (Kenyan Shillings)
        # 1 USD ≈ 150 KES
        self.pricing_kes = {
            'pro_monthly': 4500,      # ~$30
            'pro_yearly': 45000,      # ~$300 (17% discount)
            'enterprise_monthly': 15000,  # ~$100
            'enterprise_yearly': 150000   # ~$1000 (17% discount)
        }
        
        self.access_token = None
        self.token_expiry = None
    
    def get_access_token(self):
        """Get M-Pesa API access token"""
        try:
            # Check if token is still valid
            if self.access_token and self.token_expiry:
                if datetime.now() < self.token_expiry:
                    return self.access_token
            
            # Request new token
            url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
            
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret)
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result['access_token']
                # Token expires in 3600 seconds (1 hour)
                from datetime import timedelta
                self.token_expiry = datetime.now() + timedelta(seconds=3500)
                
                self.logger.info("M-Pesa access token obtained")
                return self.access_token
            else:
                self.logger.error(f"Failed to get M-Pesa token: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"M-Pesa token error: {e}")
            return None
    
    def generate_password(self):
        """Generate password for STK Push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{self.business_shortcode}{self.passkey}{timestamp}"
        encoded = base64.b64encode(data_to_encode.encode()).decode('utf-8')
        return encoded, timestamp
    
    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate M-Pesa STK Push (Lipa na M-Pesa Online)
        
        Args:
            phone_number: Customer phone number (254XXXXXXXXX)
            amount: Amount to charge
            account_reference: Reference (e.g., user ID)
            transaction_desc: Description of transaction
            
        Returns:
            dict: Response with checkout ID and status
        """
        try:
            # Format phone number (remove + and spaces)
            phone = phone_number.replace('+', '').replace(' ', '')
            if not phone.startswith('254'):
                # Add Kenya country code if not present
                phone = f'254{phone.lstrip("0")}'
            
            # Get access token
            token = self.get_access_token()
            if not token:
                return {'success': False, 'message': 'Failed to authenticate with M-Pesa'}
            
            # Generate password and timestamp
            password, timestamp = self.generate_password()
            
            # Prepare request
            url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(amount),
                'PartyA': phone,
                'PartyB': self.business_shortcode,
                'PhoneNumber': phone,
                'CallBackURL': self.callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ResponseCode') == '0':
                    # Success - STK pushed to phone
                    checkout_id = result.get('CheckoutRequestID')
                    merchant_request_id = result.get('MerchantRequestID')
                    
                    # Save transaction record
                    self.save_mpesa_transaction({
                        'checkout_request_id': checkout_id,
                        'merchant_request_id': merchant_request_id,
                        'phone_number': phone,
                        'amount': amount,
                        'account_reference': account_reference,
                        'status': 'pending'
                    })
                    
                    self.logger.info(f"STK Push sent to {phone} for KES {amount}")
                    
                    return {
                        'success': True,
                        'message': 'Payment request sent to your phone',
                        'checkout_request_id': checkout_id,
                        'merchant_request_id': merchant_request_id
                    }
                else:
                    return {
                        'success': False,
                        'message': result.get('CustomerMessage', 'Payment request failed')
                    }
            else:
                self.logger.error(f"STK Push failed: {response.text}")
                return {
                    'success': False,
                    'message': 'Failed to initiate payment'
                }
                
        except Exception as e:
            self.logger.error(f"STK Push error: {e}")
            return {
                'success': False,
                'message': 'Payment initiation failed'
            }
    
    def query_stk_status(self, checkout_request_id):
        """Query STK Push transaction status"""
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'message': 'Authentication failed'}
            
            password, timestamp = self.generate_password()
            
            url = f'{self.base_url}/mpesa/stkpushquery/v1/query'
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('ResultCode'),
                    'description': result.get('ResultDesc')
                }
            else:
                return {'success': False, 'message': 'Query failed'}
                
        except Exception as e:
            self.logger.error(f"STK query error: {e}")
            return {'success': False, 'message': str(e)}
    
    def handle_callback(self, callback_data):
        """Handle M-Pesa payment callback"""
        try:
            # Extract callback data
            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            if result_code == 0:
                # Payment successful
                callback_metadata = stk_callback.get('CallbackMetadata', {})
                items = callback_metadata.get('Item', [])
                
                # Extract payment details
                payment_data = {}
                for item in items:
                    name = item.get('Name')
                    value = item.get('Value')
                    payment_data[name] = value
                
                # Update transaction
                self.update_mpesa_transaction(checkout_request_id, {
                    'status': 'completed',
                    'mpesa_receipt': payment_data.get('MpesaReceiptNumber'),
                    'transaction_date': payment_data.get('TransactionDate'),
                    'amount': payment_data.get('Amount'),
                    'phone_number': payment_data.get('PhoneNumber')
                })
                
                # Process subscription activation
                self.process_subscription_from_mpesa(checkout_request_id)
                
                self.logger.info(f"M-Pesa payment successful: {checkout_request_id}")
                
            else:
                # Payment failed or cancelled
                self.update_mpesa_transaction(checkout_request_id, {
                    'status': 'failed',
                    'failure_reason': result_desc
                })
                
                self.logger.warning(f"M-Pesa payment failed: {result_desc}")
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Callback processing error: {e}")
            return {'success': False, 'message': str(e)}
    
    def create_subscription_mpesa(self, user_id, plan_type, billing_cycle='monthly', phone_number=None):
        """
        Create subscription via M-Pesa payment
        
        Args:
            user_id: User ID
            plan_type: 'pro' or 'enterprise'
            billing_cycle: 'monthly' or 'yearly'
            phone_number: Customer M-Pesa number
        """
        try:
            user = self.db.get_user_by_id(user_id)
            
            if not phone_number:
                phone_number = user.phone
            
            if not phone_number:
                return {'success': False, 'message': 'Phone number required'}
            
            # Get price
            plan_key = f"{plan_type}_{billing_cycle}"
            amount = self.pricing_kes.get(plan_key)
            
            if not amount:
                return {'success': False, 'message': 'Invalid plan type'}
            
            # Initiate STK Push
            result = self.initiate_stk_push(
                phone_number=phone_number,
                amount=amount,
                account_reference=f"SUB_{user_id}",
                transaction_desc=f"Trading Bot {plan_type.title()} Subscription"
            )
            
            if result['success']:
                # Save pending subscription
                self.save_pending_subscription(
                    user_id=user_id,
                    checkout_request_id=result['checkout_request_id'],
                    plan_type=plan_type,
                    billing_cycle=billing_cycle,
                    amount=amount
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"M-Pesa subscription error: {e}")
            return {'success': False, 'message': str(e)}
    
    def save_mpesa_transaction(self, transaction_data):
        """Save M-Pesa transaction to database"""
        self.db.save_mpesa_transaction(transaction_data)
    
    def update_mpesa_transaction(self, checkout_id, update_data):
        """Update M-Pesa transaction status"""
        self.db.update_mpesa_transaction(checkout_id, update_data)
    
    def save_pending_subscription(self, user_id, checkout_request_id, plan_type, billing_cycle, amount):
        """Save pending subscription linked to M-Pesa transaction"""
        self.db.save_pending_subscription({
            'user_id': user_id,
            'checkout_request_id': checkout_request_id,
            'plan_type': plan_type,
            'billing_cycle': billing_cycle,
            'amount': amount,
            'status': 'pending'
        })
    
    def process_subscription_from_mpesa(self, checkout_request_id):
        """Activate subscription after successful M-Pesa payment"""
        try:
            # Get pending subscription
            subscription = self.db.get_pending_subscription(checkout_request_id)
            
            if not subscription:
                self.logger.error(f"No pending subscription for {checkout_request_id}")
                return
            
            user = self.db.get_user_by_id(subscription['user_id'])
            
            # Activate subscription
            from models.user import SubscriptionTier
            from datetime import timedelta
            
            tier = SubscriptionTier.PRO if subscription['plan_type'] == 'pro' else SubscriptionTier.ENTERPRISE
            user.subscription_tier = tier
            user.subscription_start = datetime.utcnow()
            
            if subscription['billing_cycle'] == 'monthly':
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
            else:
                user.subscription_end = datetime.utcnow() + timedelta(days=365)
            
            self.db.update_user(user)
            
            # Update subscription status
            self.db.update_pending_subscription(checkout_request_id, {'status': 'completed'})
            
            self.logger.info(f"Subscription activated for user {user.id} via M-Pesa")
            
        except Exception as e:
            self.logger.error(f"Subscription activation error: {e}")
    
    def get_pochi_payment_instructions(self, amount, plan_type):
        """
        Get manual Pochi la Biashara payment instructions
        For customers who prefer manual payment
        """
        return {
            'method': 'Pochi la Biashara',
            'business_number': self.pochi_number,
            'business_name': 'Trading Bot Kenya',
            'amount': amount,
            'plan': plan_type,
            'instructions': [
                f"1. Go to M-Pesa on your phone",
                f"2. Select 'Lipa na M-Pesa'",
                f"3. Select 'Pay Bill' or 'Buy Goods and Services'",
                f"4. Enter Business Number: {self.pochi_number}",
                f"5. Enter Amount: KES {amount}",
                f"6. Enter Account Number: Your Email or Phone",
                f"7. Enter your M-Pesa PIN",
                f"8. Confirm payment",
                f"9. You will receive confirmation SMS",
                f"10. Send the M-Pesa code to support for activation"
            ],
            'support_contact': '+254718982047',
            'note': 'Please send your M-Pesa confirmation message to our number for manual verification and account activation.'
        }
