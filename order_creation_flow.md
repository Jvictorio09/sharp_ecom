# Order Creation Flow - System Components

## 📋 Overview
When a customer places an order through checkout, the system touches multiple components in a specific sequence. Here's the complete breakdown:

---

## 🔄 Order Creation Process

### 1️⃣ **Checkout View (`myApp/views.py` - `checkout()` function)**
   - **Location:** Line 1220
   - **Method:** POST request from checkout form
   - **Triggered by:** Customer submitting checkout form

### 2️⃣ **Form Data Collection & Validation**
   Components touched:
   - Customer contact info (name, phone, email)
   - Shipping address (country-aware validation)
   - Payment method selection
   - Shipping method
   - Promo code validation (if applied)
   - Phone validation (E.164 format)
   - Country enforcement (Middle East + USA)

### 3️⃣ **Database Transaction (`transaction.atomic()`)**
   
   **a) Order Creation:**
   - **Model:** `Order` (`myApp/models.py` - Line 100)
   - **Action:** `Order.objects.create(**order_kwargs)` (Line 1377)
   - **Auto-generated:** Unique order number via `generate_order_number()`
   - **Stored data:**
     - Customer info (name, phone, email)
     - Shipping address (JSON + text fields)
     - Country code
     - Subtotal, shipping cost, discount
     - Payment & shipping method
     - Status (defaults to "0" - Created)
   
   **b) Order Items Creation:**
   - **Model:** `OrderItem` (`myApp/models.py` - Line 173)
   - **Action:** `OrderItem.objects.create()` for each cart item (Line 1384-1391)
   - **Stored data:**
     - Product reference
     - Product name (snapshot)
     - Unit price (snapshot)
     - Quantity
     - Line total
   
   **c) Promo Code Usage Update (if applicable):**
   - **Model:** `PromoCode` (`myApp/models.py` - Line 285)
   - **Action:** Increment `used_count` or `usage_count` (Line 1394-1404)

### 4️⃣ **Wassel Shipment Creation**
   - **Function:** `_create_wassel_shipment_for_order()` (Line 1406)
   - **Location:** `myApp/views.py` - Line 469
   - **Action:** 
     - Creates shipment with Wassel courier API
     - Generates AWB (Air Waybill) number
     - Stores AWB in `order.shipping_address._carrier.awb`
     - Saves payload snapshot for debugging
   - **Idempotent:** Checks if AWB already exists

### 5️⃣ **Cart Cleanup**
   - **Action:** Clear cart from session (Line 1414)
   - **Storage:** `request.session[CART_KEY] = {}`
   - **Purpose:** Prevent duplicate orders

### 6️⃣ **Post-Commit Background Tasks**
   
   **a) Email Notifications (Async):**
   - **Function:** `_send_emails_async()` (Line 1418)
   - **Runs in:** Background thread (daemon)
   - **Sends:**
     1. **Customer Confirmation Email:**
        - Function: `_email_order_confirmation()` (Line 1696)
        - Template: `emails/order_confirmation.txt` + `.html`
        - To: Customer email
        - Subject: "Your SHARP Order {order_number}"
        - Provider: Resend API (via `_safe_send_mail()`)
     
     2. **Admin New Order Email:**
        - Function: `_email_admin_new_order()` (Line 1732)
        - Template: `emails/admin_new_order.txt`
        - To: Admin email (from settings)
        - Purpose: Notify admin of new order

   **b) Zoho Inventory Integration (Async):**
   - **Function:** `push_order_to_zoho()` (Line 1419)
   - **Location:** `myApp/integrations/zoho_inventory.py` - Line 308
   - **Process:**
     1. **Ensure/Create Customer Contact in Zoho:**
        - Search by email or name
        - Create if not exists
        - Store shipping/billing addresses
     
     2. **Create Sales Order in Zoho:**
        - Reference: Our order number
        - Line items: Products with SKUs
        - Handles bundles (composite items)
     
     3. **Confirm Sales Order**
     
     4. **Convert to Invoice:**
        - Deducts stock from inventory
        - Creates invoice with line items
     
     5. **Record Payment (if AUTO_MARK_PAID=True):**
        - Payment mode: "Cash" (COD) or "Online"
        - Links payment to invoice

### 7️⃣ **Success Response**
   - **Messages:** Success message to user (Line 1421)
   - **Redirect:** `/thanks/?o={order_number}` (Line 1422)
   - **Display:** Thank you page with order details

---

## 📦 Models Involved

### **Order** (`myApp/models.py`)
- **Fields touched:**
  - `order_number` (auto-generated)
  - `created_at`, `updated_at` (auto timestamps)
  - `full_name`, `phone`, `email`
  - `address_line1`, `city`, `province`, `zip_code`
  - `country`, `shipping_address` (JSON), `shipping_address_text`
  - `shipping_method`, `payment_method`
  - `subtotal`, `shipping_cost`, `discount_total`
  - `notes`, `status`

