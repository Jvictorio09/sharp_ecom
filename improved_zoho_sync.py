"""
IMPROVED ZOHO SYNC CODE
Replace the sync_to_zoho function in views.py with this better version.
"""

import logging
log = logging.getLogger(__name__)

# BETTER VERSION - Add to views.py around line 1420
def improved_sync_to_zoho():
    """
    Improved Zoho sync with proper logging and error handling.
    """
    try:
        log.info(f"🚀 Starting Zoho sync for order {order.order_number}")
        push_order_to_zoho(order)
        log.info(f"✅ Zoho sync SUCCESS for {order.order_number}")
        
    except Exception as e:
        # Log the full error with traceback
        log.error(
            f"❌ ZOHO SYNC FAILED for {order.order_number}: {str(e)}", 
            exc_info=True,
            extra={
                'order_number': order.order_number,
                'order_id': order.id,
                'error_type': type(e).__name__
            }
        )
        
        # Optional: Store error in shipping_address for visibility
        try:
            addr = dict(order.shipping_address or {})
            addr['_zoho_sync_error'] = {
                'error': str(e),
                'type': type(e).__name__,
                'timestamp': timezone.now().isoformat()
            }
            order.shipping_address = addr
            order.save(update_fields=['shipping_address'])
        except:
            pass

