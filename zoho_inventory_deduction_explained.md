# Zoho Inventory Deduction - Deep Dive

## 🎯 Overview
Inventory deduction in Zoho happens **automatically when an Invoice is created**. Our system creates invoices from Sales Orders during the order creation process.

---

## 🔄 The Inventory Deduction Pipeline

### **Step-by-Step Process:**

```
Order Created → Zoho Sync → Sales Order → Invoice → INVENTORY DEDUCTED ✅
```

### **Detailed Flow:**

#### **1️⃣ Order Creation in Our System**
**Location:** `myApp/views.py` - Line 1377
```python
order = Order.objects.create(**order_kwargs)
OrderItem.objects.create(order=order, product=p, quantity=qty, ...)
```

**What's stored:**
- Product SKU
- Product name
- Quantity ordered
- Unit price (snapshot)

#### **2️⃣ Async Zoho Sync Triggered**
**Location:** `myApp/views.py` - Line 1419
```python
transaction.on_commit(lambda: push_order_to_zoho(order))
```

**Why async?** 
- Doesn't block customer checkout
- Runs in background after order is saved
- Failures don't prevent order creation

---

## 📦 Zoho Inventory Deduction Mechanism

### **The Critical Function:** `push_order_to_zoho()`
**Location:** `myApp/integrations/zoho_inventory.py` - Line 308

### **5-Stage Pipeline:**

#### **Stage 1: Customer Contact Creation/Lookup**
**Function:** `_ensure_customer(order)` - Line 192

**Parts Touched:**
- **Zoho API:** `GET /contacts?email={email}` or `GET /contacts?contact_name={name}`
- **If not found:** `POST /contacts` with customer data

**Data Sent:**
```json
{
  "contact_name": "Customer Name",
  "contact_type": "customer",
  "email": "customer@example.com",
  "phone": "+123456789",
  "shipping_address": {...},
  "billing_address": {...}
}
```

**Result:** `contact_id` (used in subsequent calls)

---

#### **Stage 2: Sales Order Creation**
**Function:** `_create_sales_order()` - Line 242

**Parts Touched:**
- **Our Database:** Reads `Order` and `OrderItem` records
- **Zoho API:** `POST /salesorders`

**Critical Function:** `_line_items(order)` - Line 146
**Purpose:** Converts our order items to Zoho format

**How it works:**

```python
# For each item in the order:
for line in order.items.select_related("product"):
    p = line.product
    qty = float(line.quantity)
    
    # Build Zoho line item
    out.append({
        "sku": p.sku,           # ← CRITICAL: SKU must match Zoho item
        "name": p.name,
        "item_id": None,        # Zoho will look up by SKU
        "quantity": qty,        # ← This quantity will be deducted
        "rate": float(line.unit_price)
    })
```

**Data Sent to Zoho:**
```json
{
  "customer_id": "123456789",
  "reference_number": "ORD-ABC123",
  "date": "2025-10-13",
  "line_items": [
    {
      "sku": "SHARP-SHARPSHAMPOO-31",
      "name": "Sharp Shampoo",
      "quantity": 2.0,
      "rate": 15.00
    }
  ]
}
```

**What Zoho Does:**
1. Looks up item by SKU
2. Gets internal `item_id`
3. Creates Sales Order with line items
4. **NO STOCK DEDUCTION YET** (just a draft order)

**Result:** Sales Order ID (e.g., `SO-123456`)

---

#### **Stage 3: Confirm Sales Order**
**Function:** `_confirm_sales_order(so_id)` - Line 260

**Parts Touched:**
- **Zoho API:** `POST /salesorders/{id}/status/confirmed`

**What This Does:**
- Changes SO status from "Draft" to "Confirmed"
- Makes it visible in Zoho dashboard
- Prepares it for invoicing
- **STILL NO STOCK DEDUCTION**

---

#### **Stage 4: Convert to Invoice** ⚡ **INVENTORY DEDUCTION HAPPENS HERE**
**Function:** `_convert_so_to_invoice(so_id, customer_id)` - Line 297