### **OrderItem** (`myApp/models.py`)
- **Fields touched:**
  - `order` (FK to Order)
  - `product` (FK to Product)
  - `name` (snapshot)
  - `unit_price` (snapshot)
  - `quantity`
  - `line_total`

### **PromoCode** (`myApp/models.py`)
- **Fields touched:**
  - `used_count` or `usage_count` (incremented)

---

## 🔗 External Integrations

### 1. **Wassel Courier API**
- **Purpose:** Create shipment & get AWB
- **Endpoint:** Wassel API
- **Credentials:** From `settings.WASSEL`
- **Data stored:** AWB number in order JSON field

### 2. **Zoho Inventory API**
- **Purpose:** Sync order, create invoice, deduct stock
- **Endpoints:**
  - `/contacts` - Create/find customer
  - `/salesorders` - Create sales order
  - `/salesorders/{id}/status/confirmed` - Confirm SO
  - `/invoices` - Convert SO to invoice
  - `/customerpayments` - Record payment
- **Credentials:** From environment/settings
  - `ZOHO_CLIENT_ID`
  - `ZOHO_CLIENT_SECRET`
  - `ZOHO_REFRESH_TOKEN`
  - `ZOHO_ORG_ID`

### 3. **Resend Email API**
- **Purpose:** Send transactional emails
- **Endpoints:** Resend API
- **Credentials:** From `settings.RESEND`
- **Templates used:**
  - `emails/order_confirmation.txt` & `.html`
  - `emails/admin_new_order.txt`

---

## 🎯 Summary: Touch Points

| Component | Action | Timing |
|-----------|--------|--------|
| **Session** | Clear cart | Immediate |
| **Database - Order** | Create order record | Immediate (transaction) |
| **Database - OrderItem** | Create line items | Immediate (transaction) |
| **Database - PromoCode** | Increment usage | Immediate (transaction) |
| **Wassel API** | Create shipment | After transaction |
| **Zoho API** | Create SO/Invoice/Payment | After transaction (async) |
| **Email - Customer** | Order confirmation | After transaction (async) |
| **Email - Admin** | New order notification | After transaction (async) |
| **User Session** | Success message & redirect | Immediate |

---

## ⚙️ Configuration Dependencies

### Settings (`myProject/settings.py`)
- `WASSEL` dict (courier integration)
- `ZOHO` dict (inventory integration)
- `RESEND` dict (email integration)
- `DEFAULT_FROM_EMAIL`
- `ADMIN_ORDER_EMAIL`
- `CONTACT_RECEIVER_EMAIL`

### Environment Variables
- `ZOHO_CLIENT_ID`
- `ZOHO_CLIENT_SECRET`
- `ZOHO_REFRESH_TOKEN`
- `ZOHO_ORG_ID`
- `ZOHO_BASE`
- `RESEND_API_KEY`
- `RESEND_FROM`
- `WASSEL_EMAIL`
- `WASSEL_PASSWORD`
- `WASSEL_COMPANY_STORE_ID`

---

## 🚨 Error Handling

### Transactional Errors
- **Scope:** Order & OrderItem creation
- **Behavior:** Rollback entire transaction
- **User impact:** Error message, no order created

### Non-Blocking Errors (Caught & Logged)
- **Email failures:** Order still created, warning shown
- **Zoho failures:** Order still created, logged
- **Wassel failures:** Order created, warning message shown

### Idempotency
- **AWB creation:** Checks if already exists before creating
- **Zoho sync:** Can be retried manually if needed

---

## 📊 Data Flow Diagram

```
Customer Checkout Form
         ↓
    [Validation]
         ↓
  [Database Transaction]
    ├─ Create Order
    ├─ Create OrderItems  
    └─ Update PromoCode
         ↓
  [Wassel Shipment] → Store AWB
         ↓
   [Clear Cart]
         ↓
[Transaction Commit]
         ↓
    [Async Tasks]
    ├─ Customer Email
    ├─ Admin Email
    └─ Zoho Sync
        ├─ Create Contact
        ├─ Create Sales Order
        ├─ Confirm SO
        ├─ Create Invoice
        └─ Record Payment
         ↓
   [Success Page]
```

---

## 🔍 File References

- **Main checkout logic:** `myApp/views.py` (Line 1220-1422)
- **Order model:** `myApp/models.py` (Line 100-169)
- **OrderItem model:** `myApp/models.py` (Line 173-183)
- **Zoho integration:** `myApp/integrations/zoho_inventory.py` (Line 308-355)
- **Email templates:** `templates/emails/`
- **Settings:** `myProject/settings.py`


