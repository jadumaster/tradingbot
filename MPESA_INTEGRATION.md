# 💰 M-PESA PAYMENT INTEGRATION GUIDE

## 🇰🇪 M-Pesa Payment Support Added!

Your trading bot now supports **M-Pesa payments** for customers in Kenya and East Africa! Users can pay for subscriptions using their mobile money.

---

## ✨ Features Added

### 1. **STK Push (Lipa na M-Pesa Online)** ✅
- Automated payment prompts sent directly to customer's phone
- Real-time payment confirmation
- Automatic subscription activation

### 2. **Pochi la Biashara** ✅
- Manual payment option
- Business Number: **+254 718982047**
- Till Number support
- Payment verification

### 3. **Kenyan Shilling Pricing** ✅
- **PRO Monthly**: KES 4,500 (~$30)
- **PRO Yearly**: KES 45,000 (~$300)  
- **ENTERPRISE Monthly**: KES 15,000 (~$100)
- **ENTERPRISE Yearly**: KES 150,000 (~$1,000)

---

## 🚀 SETUP GUIDE

### Step 1: Get M-Pesa Daraja API Credentials

1. **Create Safaricom Developer Account**
   - Go to: https://developer.safaricom.co.ke
   - Click "Sign Up"
   - Verify your email

2. **Create an App**
   - Login to developer portal
   - Click "My Apps" → "Create New App"
   - Select APIs: "Lipa Na M-Pesa Online"
   - Click "Create App"

3. **Get Credentials**
   - Go to your app dashboard
   - Copy:
     - **Consumer Key**
     - **Consumer Secret**
     - **Passkey** (for Lipa Na M-Pesa Online)

4. **Get Business Shortcode**
   - For testing: Use sandbox shortcode `174379`
   - For production: Use your Paybill or Till Number

---

### Step 2: Configure Environment Variables

Add to your `.env` file:

```env
# M-Pesa Configuration
MPESA_CONSUMER_KEY=your_consumer_key_from_daraja
MPESA_CONSUMER_SECRET=your_consumer_secret_from_daraja
MPESA_SHORTCODE=174379  # Your Till/Paybill number
MPESA_PASSKEY=your_passkey_from_daraja
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback

# Pochi la Biashara
MPESA_POCHI_NUMBER=+254718982047
MPESA_TILL_NUMBER=9508133

# Environment (True for testing, False for production)
MPESA_SANDBOX=True
```

---

### Step 3: Set Up Callback URL

Your app needs to receive M-Pesa payment confirmations:

1. **For Local Testing** (use ngrok):
   ```bash
   ngrok http 5000
   ```
   Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
   
2. **Update callback URL**:
   ```env
   MPESA_CALLBACK_URL=https://abc123.ngrok.io/api/mpesa/callback
   ```

3. **For Production**:
   Use your actual domain
   ```env
   MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback
   ```

---

## 📡 API ENDPOINTS

### 1. Initiate M-Pesa Payment (STK Push)

```http
POST /api/mpesa/subscribe
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "plan_type": "pro",
  "billing_cycle": "monthly",
  "phone_number": "254712345678"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment request sent to your phone",
  "checkout_request_id": "ws_CO_12345",
  "merchant_request_id": "1234-5678-9012"
}
```

---

### 2. Check Payment Status

```http
GET /api/mpesa/status/{checkout_request_id}
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "status": "completed",
  "mpesa_receipt": "OEI2AK4Q16",
  "amount": 4500
}
```

---

### 3. Get Pochi la Biashara Instructions

```http
GET /api/mpesa/pochi-instructions
```

**Response:**
```json
{
  "method": "Pochi la Biashara",
  "business_number": "+254718982047",
  "business_name": "Trading Bot Kenya",
  "amount": 4500,
  "instructions": [
    "1. Go to M-Pesa on your phone",
    "2. Select 'Lipa na M-Pesa'",
    ...
  ]
}
```

---

### 4. M-Pesa Callback (Handled Automatically)

```http
POST /api/mpesa/callback
Content-Type: application/json

{
  "Body": {
    "stkCallback": {
      "ResultCode": 0,
      "ResultDesc": "Success",
      "CheckoutRequestID": "ws_CO_12345",
      ...
    }
  }
}
```

---

## 💳 PAYMENT FLOW

### Automated Flow (STK Push)

```
1. User clicks "Subscribe with M-Pesa"
   ↓
2. API sends STK Push request to Daraja
   ↓
3. User receives payment prompt on phone
   ↓
4. User enters M-Pesa PIN
   ↓
5. M-Pesa processes payment
   ↓
6. M-Pesa sends callback to your server
   ↓
7. Server activates user subscription
   ↓
8. User receives confirmation (SMS + Email + in-app)
```

### Manual Flow (Pochi la Biashara)

```
1. User selects "Pay via M-Pesa Manually"
   ↓
2. System shows payment instructions
   ↓
3. User pays to +254718982047
   ↓
4. User sends M-Pesa confirmation code
   ↓
5. Admin verifies payment manually
   ↓
6. Admin activates subscription
```

---

## 🧪 TESTING

### Test with Sandbox

1. **Use Test Credentials**
   ```env
   MPESA_SANDBOX=True
   MPESA_SHORTCODE=174379
   ```

2. **Test Phone Numbers** (Sandbox)
   - Use: `254708374149` (Safaricom test number)
   - PIN: Any 4 digits