**Parts Touched:**

1. **Fetch Sales Order:**
   - `GET /salesorders/{so_id}` → Gets SO with Zoho's `item_id` values

2. **Build Invoice Payload:**
   **Function:** `_so_to_invoice_payload()` - Line 266
   
   **Critical Detail:** Uses `item_id` from Sales Order (not SKU)
   
   ```python
   for li in so.get("line_items"):
       items.append({
           "item_id": li.get("item_id"),      # ← Zoho's internal ID
           "quantity": float(li.get("quantity")),  # ← Amount to deduct
           "salesorder_item_id": li.get("line_item_id")
       })
   ```

3. **Create Invoice:**
   - **Zoho API:** `POST /invoices`
   
   **Payload:**
   ```json
   {
     "customer_id": "123456789",
     "salesorder_id": "SO-123456",
     "line_items": [
       {
         "item_id": "987654321",           // Zoho's item ID
         "quantity": 2.0,                  // Deduct 2 units
         "salesorder_item_id": "SO_ITEM_123"
       }
     ]
   }
   ```

**🎯 WHAT ZOHO DOES NOW (THE MAGIC):**

1. **Validates** item exists and has sufficient stock
2. **Creates** the invoice document
3. **DEDUCTS** the quantity from item's `stock_on_hand`
   - Example: Item had 1500 units → Now has 1498 units
4. **Records** the stock movement in inventory history
5. **Links** invoice to original Sales Order

**For Bundles/Composite Items:**
- If item is configured as "Composite Item" in Zoho
- Zoho automatically deducts component stock based on bundle formula
- Example: "Full Package" bundle = 1 Shampoo + 1 Conditioner + 1 Oil
  - Selling 1 bundle deducts: 1 shampoo, 1 conditioner, 1 oil

**Result:** Invoice ID (e.g., `INV-123456`)

---

#### **Stage 5: Record Payment (Optional)**
**Function:** Inline in `push_order_to_zoho()` - Line 339
**Controlled by:** `AUTO_MARK_PAID = True` (Line 11)

**Parts Touched:**
- **Zoho API:** `POST /customerpayments`

**Data Sent:**
```json
{
  "customer_id": "123456789",
  "payment_mode": "Cash",  // or "Online"
  "amount": 30.00,
  "invoices": [
    {
      "invoice_id": "INV-123456",
      "amount_applied": 30.00
    }
  ]
}
```

**What This Does:**
- Marks invoice as "Paid"
- Records payment in accounting
- **Does NOT affect inventory** (already deducted in Stage 4)

---

## 🔧 Components Touched for Inventory Deduction

### **Our System:**
1. **Order Model** (`myApp/models.py`)
   - Fields read: `order_number`, `full_name`, `email`, `phone`, shipping address
   
2. **OrderItem Model** (`myApp/models.py`)
   - Fields read: `product` (FK), `quantity`, `unit_price`
   
3. **Product Model** (`myApp/models.py`)
   - Fields read: `sku`, `name`, `price`, `is_bundle`

4. **ProductComponent Model** (if bundles)
   - Fields read: `component` (FK), `quantity` (per bundle)

### **Zoho Inventory System:**

1. **Items Table**
   - **Field Modified:** `stock_on_hand` (decremented by quantity)
   - **Field Modified:** `actual_available_stock` (if tracked separately)
   - **Lookup Method:** By SKU → gets `item_id`

2. **Stock History/Movements**
   - New record created showing:
     - Item ID
     - Quantity change (-2)
     - Reference: Invoice number
     - Date/time
     - Warehouse (if multi-warehouse)

3. **Invoices Table**
   - New invoice record created
   - Status: "Sent" or "Paid" (if payment recorded)

4. **Sales Orders Table**
   - Status updated to "Invoiced"
   - Linked to invoice

5. **Contacts Table**
   - Customer record (created or updated)

---

## 🔍 Critical Requirements for Deduction to Work

### **1. SKU Matching** ⚠️ MOST IMPORTANT
- Product SKU in our database **MUST** match Item SKU in Zoho
- Case-sensitive matching
- Example: `SHARP-SHARPSHAMPOO-31` (both systems)

**Check this:**
```sql
-- Our database
SELECT sku, name FROM myApp_product;

-- Compare with Zoho
GET /items?sku=SHARP-SHARPSHAMPOO-31
```

### **2. Item Must Exist in Zoho**
- Item must be created in Zoho Inventory first
- Can't invoice items that don't exist
- Error if SKU not found: "Item not found"

### **3. Sufficient Stock**
- Zoho checks available stock before invoicing
- If stock < quantity, may fail or allow negative stock (based on settings)
- Your Zoho setting controls this behavior

### **4. Proper Item Configuration**
**For Simple Items:**
- Must have `track_inventory = true` in Zoho
- Must have warehouse assigned

**For Bundles (Composite Items):**
- Must be configured as "Composite Item" in Zoho
- Components must be linked with quantities
- Example: Full Package contains:
  - 1× Sharp Shampoo
  - 1× Sharp Conditioner
  - 1× Sharp Treatment Oil

### **5. Zoho Credentials Valid**
- Access token must be valid
- Organization ID correct
- Proper permissions (create invoices, manage inventory)

---

## 🎯 Bundle Inventory Deduction

**Current Setting:** `EXPLODE_BUNDLES = False` (Line 16)

**How it works:**

### **Option 1: Send Bundle as Single Item (Current)**
```python
{
  "sku": "SHARP-FULLPACKAGE-23",  // Bundle SKU
  "quantity": 1,
  "description": "Includes: 1× Shampoo; 1× Conditioner; 1× Oil"
}
```

**Zoho's Behavior:**
- Receives bundle SKU
- Looks up composite item configuration
- **Automatically deducts component stock** based on formula
- 1 bundle sold → deducts 1 shampoo, 1 conditioner, 1 oil
- Bundle's `stock_on_hand` might be calculated or tracked separately

### **Option 2: Explode Bundle (If EXPLODE_BUNDLES = True)**
```python
[
  {"sku": "SHARP-SHARPSHAMPOO-31", "quantity": 1},
  {"sku": "SHARP-SHARPCONDITI-32", "quantity": 1},
  {"sku": "SHARP-SHARPTREATME-33", "quantity": 1}
]
```

**Zoho's Behavior:**
- Receives 3 separate items
- Deducts each component individually
- Doesn't track as bundle sale

**Recommended:** Option 1 (current setup) for proper bundle tracking

---

## ✅ How to Verify Inventory Deduction Works

### **Method 1: Check Zoho Dashboard**
1. Log into Zoho Inventory
2. Go to **Items** → Select an item
3. Note current **Stock on Hand**
4. Place test order for that item
5. Wait for sync (few seconds)
6. Refresh item page
7. **Stock on Hand should be decreased**

### **Method 2: Check via API (Automated)**
See the verification script below

### **Method 3: Check Zoho Reports**
1. Go to **Reports** → **Stock Summary**
2. View stock movements
3. Filter by item and date
4. Should see invoice-based deduction

### **Method 4: Check Invoice in Zoho**
1. Go to **Sales** → **Invoices**
2. Find invoice by your order number (reference field)
3. Open invoice
4. Verify line items and quantities
5. Check invoice status (should be "Paid" if AUTO_MARK_PAID=True)

---

## 🚨 Common Issues & Troubleshooting

### **Issue 1: Stock Not Deducting**

**Possible Causes:**
- ✗ SKU mismatch (most common)
- ✗ Item doesn't exist in Zoho
- ✗ Item has `track_inventory = false`
- ✗ Zoho sync failed silently
- ✗ Invoice creation failed

**How to Check:**
```python
# Run the verification script (see below)
python verify_inventory_deduction.py
```

### **Issue 2: Wrong Quantity Deducted**

**Causes:**
- Bundle component quantities wrong in Zoho
- Quantity calculation error in `_line_items()`
- Multiple sync attempts

### **Issue 3: Negative Stock Allowed**