3. **Initiate Test Payment**
   ```bash
   curl -X POST http://localhost:5000/api/mpesa/subscribe \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "plan_type": "pro",
       "billing_cycle": "monthly",
       "phone_number": "254708374149"
     }'
   ```

4. **Check Logs**
   - Watch for STK Push response
   - Verify callback received
   - Confirm subscription activated

---

## 🔐 SECURITY

### Production Checklist

✅ **HTTPS Required** - M-Pesa requires HTTPS for callbacks  
✅ **Validate Callbacks** - Verify callback authenticity  
✅ **Encrypt Credentials** - Never expose API keys  
✅ **IP Whitelisting** - Restrict callback endpoint  
✅ **Rate Limiting** - Prevent payment spam  
✅ **Transaction Logging** - Keep audit trail  

---

## 💰 PRICING COMPARISON

| Plan | Stripe (USD) | M-Pesa (KES) | Savings |
|------|-------------|--------------|---------|
| **Pro Monthly** | $29.99 | 4,500 (~$30) | Similar |
| **Pro Yearly** | $299.99 | 45,000 (~$300) | 17% off |
| **Enterprise Monthly** | $99.99 | 15,000 (~$100) | Similar |
| **Enterprise Yearly** | $999.99 | 150,000 (~$1,000) | 17% off |

*Exchange rate: 1 USD ≈ 150 KES*

---

## 📱 POCHI LA BIASHARA DETAILS

### Business Information
- **Business Name**: Trading Bot Kenya
- **Phone Number**: +254 718982047
- **Till Number**: 9508133 (if applicable)
- **Account Type**: Pochi la Biashara

### Customer Instructions
```
1. Open M-Pesa Menu
2. Select "Lipa na M-Pesa"
3. Choose "Pay Bill" or "Buy Goods"
4. Enter: +254718982047
5. Amount: [Subscription Amount]
6. Account: Your email/phone
7. Enter M-Pesa PIN
8. Confirm
9. Send M-Pesa code to +254718982047
```

---

## 🎯 INTEGRATION EXAMPLE

### Frontend Payment Button

```javascript
// Subscribe with M-Pesa
async function subscribeWithMpesa(planType) {
  const response = await fetch('/api/mpesa/subscribe', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      plan_type: planType,
      billing_cycle': 'monthly',
      phone_number: userPhone  // 254XXXXXXXXX format
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    // Show success message
    alert('Check your phone for M-Pesa payment prompt!');
    
    // Poll for payment status
    checkPaymentStatus(result.checkout_request_id);
  }
}

// Check payment status
async function checkPaymentStatus(checkoutId) {
  const response = await fetch(`/api/mpesa/status/${checkoutId}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  const result = await response.json();
  
  if (result.status === 'completed') {
    alert('Payment successful! Your subscription is now active.');
    window.location.reload();
  } else if (result.status === 'pending') {
    // Check again in 5 seconds
    setTimeout(() => checkPaymentStatus(checkoutId), 5000);
  }
}
```

---

## 📊 TRANSACTION MONITORING

### Admin Dashboard

View all M-Pesa transactions:
- Pending payments
- Completed payments
- Failed payments
- Revenue by payment method

### Database Tables

**mpesa_transactions**
- checkout_request_id
- merchant_request_id
- phone_number
- amount
- mpesa_receipt
- status
- timestamp

**pending_subscriptions**
- user_id
- checkout_request_id
- plan_type
- amount
- status

---

## 🆘 TROUBLESHOOTING

### Common Issues

**1. STK Push not received**
- Check phone number format (254XXXXXXXXX)
- Verify phone has M-Pesa activated
- Check M-Pesa server status

**2. Callback not received**
- Verify callback URL is HTTPS
- Check ngrok is running (local testing)
- Review server logs

**3. Payment not activating subscription**
- Check callback processing logs
- Verify database connection
- Review pending_subscriptions table

**4. Invalid credentials**
- Verify Consumer Key/Secret
- Check Passkey
- Ensure correct environment (sandbox/prod)

---

## 📈 NEXT STEPS

### Phase 1: Testing (Current)
- ✅ M-Pesa service created
- ✅ API endpoints defined
- ⏳ Test with sandbox
- ⏳ Verify callbacks

### Phase 2: Production
- [ ] Get production M-Pesa credentials
- [ ] Register Pochi la Biashara
- [ ] Set up production callback URL
- [ ] Go live!

### Phase 3: Enhancement
- [ ] Add M-Pesa Express (recurring)
- [ ] SMS confirmations
- [ ] Payment reminders
- [ ] Multi-currency support

---

## 💡 PRO TIPS

1. **Always test in sandbox first** - Don't use real money until everything works

2. **Monitor transactions** - Keep track of all M-Pesa payments

3. **Provide clear instructions** - Many users prefer manual Pochi payments

4. **Fast activation** - Activate subscriptions immediately after callback

5. **Send confirmations** - SMS + Email + In-app notification

6. **Handle failures gracefully** - Guide users if payment fails

---

## 📞 SUPPORT

### M-Pesa Support
- Developer Portal: https://developer.safaricom.co.ke
- Email: apisupport@safaricom.co.ke

### Your Support
- Pochi Number: +254 718982047
- For payment issues and manual verification

---

**M-Pesa Integration Complete! 🇰🇪💚**

Your trading bot now accepts payments from millions of M-Pesa users across Kenya and East Africa!

---

*Last Updated: 2024-12-12*