**Cause:**
- Zoho setting: "Allow negative stock" is enabled
- Not necessarily a problem, but worth monitoring

**Check in Zoho:**
Settings → Preferences → Items → Allow negative stock

### **Issue 4: Sync Errors**

**Check logs:**
```python
# In views.py, line 354
log.exception("Zoho push failed for %s", order.order_number)
```

**Common errors:**
- Authentication failed → Refresh token expired
- Item not found → SKU mismatch
- Insufficient stock → Need to restock

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ ORDER CREATED                                               │
│ Order: ORD-ABC123                                           │
│ Item: Sharp Shampoo (SKU: SHARP-SHARPSHAMPOO-31)          │
│ Qty: 2                                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ZOHO SYNC TRIGGERED (Async)                                 │
│ Function: push_order_to_zoho(order)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Get/Create Customer Contact                        │
│ API: POST /contacts                                          │
│ Result: contact_id = "123456789"                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Create Sales Order                                 │
│ API: POST /salesorders                                       │
│ Payload: {                                                   │
│   "customer_id": "123456789",                               │
│   "line_items": [{                                          │
│     "sku": "SHARP-SHARPSHAMPOO-31",                        │
│     "quantity": 2                                           │
│   }]                                                         │
│ }                                                            │
│ ↓                                                            │
│ Zoho looks up SKU → finds item_id = "987654321"            │
│ Result: salesorder_id = "SO-00123"                         │
│                                                              │
│ Stock Status: UNCHANGED (1500 units)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: Confirm Sales Order                                │
│ API: POST /salesorders/SO-00123/status/confirmed            │
│ Result: SO status = "Confirmed"                             │
│                                                              │
│ Stock Status: UNCHANGED (1500 units)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: Create Invoice from SO  ⚡ DEDUCTION HAPPENS       │
│ API: POST /invoices                                          │
│ Payload: {                                                   │
│   "salesorder_id": "SO-00123",                              │
│   "line_items": [{                                          │
│     "item_id": "987654321",  ← Zoho's internal ID          │
│     "quantity": 2                                           │
│   }]                                                         │
│ }                                                            │
│ ↓                                                            │
│ Zoho creates invoice INV-00456                              │
│ ↓                                                            │
│ 🎯 INVENTORY DEDUCTION:                                     │
│    Item "987654321" stock: 1500 - 2 = 1498                 │
│                                                              │
│ Result: invoice_id = "INV-00456"                            │
│                                                              │
│ Stock Status: DEDUCTED ✅ (1498 units)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: Record Payment                                     │
│ API: POST /customerpayments                                  │
│ Result: Invoice marked as "Paid"                            │
│                                                              │
│ Stock Status: UNCHANGED (1498 units)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security & Reliability

### **Error Handling:**
- All Zoho operations wrapped in try/except
- Failures logged but don't block order creation
- Customer still receives order confirmation

### **Idempotency:**
- No built-in duplicate prevention
- If function runs twice, creates 2 invoices → deducts twice ⚠️
- Solution: Add order tracking field for Zoho invoice ID

### **Retry Logic:**
- Not automatic
- Can manually retry from admin panel or script
- Should implement: Store `zoho_invoice_id` on Order model

---

## 📝 Summary

**Inventory Deduction Happens When:**
→ Invoice is created in Zoho (Stage 4)

**Critical Path:**
1. Our Order → 2. Sales Order → 3. Confirm → **4. Invoice (DEDUCT)** → 5. Payment

**Parts Touched:**
- Our DB: Order, OrderItem, Product models
- Zoho API: /contacts, /salesorders, /invoices, /customerpayments
- Zoho Inventory: Item stock_on_hand field

**Verification:**
- Check Zoho dashboard stock levels
- Use API to query before/after
- Check invoice creation in Zoho
- Review stock movement history

**Key Success Factors:**
✅ SKU matching between systems
✅ Items exist and configured in Zoho
✅ Track inventory enabled
✅ Valid API credentials
✅ Proper bundle/composite setup


