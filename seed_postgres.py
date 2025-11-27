#!/usr/bin/env python
"""
PostgreSQL Seed File
Generated on: 2025-11-25 04:05:40

This file contains all your data ready to be imported into PostgreSQL.
Run this file on your PostgreSQL database to seed it with all your data.

Usage:
    python seed_postgres.py

Or from Django shell:
    python manage.py shell
    >>> exec(open('seed_postgres.py').read())
    >>> seed_database()
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from myApp.models import (
    Product, Order, OrderItem, PromoCode, Post, PostBlock, 
    Subscriber, FxRate, ProductComponent
)

# ============================================================================
# DATA DEFINITIONS
# ============================================================================

PRODUCTS_DATA = [
    {
        "name": "Conditioner + Oil Duo",
        "sku": "SHARP-CONDITIONERO-40",
        "slug": "conditioner-oil-duo",
        "short_description": "Hydrate + polish",
        "description": "Weightless moisture with flyaway-taming control.",
        "price": 32.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Conditioner-_-Oil-Duo_leowiu.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698762/2_maw4et.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:21:56.213334+00:00"
    },
    {
        "name": "Conditioner + Sea Salt Duo",
        "sku": "SHARP-CONDITIONERS-42",
        "slug": "conditioner-sea-salt-duo",
        "short_description": "Hydrate + texture",
        "description": "Smooth detangle with beachy volume.",
        "price": 30.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Conditioner-_-Sea-Salt-Duo_kzhyaj.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:21:56.670926+00:00"
    },
    {
        "name": "Full Package",
        "sku": "SHARP-FULLPACKAGE-23",
        "slug": "full-package",
        "short_description": "Shampoo + Conditioner + Sea Salt + Oil",
        "description": "Our best-value set for clean, hydrated, textured hair with polished finish. Free delivery.",
        "price": 60.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Full-Package_jwpfyg.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698762/2_maw4et.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-08-30T16:14:14.091326+00:00"
    },
    {
        "name": "Sea Salt + Oil Duo",
        "sku": "SHARP-SEASALTOILDU-36",
        "slug": "sea-salt-oil-duo",
        "short_description": "Texture + polish",
        "description": "Matte grip with a glossy, controlled finish.",
        "price": 29.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Sea-Salt-_-Oil-Duo_vpjvpg.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698762/2_maw4et.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:18:36.168656+00:00"
    },
    {
        "name": "Shampoo + Conditioner + Oil Trio",
        "sku": "SHARP-SHAMPOOCONDI-37",
        "slug": "shampoo-conditioner-oil-trio",
        "short_description": "Cleanse, hydrate, finish",
        "description": "Balanced wash, smooth detangle, frizz control—your everyday glow-up.",
        "price": 50.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Shampoo-_-Conditioner-_-Oil-Trio_adoupx.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698762/2_maw4et.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:18:36.401752+00:00"
    },
    {
        "name": "Shampoo + Conditioner + Sea Salt Trio",
        "sku": "SHARP-SHAMPOOCONDI-38",
        "slug": "shampoo-conditioner-sea-salt-trio",
        "short_description": "Cleanse, hydrate, texture",
        "description": "Soft, healthy hair with natural volume and touchable grip.",
        "price": 50.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:18:36.620088+00:00"
    },
    {
        "name": "Shampoo + Conditioner Duo",
        "sku": "SHARP-SHAMPOOCONDI-35",
        "slug": "shampoo-conditioner-duo",
        "short_description": "Daily clean + weightless moisture",
        "description": "The everyday core routine. Gentle cleanse, smooth detangle, natural shine.",
        "price": 34.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986070/Shampoo-_-Conditioner-Duo_jcl7u4.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:18:35.954502+00:00"
    },
    {
        "name": "Shampoo + Oil Duo",
        "sku": "SHARP-SHAMPOOOILDU-39",
        "slug": "shampoo-oil-duo",
        "short_description": "Cleanse + polish",
        "description": "Balanced wash meets frizz control for a sleek finish.",
        "price": 32.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986070/Shampoo-_-Oil-Duo_lxqkql.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698762/2_maw4et.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:21:55.990160+00:00"
    },
    {
        "name": "Shampoo + Sea Salt Duo",
        "sku": "SHARP-SHAMPOOSEASA-41",
        "slug": "shampoo-sea-salt-duo",
        "short_description": "Cleanse + texture",
        "description": "Soft, healthy hair with natural volume and touchable grip.",
        "price": 30.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Shampoo-_-Sea-Salt-Duo_bchivy.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg",
        "is_bundle": true,
        "free_delivery": true,
        "created_at": "2025-09-01T04:21:56.423185+00:00"
    },
    {
        "name": "Sharp Conditioner",
        "sku": "SHARP-SHARPCONDITI-32",
        "slug": "sharp-conditioner",
        "short_description": "Coconut + Rice oils for deep hydration and smooth detangling.",
        "description": "Hydrating Conditioner\n\nDeeply hydrates and nourishes hair, smooths tangles, and improves softness and shine—without heaviness.\n\nHow to Use\n• After shampooing, apply to mid-lengths and ends.\n• Leave for 2–3 minutes, then rinse well.\n\nWhat It Does\n• Deep hydration and softness\n• Helps repair split ends; strengthens strands\n• Improves smoothness, shine, and manageability\n\nKey Ingredients\n• Coconut Oil — restores moisture; adds softness\n• Rice Oil — strengthens; enhances flexibility\n• Vitamins E & B5 — support hydration and protection\n",
        "price": 19.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/39fbf9e4-e3e0-488a-90cd-762f60351da7_elsobt.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698752/150ddba4-fcf1-4bd2-9443-b797e385de64_vr3tix.jpg",
        "is_bundle": false,
        "free_delivery": false,
        "created_at": "2025-09-01T04:15:55.054605+00:00"
    },
    {
        "name": "Sharp Sea Salt Spray",
        "sku": "SHARP-SHARPSEASALT-34",
        "slug": "sharp-sea-salt-spray",
        "short_description": "Mineral-rich sea salt for natural volume and textured hold.",
        "description": "Sea Salt Spray\n\nCreate effortless beach waves with our mineral-rich sea salt spray that adds natural volume and texture.\n\nHow to Use\n• Spray evenly on damp or dry hair.\n• Scrunch or style with fingers for natural texture.\n• Air-dry or diffuse for extra volume.\n\nWhat It Does\n• Adds natural volume and lift\n• Creates raw, beach-style texture\n• Helps balance scalp with essential minerals\n\nKey Ingredients\n• Dead Sea Minerals — strengthen hair fibers; support scalp balance\n• Magnesium & Calcium — support shine and elasticity\n",
        "price": 15.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-3_ljrau1.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698756/05505087-3572-48c8-9338-dafbed984b41_zbwehv.jpg",
        "is_bundle": false,
        "free_delivery": false,
        "created_at": "2025-09-01T04:15:55.237601+00:00"
    },
    {
        "name": "Sharp Shampoo",
        "sku": "SHARP-SHARPSHAMPOO-31",
        "slug": "sharp-shampoo",
        "short_description": "Aloe + Argan + Rosemary: gentle cleanse with strength and shine.",
        "description": "Nourishing Shampoo\n\nGently cleanse and strengthen your hair with our nutrient-rich formula.\n\nHow to Use\n• Massage 2–3 pumps into wet hair and scalp.\n• Work into a rich lather and rinse well. Repeat if needed.\n\nWhat It Does\n• Cleanses without stripping natural oils\n• Strengthens roots and supports fiber repair\n• Boosts shine and elasticity\n\nKey Ingredients\n• Aloe Vera — hydrates and soothes scalp\n• Argan Oil — nourishes; protects against dryness\n• Rosemary Oil — stimulates scalp micro-circulation\n• Vitamins E & B5 — support resilient hair\n• Silk Protein — improves softness and shine\n",
        "price": 19.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698760/5_dlyniy.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698758/2_ibkeof.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698757/1_qb65tt.jpg",
        "is_bundle": false,
        "free_delivery": false,
        "created_at": "2025-09-01T04:15:54.948837+00:00"
    },
    {
        "name": "Sharp Treatment Oil",
        "sku": "SHARP-SHARPTREATME-33",
        "slug": "sharp-treatment-oil",
        "short_description": "Nourishing multi-oil blend: repairs ends, tames frizz, adds shine.",
        "description": "SHARP Natural Hair Treatment — Nourishing Oil Blend\n\nRepairs and nourishes damaged ends, reduces frizz, and adds healthy natural shine while supporting overall hair health.\n\nHow to Use\n• Apply 2–4 drops to damp or dry hair, focusing on the ends.\n• Use daily as a leave-in, or overnight for deeper nourishment.\n\nBenefits\n• Repairs and nourishes split ends\n• Reduces frizz; boosts natural shine\n• Supports stronger, healthier hair\n\nKey Ingredients & Benefits\n• Sunflower Oil — moisturizes; protects from dryness\n• Sweet Almond Oil — adds nourishment and softness\n• Castor Oil — supports strength and growth\n• Coconut Oil — hydrates; enhances shine\n• Aloe Vera Extract — soothes scalp; hydrates hair\n• Laurel, Cress & Lavender Oils — nourish and revitalize\n• Garlic Oil — supports scalp health\n• Vitamin E (Tocopherol) — antioxidant protection; shine\n",
        "price": 17.0,
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092383/1_zc9pfx.jpg",
        "is_active": true,
        "gallery_csv": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092383/1_zc9pfx.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092382/3_oofwzf.jpg,https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092382/2_faqvtp.jpg",
        "is_bundle": false,
        "free_delivery": false,
        "created_at": "2025-09-01T04:15:55.136301+00:00"
    },
]

PRODUCT_COMPONENTS_DATA = [
    {
        "parent_name": "Shampoo + Conditioner + Sea Salt Trio",
        "component_name": "Sharp Shampoo",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Conditioner + Sea Salt Trio",
        "component_name": "Sharp Conditioner",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Conditioner + Sea Salt Trio",
        "component_name": "Sharp Sea Salt Spray",
        "quantity": 1
    },
    {
        "parent_name": "Full Package",
        "component_name": "Sharp Shampoo",
        "quantity": 1
    },
    {
        "parent_name": "Full Package",
        "component_name": "Sharp Conditioner",
        "quantity": 1
    },
    {
        "parent_name": "Full Package",
        "component_name": "Sharp Sea Salt Spray",
        "quantity": 1
    },
    {
        "parent_name": "Full Package",
        "component_name": "Sharp Treatment Oil",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Conditioner Duo",
        "component_name": "Sharp Shampoo",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Conditioner Duo",
        "component_name": "Sharp Conditioner",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Oil Duo",
        "component_name": "Sharp Shampoo",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Oil Duo",
        "component_name": "Sharp Treatment Oil",
        "quantity": 1
    },
    {
        "parent_name": "Conditioner + Oil Duo",
        "component_name": "Sharp Conditioner",
        "quantity": 1
    },
    {
        "parent_name": "Conditioner + Oil Duo",
        "component_name": "Sharp Treatment Oil",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Sea Salt Duo",
        "component_name": "Sharp Shampoo",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Sea Salt Duo",
        "component_name": "Sharp Sea Salt Spray",
        "quantity": 1
    },
    {
        "parent_name": "Conditioner + Sea Salt Duo",
        "component_name": "Sharp Conditioner",
        "quantity": 1
    },
    {
        "parent_name": "Conditioner + Sea Salt Duo",
        "component_name": "Sharp Sea Salt Spray",
        "quantity": 1
    },
    {
        "parent_name": "Sea Salt + Oil Duo",
        "component_name": "Sharp Sea Salt Spray",
        "quantity": 1
    },
    {
        "parent_name": "Sea Salt + Oil Duo",
        "component_name": "Sharp Treatment Oil",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Conditioner + Oil Trio",
        "component_name": "Sharp Shampoo",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Conditioner + Oil Trio",
        "component_name": "Sharp Conditioner",
        "quantity": 1
    },
    {
        "parent_name": "Shampoo + Conditioner + Oil Trio",
        "component_name": "Sharp Treatment Oil",
        "quantity": 1
    }
]

ORDERS_DATA = [
    {
        "order_number": "SH-612408",
        "created_at": "2025-11-24T19:37:17.175904+00:00",
        "updated_at": "2025-11-24T19:37:19.638163+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 62.0,
                        "itemDetails": "2x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-612408"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25110700000022",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-11-24T19:37:19.637162+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-612408",
                                    "pieceId": null,
                                    "awb": "25110700000022",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-612408",
                            "pieceId": null,
                            "awb": "25110700000022",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 62.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 62.0,
        "notes": "TEST",
        "status": "0",
        "zoho_data": {
            "contact_id": "6960748000000116026",
            "salesorder_id": "6960748000000402129",
            "synced_at": "2025-11-25T03:37:25Z",
            "invoice_id": "6960748000000402147"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-418095",
        "created_at": "2025-10-16T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.873649+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000241001",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.872646+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-170123",
        "created_at": "2025-10-15T04:35:52.474428+00:00",
        "updated_at": "2025-10-15T04:35:55.028462+00:00",
        "cancel_reason": "",
        "full_name": "Julia Marie Vengado Victorio",
        "phone": "+639637386001",
        "email": "clemenceocampo28@Gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "406 DIAMOND LANE CRISTIMAR VILLAGE",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST",
                        "addressDescription": "406 DIAMOND LANE CRISTIMAR VILLAGE, Amman",
                        "recipientName": "Julia Marie Vengado Victorio",
                        "recipientEmail": "clemenceocampo28@Gmail.com",
                        "recipientPhoneNumber": "639637386001",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-170123"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000044",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T04:35:55.028462+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-170123",
                                    "pieceId": null,
                                    "awb": "25100700000044",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-170123",
                            "pieceId": null,
                            "awb": "25100700000044",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "406 DIAMOND LANE CRISTIMAR VILLAGE, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "TEST",
        "status": "0",
        "zoho_data": {
            "contact_id": "6960748000000213087",
            "salesorder_id": "6960748000000226003",
            "synced_at": "2025-10-15T12:36:01Z",
            "invoice_id": "6960748000000226019"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-839048",
        "created_at": "2025-10-15T04:29:41.211227+00:00",
        "updated_at": "2025-10-15T04:29:44.507048+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "test",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-839048"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000043",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T04:29:44.507048+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-839048",
                                    "pieceId": null,
                                    "awb": "25100700000043",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-839048",
                            "pieceId": null,
                            "awb": "25100700000043",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "test",
        "status": "0",
        "zoho_data": {
            "contact_id": "6960748000000116026",
            "salesorder_id": "6960748000000218005",
            "synced_at": "2025-10-15T12:29:50Z"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-441924",
        "created_at": "2025-10-15T04:17:19.480221+00:00",
        "updated_at": "2025-10-15T04:17:23.492233+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 32.0,
                        "itemDetails": "1x Sharp Conditioner; 1x Sharp Treatment Oil",
                        "referenceID": "SH-441924"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000042",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T04:17:23.492233+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-441924",
                                    "pieceId": null,
                                    "awb": "25100700000042",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-441924",
                            "pieceId": null,
                            "awb": "25100700000042",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "",
        "status": "0",
        "zoho_data": {
            "contact_id": "6960748000000116026",
            "salesorder_id": "6960748000000213029",
            "synced_at": "2025-10-15T12:17:28Z"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-694204",
        "created_at": "2025-10-15T04:11:26.463396+00:00",
        "updated_at": "2025-10-15T04:11:29.302147+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 50.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Treatment Oil",
                        "referenceID": "SH-694204"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000041",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T04:11:29.302147+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-694204",
                                    "pieceId": null,
                                    "awb": "25100700000041",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-694204",
                            "pieceId": null,
                            "awb": "25100700000041",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 50.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 50.0,
        "notes": "TEST",
        "status": "0",
        "zoho_data": {
            "contact_id": "6960748000000116026"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-020597",
        "created_at": "2025-10-15T03:48:51.392162+00:00",
        "updated_at": "2025-10-15T03:48:55.723424+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 50.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray",
                        "referenceID": "SH-020597"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000040",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T03:48:55.723424+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-020597",
                                    "pieceId": null,
                                    "awb": "25100700000040",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-020597",
                            "pieceId": null,
                            "awb": "25100700000040",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 50.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 50.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {
            "contact_id": "6960748000000116026"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-190112",
        "created_at": "2025-10-15T03:47:53.971059+00:00",
        "updated_at": "2025-10-15T03:47:56.550281+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-190112"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000039",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T03:47:56.550281+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-190112",
                                    "pieceId": null,
                                    "awb": "25100700000039",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-190112",
                            "pieceId": null,
                            "awb": "25100700000039",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "TEST",
        "status": "0",
        "zoho_data": {
            "contact_id": "6960748000000116026"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-857517",
        "created_at": "2025-10-15T03:33:56.027173+00:00",
        "updated_at": "2025-10-15T03:33:58.551644+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-857517"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000038",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T03:33:58.551644+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-857517",
                                    "pieceId": null,
                                    "awb": "25100700000038",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-857517",
                            "pieceId": null,
                            "awb": "25100700000038",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "TEST",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-739793",
        "created_at": "2025-10-15T03:28:00.000891+00:00",
        "updated_at": "2025-10-15T03:28:04.425552+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "test",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-739793"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000037",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T03:28:04.425552+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-739793",
                                    "pieceId": null,
                                    "awb": "25100700000037",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-739793",
                            "pieceId": null,
                            "awb": "25100700000037",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "test",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-822005",
        "created_at": "2025-10-15T02:32:56.587719+00:00",
        "updated_at": "2025-10-15T02:32:59.574518+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 30.0,
                        "itemDetails": "1x Sharp Conditioner; 1x Sharp Sea Salt Spray",
                        "referenceID": "SH-822005"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000036",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-15T02:32:59.574518+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-822005",
                                    "pieceId": null,
                                    "awb": "25100700000036",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-822005",
                            "pieceId": null,
                            "awb": "25100700000036",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 30.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 30.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "TEST-ORDER-1760420221",
        "created_at": "2025-10-14T05:37:01.593708+00:00",
        "updated_at": "2025-10-14T05:37:01.593708+00:00",
        "cancel_reason": "",
        "full_name": "Test Customer - Inventory Check",
        "phone": "+962791234567",
        "email": "test@example.com",
        "address_line1": "Test Address, Amman, Jordan",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {},
        "shipping_address_text": "Test Address, Amman, Jordan",
        "shipping_method": "standard",
        "payment_method": "Online",
        "subtotal": 50.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 50.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "TEST-ORDER-1760420143",
        "created_at": "2025-10-14T05:35:43.503080+00:00",
        "updated_at": "2025-10-14T05:35:43.503080+00:00",
        "cancel_reason": "",
        "full_name": "Test Customer - Inventory Check",
        "phone": "+962791234567",
        "email": "test@example.com",
        "address_line1": "Test Address, Amman, Jordan",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {},
        "shipping_address_text": "Test Address, Amman, Jordan",
        "shipping_method": "standard",
        "payment_method": "Online",
        "subtotal": 50.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 50.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "TEST-ORDER-1760420123",
        "created_at": "2025-10-14T05:35:23.533036+00:00",
        "updated_at": "2025-10-14T05:35:23.533036+00:00",
        "cancel_reason": "",
        "full_name": "Test Customer - Inventory Check",
        "phone": "+962791234567",
        "email": "test@example.com",
        "address_line1": "Test Address, Amman, Jordan",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {},
        "shipping_address_text": "Test Address, Amman, Jordan",
        "shipping_method": "standard",
        "payment_method": "Online",
        "subtotal": 50.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 50.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-413239",
        "created_at": "2025-10-13T18:27:04.907232+00:00",
        "updated_at": "2025-10-13T18:27:07.452278+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDE RCOMPOSITE",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 50.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray",
                        "referenceID": "SH-413239"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000029",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-13T18:27:07.452278+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-413239",
                                    "pieceId": null,
                                    "awb": "25100700000029",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-413239",
                            "pieceId": null,
                            "awb": "25100700000029",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 50.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 50.0,
        "notes": "TEST ORDE RCOMPOSITE",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-370474",
        "created_at": "2025-10-13T18:25:01.409597+00:00",
        "updated_at": "2025-10-13T18:25:05.173440+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER ONLY",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-370474"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000028",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-13T18:25:05.173440+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-370474",
                                    "pieceId": null,
                                    "awb": "25100700000028",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-370474",
                            "pieceId": null,
                            "awb": "25100700000028",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "TEST ORDER ONLY",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-970389",
        "created_at": "2025-10-13T18:16:45.402903+00:00",
        "updated_at": "2025-10-13T18:16:49.906323+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER COMPOSITE",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 32.0,
                        "itemDetails": "1x Sharp Conditioner; 1x Sharp Treatment Oil",
                        "referenceID": "SH-970389"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000027",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-13T18:16:49.906323+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-970389",
                                    "pieceId": null,
                                    "awb": "25100700000027",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-970389",
                            "pieceId": null,
                            "awb": "25100700000027",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "TEST ORDER COMPOSITE",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-223810",
        "created_at": "2025-10-13T17:57:10.072829+00:00",
        "updated_at": "2025-10-13T17:57:14.148763+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST COMPOSITE",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 79.0,
                        "itemDetails": "2x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-223810"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000026",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-13T17:57:14.148763+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-223810",
                                    "pieceId": null,
                                    "awb": "25100700000026",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-223810",
                            "pieceId": null,
                            "awb": "25100700000026",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 79.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 79.0,
        "notes": "TEST COMPOSITE",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "TEST-20251008024916",
        "created_at": "2025-10-08T02:49:16.554533+00:00",
        "updated_at": "2025-10-08T02:49:16.555541+00:00",
        "cancel_reason": "",
        "full_name": "Zoho Test Customer",
        "phone": "+962791234567",
        "email": "zoho.test@example.com",
        "address_line1": "Test Address for Zoho Integration",
        "city": "Amman",
        "province": "Amman",
        "zip_code": "11183",
        "country": "JO",
        "shipping_address": {},
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "standard",
        "payment_method": "online",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "Test order for Zoho integration verification",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-702898",
        "created_at": "2025-10-08T02:39:47.650482+00:00",
        "updated_at": "2025-10-08T02:39:49.737754+00:00",
        "cancel_reason": "",
        "full_name": "TEST ORDER",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "TEST ORDER",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-702898"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000019",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-08T02:39:49.737754+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-702898",
                                    "pieceId": null,
                                    "awb": "25100700000019",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-702898",
                            "pieceId": null,
                            "awb": "25100700000019",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-071063",
        "created_at": "2025-10-08T02:37:15.487304+00:00",
        "updated_at": "2025-10-08T02:37:16.558939+00:00",
        "cancel_reason": "",
        "full_name": "TEST ORDER",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "test order",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "TEST ORDER",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-071063"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000018",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-08T02:37:16.558939+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-071063",
                                    "pieceId": null,
                                    "awb": "25100700000018",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-071063",
                            "pieceId": null,
                            "awb": "25100700000018",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "test order",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-503744",
        "created_at": "2025-10-08T02:35:36.190122+00:00",
        "updated_at": "2025-10-08T02:35:38.493576+00:00",
        "cancel_reason": "",
        "full_name": "TEST ORDER",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "TEST ORDER",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 30.0,
                        "itemDetails": "1x Sharp Conditioner; 1x Sharp Sea Salt Spray",
                        "referenceID": "SH-503744"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25100700000017",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-10-08T02:35:38.493576+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-503744",
                                    "pieceId": null,
                                    "awb": "25100700000017",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-503744",
                            "pieceId": null,
                            "awb": "25100700000017",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 30.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 30.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-838622",
        "created_at": "2025-10-03T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.891922+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000179031",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.891922+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-884572",
        "created_at": "2025-10-02T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.893427+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000179019",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.893427+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-049449",
        "created_at": "2025-10-01T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.893952+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 34.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000180001",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.893952+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-948151",
        "created_at": "2025-09-30T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.894961+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000174001",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.894961+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-008631",
        "created_at": "2025-09-28T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.896958+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000158001",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.896958+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-635996",
        "created_at": "2025-09-28T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.895959+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 19.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000158013",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.895959+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-259418",
        "created_at": "2025-09-26T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.897958+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000154001",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.897958+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-179560",
        "created_at": "2025-09-25T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.898958+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 19.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000129015",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.898958+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-690602",
        "created_at": "2025-09-25T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.898958+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000137001",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.897958+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-699183",
        "created_at": "2025-09-24T14:58:27.674834+00:00",
        "updated_at": "2025-09-24T14:58:29.918231+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-699183"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000018",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T14:58:29.918231+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-699183",
                                    "pieceId": null,
                                    "awb": "25090700000018",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-699183",
                            "pieceId": null,
                            "awb": "25090700000018",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-522425",
        "created_at": "2025-09-24T14:42:50.936846+00:00",
        "updated_at": "2025-09-24T14:42:52.138805+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "test order",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-522425"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000017",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T14:42:52.138805+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-522425",
                                    "pieceId": null,
                                    "awb": "25090700000017",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-522425",
                            "pieceId": null,
                            "awb": "25090700000017",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "test order",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-035466",
        "created_at": "2025-09-24T14:36:20.458004+00:00",
        "updated_at": "2025-09-24T14:36:22.728427+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "test order",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-035466"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000016",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T14:36:22.728427+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-035466",
                                    "pieceId": null,
                                    "awb": "25090700000016",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-035466",
                            "pieceId": null,
                            "awb": "25090700000016",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "test order",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-463076",
        "created_at": "2025-09-24T14:21:04.620079+00:00",
        "updated_at": "2025-09-24T14:21:06.863604+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 32.0,
                        "itemDetails": "1x Sharp Conditioner; 1x Sharp Treatment Oil",
                        "referenceID": "SH-463076"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000015",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T14:21:06.863604+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-463076",
                                    "pieceId": null,
                                    "awb": "25090700000015",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-463076",
                            "pieceId": null,
                            "awb": "25090700000015",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-536037",
        "created_at": "2025-09-24T14:15:37.737933+00:00",
        "updated_at": "2025-09-24T14:15:40.193558+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 60.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Sea Salt Spray; 1x Sharp Treatment Oil",
                        "referenceID": "SH-536037"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000014",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T14:15:40.193558+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-536037",
                                    "pieceId": null,
                                    "awb": "25090700000014",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-536037",
                            "pieceId": null,
                            "awb": "25090700000014",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 60.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 60.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-068930",
        "created_at": "2025-09-24T13:22:34.800357+00:00",
        "updated_at": "2025-09-24T13:22:37.115931+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 17.0,
                        "itemDetails": "1x Sharp Treatment Oil",
                        "referenceID": "SH-068930"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000013",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T13:22:37.115931+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-068930",
                                    "pieceId": null,
                                    "awb": "25090700000013",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-068930",
                            "pieceId": null,
                            "awb": "25090700000013",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 17.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 17.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-597411",
        "created_at": "2025-09-24T12:34:03.429816+00:00",
        "updated_at": "2025-09-24T12:34:05.721500+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 15.0,
                        "itemDetails": "1x Sharp Sea Salt Spray",
                        "referenceID": "SH-597411"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000012",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T12:34:05.721500+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-597411",
                                    "pieceId": null,
                                    "awb": "25090700000012",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-597411",
                            "pieceId": null,
                            "awb": "25090700000012",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 15.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-373292",
        "created_at": "2025-09-24T12:31:37.014696+00:00",
        "updated_at": "2025-09-24T12:31:39.236262+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 50.0,
                        "itemDetails": "1x Sharp Shampoo; 1x Sharp Conditioner; 1x Sharp Treatment Oil",
                        "referenceID": "SH-373292"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000011",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T12:31:39.236262+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-373292",
                                    "pieceId": null,
                                    "awb": "25090700000011",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-373292",
                            "pieceId": null,
                            "awb": "25090700000011",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 50.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 50.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-147909",
        "created_at": "2025-09-24T12:26:18.395673+00:00",
        "updated_at": "2025-09-24T12:26:20.901261+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "TEST ORDER",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 19.0,
                        "itemDetails": "1x Sharp Shampoo",
                        "referenceID": "SH-147909"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000010",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-24T12:26:20.900263+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-147909",
                                    "pieceId": null,
                                    "awb": "25090700000010",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-147909",
                            "pieceId": null,
                            "awb": "25090700000010",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 19.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 19.0,
        "notes": "TEST ORDER",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-254751",
        "created_at": "2025-09-24T00:00:00+00:00",
        "updated_at": "2025-10-17T02:46:30.900464+00:00",
        "cancel_reason": "",
        "full_name": "Unknown Customer",
        "phone": "",
        "email": "",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": ", ,",
        "shipping_method": "standard",
        "payment_method": "cod",
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "Imported from Zoho on 2025-10-17 02:46:30",
        "status": "0",
        "zoho_data": {
            "salesorder_id": "6960748000000125340",
            "contact_id": null,
            "synced_at": "2025-10-17T02:46:30.899958+00:00",
            "import_source": "zoho_pull"
        },
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-321439",
        "created_at": "2025-09-22T07:46:01.971150+00:00",
        "updated_at": "2025-09-22T07:46:04.273062+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "district": "Amman",
            "city_ar": "عمان",
            "area_ar": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "companyStoreID": 737,
                        "recipientCity": "عمان",
                        "recipientArea": "Amman",
                        "remark": "test orde ronly",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "codAmount": 15.0,
                        "itemDetails": "1x Sharp Sea Salt Spray",
                        "referenceID": "SH-321439"
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090700000005",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-22T07:46:04.272069+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-321439",
                                    "pieceId": null,
                                    "awb": "25090700000005",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-321439",
                            "pieceId": null,
                            "awb": "25090700000005",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, عمان, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 15.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "test orde ronly",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-799100",
        "created_at": "2025-09-22T02:43:27.863999+00:00",
        "updated_at": "2025-09-22T02:43:27.863999+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 700,
                        "recipientCity": "Amman",
                        "recipientArea": "Amman",
                        "remark": null,
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": 34.0,
                        "itemDetails": "1× Sharp Sea Salt Spray; 1× Sharp Shampoo",
                        "ReferenceID": "SH-799100",
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "Wassel validation failed: {'isSuccess': False, 'validations': [{'code': None, 'message': 'Store Is Not Belongs To Company', 'exceptionMessage': None, 'refID': 'SH-799100'}, {'code': None, 'message': 'لا يوجد مدينة بالمسمى - Amman', 'exceptionMessage': None, 'refID': 'SH-799100'}], 'data': None, 'httpStatusCode': 200}"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 34.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 34.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-460835",
        "created_at": "2025-09-22T02:35:50.702330+00:00",
        "updated_at": "2025-09-22T02:35:50.703331+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 700,
                        "recipientCity": "Amman",
                        "recipientArea": "Amman",
                        "remark": "test order only dont push through",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": 15.0,
                        "itemDetails": "1× Sharp Sea Salt Spray",
                        "ReferenceID": "SH-460835",
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "Wassel validation failed: {'isSuccess': False, 'validations': [{'code': None, 'message': 'Store Is Not Belongs To Company', 'exceptionMessage': None, 'refID': 'SH-460835'}, {'code': None, 'message': 'لا يوجد مدينة بالمسمى - Amman', 'exceptionMessage': None, 'refID': 'SH-460835'}], 'data': None, 'httpStatusCode': 200}"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 15.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "test order only dont push through",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-617052",
        "created_at": "2025-09-22T02:33:49.749982+00:00",
        "updated_at": "2025-09-22T02:33:49.749982+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 700,
                        "recipientCity": "Amman",
                        "recipientArea": "Amman",
                        "remark": "tes order only dont push through",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": 32.0,
                        "itemDetails": "1× Sharp Conditioner; 1× Sharp Treatment Oil",
                        "ReferenceID": "SH-617052",
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "Wassel validation failed: {'isSuccess': False, 'validations': [{'code': None, 'message': 'Store Is Not Belongs To Company', 'exceptionMessage': None, 'refID': 'SH-617052'}, {'code': None, 'message': 'لا يوجد مدينة بالمسمى - Amman', 'exceptionMessage': None, 'refID': 'SH-617052'}], 'data': None, 'httpStatusCode': 200}"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "tes order only dont push through",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-588629",
        "created_at": "2025-09-18T06:23:02.813541+00:00",
        "updated_at": "2025-09-18T06:23:05.057888+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Aqaba",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Aqaba",
                        "remark": "test",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Aqaba",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": 17.0,
                        "itemDetails": "1× Sharp Treatment Oil",
                        "ReferenceID": "SH-588629",
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ],
                "name": "wasselexpress",
                "awb": "25090012000005",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-18T06:23:05.057888+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-588629",
                                    "pieceId": null,
                                    "awb": "25090012000005",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-588629",
                            "pieceId": null,
                            "awb": "25090012000005",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Aqaba, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 17.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 17.0,
        "notes": "test",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-716174",
        "created_at": "2025-09-18T06:16:45.223398+00:00",
        "updated_at": "2025-09-18T06:16:45.224406+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Ajloun",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Ajloun",
                        "remark": "testt",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Ajloun",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": 17.0,
                        "itemDetails": "1× Sharp Treatment Oil",
                        "ReferenceID": "SH-716174",
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "401 Client Error: Unauthorized for url: https://demo.wasselexpress.com/web-api/api/account/Login"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Ajloun, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 17.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 17.0,
        "notes": "testt",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-769724",
        "created_at": "2025-09-18T06:14:04.613631+00:00",
        "updated_at": "2025-09-18T06:14:04.613631+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Aqaba",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Aqaba",
                        "remark": "test",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Aqaba",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": 15.0,
                        "itemDetails": "1× Sharp Sea Salt Spray",
                        "ReferenceID": "SH-769724",
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "All Wassel login endpoints failed"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Aqaba, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 15.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "test",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-176029",
        "created_at": "2025-09-18T06:06:23.865018+00:00",
        "updated_at": "2025-09-18T06:06:23.866526+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Irbid",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Irbid",
                        "remark": "test order payload",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Irbid",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": 15.0,
                        "itemDetails": "1× Sharp Sea Salt Spray",
                        "ReferenceID": "SH-176029",
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "All Wassel login endpoints failed"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Irbid, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 15.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 15.0,
        "notes": "test order payload",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-058756",
        "created_at": "2025-09-18T05:48:34.091726+00:00",
        "updated_at": "2025-09-18T05:48:34.091726+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Amman",
                        "remark": null,
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "+962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": "17.00",
                        "itemDetails": "1× Sharp Treatment Oil",
                        "referenceID": "SH-058756",
                        "companyID": null,
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "All Wassel login endpoints failed"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 17.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 17.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-067627",
        "created_at": "2025-09-18T05:42:00.569920+00:00",
        "updated_at": "2025-09-18T05:42:00.570925+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Amman",
                        "remark": "test order 11",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "+962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": "17.00",
                        "itemDetails": "1× Sharp Treatment Oil",
                        "referenceID": "SH-067627",
                        "companyID": null,
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "All Wassel login endpoints failed"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 17.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 17.0,
        "notes": "test order 11",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-253898",
        "created_at": "2025-09-16T13:06:33.404606+00:00",
        "updated_at": "2025-09-16T13:06:33.405608+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Amman",
                        "remark": "test",
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "+962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": "70.00",
                        "itemDetails": "1× Sharp Sea Salt Spray; 1× Sharp Treatment Oil; 1× Sharp Shampoo; 1× Sharp Conditioner",
                        "referenceID": "SH-253898",
                        "companyID": null,
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "All Wassel login endpoints failed"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 70.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 70.0,
        "notes": "test",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-855478",
        "created_at": "2025-09-16T13:01:37.044050+00:00",
        "updated_at": "2025-09-16T13:01:37.045049+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "last_payload": [
                    {
                        "pieceId": null,
                        "lat": null,
                        "lng": null,
                        "companyStoreID": 13,
                        "recipientCity": "Amman",
                        "recipientArea": "Amman",
                        "remark": null,
                        "addressDescription": "Building 18, Wasfi Al-Tal St., Khalda, Amman",
                        "recipientName": "Lina Haddad",
                        "recipientEmail": "juliavictorio16@gmail.com",
                        "recipientPhoneNumber": "+962791234567",
                        "recipientSecondPhoneNumber": null,
                        "codAmount": "34.00",
                        "itemDetails": "1× Sharp Sea Salt Spray; 1× Sharp Shampoo",
                        "referenceID": "SH-855478",
                        "companyID": null,
                        "itemWeight": null,
                        "itemDimension": null,
                        "productType": null
                    }
                ]
            },
            "_carrier_error": "All Wassel login endpoints failed"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 34.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 34.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-038973",
        "created_at": "2025-09-16T12:50:47.997215+00:00",
        "updated_at": "2025-09-16T12:50:47.997215+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier_error": "All Wassel login endpoints failed"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-415495",
        "created_at": "2025-09-16T07:47:24.061543+00:00",
        "updated_at": "2025-09-16T07:47:24.062544+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier_error": "'SUBMIT_PATH_ALT'"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 70.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 70.0,
        "notes": "test order",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-975319",
        "created_at": "2025-09-16T07:45:58.572741+00:00",
        "updated_at": "2025-09-16T07:45:58.572741+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier_error": "'SUBMIT_PATH_ALT'"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "test only",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-689056",
        "created_at": "2025-09-16T07:26:13.780906+00:00",
        "updated_at": "2025-09-16T07:26:17.057868+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "name": "wasselexpress",
                "awb": "25090012000003",
                "history": [
                    {
                        "code": "0",
                        "label": "Created (awaiting courier)",
                        "at": "2025-09-16T07:26:17.057868+00:00",
                        "raw": {
                            "isSuccess": true,
                            "validations": [],
                            "data": [
                                {
                                    "referenceNumber": "SH-689056",
                                    "pieceId": null,
                                    "awb": "25090012000003",
                                    "awB_File": null
                                }
                            ],
                            "httpStatusCode": 200
                        }
                    }
                ],
                "last_update": "0",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-689056",
                            "pieceId": null,
                            "awb": "25090012000003",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 151.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 151.0,
        "notes": "test",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-076466",
        "created_at": "2025-09-16T07:21:17.717052+00:00",
        "updated_at": "2025-09-16T07:21:17.718052+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier_error": "Wassel validation failed: {'isSuccess': False, 'validations': [{'code': None, 'message': 'Submitted Reference Number is already reserved.', 'exceptionMessage': None, 'refID': 'SH-076466'}], 'data': None, 'httpStatusCode': 200}"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 59.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 59.0,
        "notes": "test order",
        "status": "0",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-333220",
        "created_at": "2025-09-16T06:28:13.147948+00:00",
        "updated_at": "2025-09-16T06:28:13.148960+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman",
            "_carrier": {
                "name": "wasselexpress",
                "awb": "25090012000001",
                "label_pdf": null,
                "last_update": "created",
                "raw": {
                    "isSuccess": true,
                    "validations": [],
                    "data": [
                        {
                            "referenceNumber": "SH-333220",
                            "pieceId": null,
                            "awb": "25090012000001",
                            "awB_File": null
                        }
                    ],
                    "httpStatusCode": 200
                }
            }
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 32.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 32.0,
        "notes": "",
        "status": "confirmed",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-086780",
        "created_at": "2025-09-15T06:40:25.214082+00:00",
        "updated_at": "2025-09-15T06:40:25.214082+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "area": "Amman"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 19.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 19.0,
        "notes": "",
        "status": "pending",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-503994",
        "created_at": "2025-09-13T13:04:45.055779+00:00",
        "updated_at": "2025-09-13T13:04:45.055779+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "JO",
        "shipping_address": {
            "address_line1": "Building 18, Wasfi Al-Tal St., Khalda",
            "city": "Amman",
            "postal_code": "11953",
            "area": "Amman"
        },
        "shipping_address_text": "Building 18, Wasfi Al-Tal St., Khalda, Amman, Amman, 11953, Jordan",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 164.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 164.0,
        "notes": "",
        "status": "pending",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-741949",
        "created_at": "2025-09-13T12:39:01.564157+00:00",
        "updated_at": "2025-09-13T12:39:01.564157+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": "",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 140.0,
        "shipping_cost": 0.0,
        "discount_total": 14.0,
        "grand_total": 126.0,
        "notes": "",
        "status": "pending",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-628744",
        "created_at": "2025-09-13T12:36:38.664729+00:00",
        "updated_at": "2025-09-13T12:36:38.664729+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": "",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 159.0,
        "shipping_cost": 0.0,
        "discount_total": 0.0,
        "grand_total": 159.0,
        "notes": "",
        "status": "pending",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    },
    {
        "order_number": "SH-168062",
        "created_at": "2025-09-13T11:15:24.913523+00:00",
        "updated_at": "2025-09-13T11:15:24.914520+00:00",
        "cancel_reason": "",
        "full_name": "Lina Haddad",
        "phone": "+962791234567",
        "email": "juliavictorio16@gmail.com",
        "address_line1": "",
        "city": "",
        "province": "",
        "zip_code": "",
        "country": "",
        "shipping_address": {},
        "shipping_address_text": "",
        "shipping_method": "free",
        "payment_method": "cod",
        "subtotal": 70.0,
        "shipping_cost": 0.0,
        "discount_total": 7.0,
        "grand_total": 63.0,
        "notes": "",
        "status": "pending",
        "zoho_data": {},
        "promo_code": "",
        "promo_label": ""
    }
]

ORDER_ITEMS_DATA = [
    {
        "order_number": "SH-168062",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-168062",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-168062",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-168062",
        "product_name": "Sharp Conditioner",
        "name": "Sharp Conditioner",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-628744",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-628744",
        "product_name": "Shampoo + Conditioner + Oil Trio",
        "name": "Shampoo + Conditioner + Oil Trio",
        "unit_price": 50.0,
        "quantity": 1,
        "line_total": 50.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-628744",
        "product_name": "Shampoo + Conditioner + Sea Salt Trio",
        "name": "Shampoo + Conditioner + Sea Salt Trio",
        "unit_price": 30.0,
        "quantity": 2,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-628744",
        "product_name": "Shampoo + Sea Salt Duo",
        "name": "Shampoo + Sea Salt Duo",
        "unit_price": 30.0,
        "quantity": 1,
        "line_total": 30.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-741949",
        "product_name": "Conditioner + Sea Salt Duo",
        "name": "Conditioner + Sea Salt Duo",
        "unit_price": 30.0,
        "quantity": 1,
        "line_total": 30.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-741949",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-741949",
        "product_name": "Shampoo + Conditioner + Oil Trio",
        "name": "Shampoo + Conditioner + Oil Trio",
        "unit_price": 50.0,
        "quantity": 1,
        "line_total": 50.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-503994",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-503994",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 2,
        "line_total": 120.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-503994",
        "product_name": "Sea Salt + Oil Duo",
        "name": "Sea Salt + Oil Duo",
        "unit_price": 29.0,
        "quantity": 1,
        "line_total": 29.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-086780",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-333220",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-076466",
        "product_name": "Sea Salt + Oil Duo",
        "name": "Sea Salt + Oil Duo",
        "unit_price": 29.0,
        "quantity": 1,
        "line_total": 29.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-076466",
        "product_name": "Conditioner + Sea Salt Duo",
        "name": "Conditioner + Sea Salt Duo",
        "unit_price": 30.0,
        "quantity": 1,
        "line_total": 30.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-689056",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-689056",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-689056",
        "product_name": "Shampoo + Sea Salt Duo",
        "name": "Shampoo + Sea Salt Duo",
        "unit_price": 30.0,
        "quantity": 1,
        "line_total": 30.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-689056",
        "product_name": "Sea Salt + Oil Duo",
        "name": "Sea Salt + Oil Duo",
        "unit_price": 29.0,
        "quantity": 1,
        "line_total": 29.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-689056",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-975319",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-975319",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-415495",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-415495",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-415495",
        "product_name": "Sharp Conditioner",
        "name": "Sharp Conditioner",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-415495",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-038973",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-855478",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-855478",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-253898",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-253898",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-253898",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-253898",
        "product_name": "Sharp Conditioner",
        "name": "Sharp Conditioner",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-067627",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-058756",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-176029",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-769724",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-716174",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-588629",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-617052",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-460835",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-799100",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-799100",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-321439",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-147909",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-373292",
        "product_name": "Shampoo + Conditioner + Oil Trio",
        "name": "Shampoo + Conditioner + Oil Trio",
        "unit_price": 50.0,
        "quantity": 1,
        "line_total": 50.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-597411",
        "product_name": "Sharp Sea Salt Spray",
        "name": "Sharp Sea Salt Spray",
        "unit_price": 15.0,
        "quantity": 1,
        "line_total": 15.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-068930",
        "product_name": "Sharp Treatment Oil",
        "name": "Sharp Treatment Oil",
        "unit_price": 17.0,
        "quantity": 1,
        "line_total": 17.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-536037",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-463076",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-035466",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-522425",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-699183",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-503744",
        "product_name": "Conditioner + Sea Salt Duo",
        "name": "Conditioner + Sea Salt Duo",
        "unit_price": 30.0,
        "quantity": 1,
        "line_total": 30.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-071063",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-702898",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "TEST-20251008024916",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-223810",
        "product_name": "Sharp Shampoo",
        "name": "Sharp Shampoo",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-223810",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-970389",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-370474",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-413239",
        "product_name": "Shampoo + Conditioner + Sea Salt Trio",
        "name": "Shampoo + Conditioner + Sea Salt Trio",
        "unit_price": 50.0,
        "quantity": 1,
        "line_total": 50.0,
        "cancel_reason": ""
    },
    {
        "order_number": "TEST-ORDER-1760420143",
        "product_name": "Conditioner",
        "name": "Conditioner",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "TEST-ORDER-1760420143",
        "product_name": "Conditioner + Oil",
        "name": "Conditioner + Oil",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "TEST-ORDER-1760420221",
        "product_name": "Sharp Conditioner",
        "name": "Sharp Conditioner",
        "unit_price": 19.0,
        "quantity": 1,
        "line_total": 19.0,
        "cancel_reason": ""
    },
    {
        "order_number": "TEST-ORDER-1760420221",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-822005",
        "product_name": "Conditioner + Sea Salt Duo",
        "name": "Conditioner + Sea Salt Duo",
        "unit_price": 30.0,
        "quantity": 1,
        "line_total": 30.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-739793",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-857517",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-190112",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-020597",
        "product_name": "Shampoo + Conditioner + Sea Salt Trio",
        "name": "Shampoo + Conditioner + Sea Salt Trio",
        "unit_price": 50.0,
        "quantity": 1,
        "line_total": 50.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-694204",
        "product_name": "Shampoo + Conditioner + Oil Trio",
        "name": "Shampoo + Conditioner + Oil Trio",
        "unit_price": 50.0,
        "quantity": 1,
        "line_total": 50.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-441924",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-839048",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-170123",
        "product_name": "Full Package",
        "name": "Full Package",
        "unit_price": 60.0,
        "quantity": 1,
        "line_total": 60.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-612408",
        "product_name": "Conditioner + Sea Salt Duo",
        "name": "Conditioner + Sea Salt Duo",
        "unit_price": 30.0,
        "quantity": 1,
        "line_total": 30.0,
        "cancel_reason": ""
    },
    {
        "order_number": "SH-612408",
        "product_name": "Conditioner + Oil Duo",
        "name": "Conditioner + Oil Duo",
        "unit_price": 32.0,
        "quantity": 1,
        "line_total": 32.0,
        "cancel_reason": ""
    }
]

PROMO_CODES_DATA = [
    {
        "code": "BLACKFRIDAY2025",
        "type": "percent",
        "value": 30.0,
        "description": "30% discount on all Sharp products on the website for the Black Friday promotion.",
        "min_subtotal": 0.0,
        "max_discount": null,
        "countries_csv": "",
        "starts_at": null,
        "ends_at": null,
        "active": true,
        "usage_limit": null,
        "used_count": 0,
        "created_at": "2025-11-24T19:22:21.881801+00:00",
        "updated_at": "2025-11-24T19:22:21.881801+00:00"
    },
    {
        "code": "SHARP2025",
        "type": "percent",
        "value": 10.0,
        "description": "",
        "min_subtotal": 50.0,
        "max_discount": 100.0,
        "countries_csv": "",
        "starts_at": null,
        "ends_at": "2025-09-19T00:00:00+00:00",
        "active": true,
        "usage_limit": 50,
        "used_count": 4,
        "created_at": "2025-09-13T03:13:25.119694+00:00",
        "updated_at": "2025-09-13T03:24:37.124808+00:00"
    }
]

POSTS_DATA = [
    {
        "title": "Quiet Luxury for Your Hair: The SHARP Natural Hair Ritual",
        "slug": "natural-hair-care",
        "excerpt": "Luxury is discipline. Discover the ritual of SHARP Natural Hair Care — where science meets botanicals, and every strand tells a story of strength, shine, and serenity.",
        "cover_image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg",
        "published_at": "2025-09-12T04:10:30.236760+00:00",
        "author_name": "SHARP Editorial"
    },
    {
        "title": "The Art of Modern Hair Care: Beyond Shampoo & Conditioner",
        "slug": "art-of-hair-care",
        "excerpt": "Hair care today is more than washing and conditioning — it’s a ritual of self-expression, balance, and modern science meeting timeless nature.",
        "cover_image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg",
        "published_at": "2025-09-12T04:14:13.591136+00:00",
        "author_name": "SHARP Editorial"
    }
]

POST_BLOCKS_DATA = [
    {
        "post_slug": "natural-hair-care",
        "order": 1,
        "kind": "paragraph",
        "text": "Imagine stepping out the door each morning knowing your hair feels as effortless as it looks.\nThat’s the promise of quiet luxury — not loud, not fleeting, but a ritual of care that whispers confidence.\nAt SHARP, we’ve crafted a collection that doesn’t just style your hair — it transforms the way you experience it.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 1,
        "kind": "paragraph",
        "text": "Healthy, radiant hair has never been about following trends — it’s about understanding the art behind the care.\nThe modern routine is no longer just shampoo and conditioner. It’s a thoughtful ritual where hydration, balance,\nand nourishment come together to express your identity with quiet confidence.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 2,
        "kind": "heading",
        "text": "Sea Salt Spray — Raw Texture, Refined Confidence",
        "level": "h2",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 2,
        "kind": "heading",
        "text": "Why Rituals Matter More Than Routines",
        "level": "h2",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 3,
        "kind": "paragraph",
        "text": "Forget stiff sprays. Our mineral-rich Sea Salt Spray is your shortcut to undone, confident waves —\ntexture that feels as natural as ocean air, with volume that lingers from sunrise to sunset.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 3,
        "kind": "paragraph",
        "text": "A routine is a task you repeat. A ritual is an act of intention.\nWhen it comes to hair care, that intention transforms the ordinary into the extraordinary.\nIt’s the difference between rushing through a wash and savoring a moment that sets the tone for your entire day.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 4,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg",
        "image2_url": "",
        "caption": "Sea Salt Spray",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 4,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg",
        "image2_url": "",
        "caption": "SHARP Hair Care Ritual",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 5,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-3_ljrau1.jpg",
        "image2_url": "",
        "caption": "Sea Salt Spray",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 5,
        "kind": "heading",
        "text": "Nature Meets Modern Science",
        "level": "h2",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 6,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698756/05505087-3572-48c8-9338-dafbed984b41_zbwehv.jpg",
        "image2_url": "",
        "caption": "Sea Salt Spray",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 6,
        "kind": "paragraph",
        "text": "Today’s best formulas don’t force you to choose between natural purity and scientific results.\nBotanicals like aloe, rosemary, and argan oil deliver softness and shine, while advanced proteins and vitamins\nstrengthen from within. The synergy is where the magic happens.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 7,
        "kind": "heading",
        "text": "Nourishing Shampoo — The Reset Button for Your Hair",
        "level": "h2",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 7,
        "kind": "heading",
        "text": "Minimal Products, Maximum Impact",
        "level": "h2",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 8,
        "kind": "paragraph",
        "text": "This isn’t just shampoo. It’s a daily reset.\nA nutrient-rich formula that cleanses without compromise, stripping away the noise of buildup while\nprotecting the harmony of your natural oils. Think of it as mindfulness in a bottle — clarity for your scalp, energy for your roots.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 8,
        "kind": "paragraph",
        "text": "Luxury isn’t about a crowded shelf — it’s about choosing fewer, smarter products that actually work.\nA hydrating conditioner that doubles as a leave-in. An oil blend that replaces three separate serums.\nThis is the essence of quiet luxury: intentional simplicity with amplified results.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 9,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg",
        "image2_url": "",
        "caption": "Nourishing Shampoo",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 9,
        "kind": "callout",
        "text": "Remember: Your hair is not just something you style — it’s something you tell your story with.\nCare for it like you would any art form.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 10,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698760/5_dlyniy.jpg",
        "image2_url": "",
        "caption": "Nourishing Shampoo",
        "prod_query": ""
    },
    {
        "post_slug": "art-of-hair-care",
        "order": 10,
        "kind": "paragraph",
        "text": "✨ Explore SHARP’s natural collection and turn your routine into an art form → /products/",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 11,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698758/2_ibkeof.jpg",
        "image2_url": "",
        "caption": "Nourishing Shampoo",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 12,
        "kind": "heading",
        "text": "Hydrating Conditioner — Gloss Without Weight",
        "level": "h2",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 13,
        "kind": "paragraph",
        "text": "Too often, conditioners weigh hair down in the name of moisture. Not ours.\nThe SHARP Hydrating Conditioner is feather-light, yet deeply reparative —\nrestoring smoothness, sealing split ends, and leaving hair with that elusive, mirror-like shine that turns heads.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 14,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg",
        "image2_url": "",
        "caption": "Hydrating Conditioner",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 15,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/39fbf9e4-e3e0-488a-90cd-762f60351da7_elsobt.jpg",
        "image2_url": "",
        "caption": "Hydrating Conditioner",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 16,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698752/150ddba4-fcf1-4bd2-9443-b797e385de64_vr3tix.jpg",
        "image2_url": "",
        "caption": "Hydrating Conditioner",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 17,
        "kind": "heading",
        "text": "Nourishing Oil Blend — Luxury in a Drop",
        "level": "h2",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 18,
        "kind": "paragraph",
        "text": "Hair oil, elevated. Our blend doesn’t just coat strands — it revives them.\nA silky, nutrient-dense elixir that repairs damage, tames frizz, and infuses hair with a glassy glow.\nOne to two drops is all it takes to step into your day with quiet, radiant confidence.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 19,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698762/2_maw4et.jpg",
        "image2_url": "",
        "caption": "Nourishing Oil Blend",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 20,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698763/3_km7fmm.jpg",
        "image2_url": "",
        "caption": "Nourishing Oil Blend",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 21,
        "kind": "image",
        "text": "",
        "level": "",
        "image1_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698761/1_wax9fy.jpg",
        "image2_url": "",
        "caption": "Nourishing Oil Blend",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 22,
        "kind": "callout",
        "text": "Luxury isn’t more. Luxury is *enough*. Discover the SHARP ritual —\na collection designed to simplify your shelf and amplify your shine.",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    },
    {
        "post_slug": "natural-hair-care",
        "order": 23,
        "kind": "paragraph",
        "text": "✨ Ready to begin your ritual? Explore the full SHARP Natural Hair Care collection → /products/",
        "level": "",
        "image1_url": "",
        "image2_url": "",
        "caption": "",
        "prod_query": ""
    }
]

FX_RATES_DATA = [
    {
        "base": "JOD",
        "quote": "USD",
        "rate": 1.41,
        "updated_at": "2025-09-05T05:04:11.934205+00:00"
    },
    {
        "base": "USD",
        "quote": "PHP",
        "rate": 58.0,
        "updated_at": "2025-09-05T05:04:12.045115+00:00"
    },
    {
        "base": "USD",
        "quote": "EUR",
        "rate": 0.92,
        "updated_at": "2025-09-05T05:04:12.115076+00:00"
    },
    {
        "base": "USD",
        "quote": "GBP",
        "rate": 0.79,
        "updated_at": "2025-09-05T05:04:12.180516+00:00"
    },
    {
        "base": "USD",
        "quote": "AED",
        "rate": 3.6725,
        "updated_at": "2025-09-05T05:04:13.802035+00:00"
    }
]

# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

@transaction.atomic
def seed_database():
    """
    Seed the PostgreSQL database with all exported data.
    This function is idempotent - safe to run multiple times.
    """
    print("=" * 70)
    print("🌱 Seeding PostgreSQL Database")
    print("=" * 70)
    print()
    
    # 1. Create Products
    print("📦 Creating Products...")
    product_map = {}
    for product_data in PRODUCTS_DATA:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults={
                'sku': product_data['sku'] or None,
                'slug': product_data['slug'],
                'short_description': product_data['short_description'],
                'description': product_data['description'],
                'price': Decimal(str(product_data['price'])),
                'image_url': product_data['image_url'] or None,
                'is_active': product_data['is_active'],
                'gallery_csv': product_data['gallery_csv'],
                'is_bundle': product_data['is_bundle'],
                'free_delivery': product_data['free_delivery'],
            }
        )
        product_map[product_data['name']] = product
        if created:
            print(f"   ✅ Created: {product.name}")
        else:
            print(f"   ℹ️  Exists: {product.name}")
    print(f"   Total: {len(product_map)} products\n")
    
    # 2. Create Product Components
    print("🔗 Creating Product Components...")
    components_created = 0
    for comp_data in PRODUCT_COMPONENTS_DATA:
        try:
            parent = product_map.get(comp_data['parent_name'])
            component = product_map.get(comp_data['component_name'])
            
            if not parent or not component:
                print(f"   ⚠️  Skipping: {comp_data['parent_name']} → {comp_data['component_name']} (product not found)")
                continue
            
            comp, created = ProductComponent.objects.get_or_create(
                parent=parent,
                component=component,
                defaults={'quantity': comp_data['quantity']}
            )
            if created:
                components_created += 1
        except Exception as e:
            print(f"   ⚠️  Error creating component: {e}")
    print(f"   Created: {components_created} components\n")
    
    # 3. Create Promo Codes
    print("🎫 Creating Promo Codes...")
    for promo_data in PROMO_CODES_DATA:
        promo, created = PromoCode.objects.get_or_create(
            code=promo_data['code'],
            defaults={
                'type': promo_data['type'],
                'value': Decimal(str(promo_data['value'])),
                'description': promo_data['description'],
                'min_subtotal': Decimal(str(promo_data['min_subtotal'])),
                'max_discount': Decimal(str(promo_data['max_discount'])) if promo_data['max_discount'] else None,
                'countries_csv': promo_data['countries_csv'],
                'starts_at': datetime.fromisoformat(promo_data['starts_at']) if promo_data['starts_at'] else None,
                'ends_at': datetime.fromisoformat(promo_data['ends_at']) if promo_data['ends_at'] else None,
                'active': promo_data['active'],
                'usage_limit': promo_data['usage_limit'],
                'used_count': promo_data['used_count'],
            }
        )
        if created:
            print(f"   ✅ Created: {promo.code}")
        else:
            print(f"   ℹ️  Exists: {promo.code}")
    print()
    
    # 4. Create Orders
    print("📋 Creating Orders...")
    order_map = {}
    for order_data in ORDERS_DATA:
        order, created = Order.objects.get_or_create(
            order_number=order_data['order_number'],
            defaults={
                'created_at': datetime.fromisoformat(order_data['created_at']),
                'updated_at': datetime.fromisoformat(order_data['updated_at']),
                'cancel_reason': order_data['cancel_reason'],
                'full_name': order_data['full_name'],
                'phone': order_data['phone'],
                'email': order_data['email'] or '',
                'address_line1': order_data['address_line1'],
                'city': order_data['city'],
                'province': order_data['province'],
                'zip_code': order_data['zip_code'],
                'country': order_data['country'],
                'shipping_address': order_data['shipping_address'],
                'shipping_address_text': order_data['shipping_address_text'],
                'shipping_method': order_data['shipping_method'],
                'payment_method': order_data['payment_method'],
                'subtotal': Decimal(str(order_data['subtotal'])),
                'shipping_cost': Decimal(str(order_data['shipping_cost'])),
                'discount_total': Decimal(str(order_data['discount_total'])),
                'grand_total': Decimal(str(order_data['grand_total'])),
                'notes': order_data['notes'],
                'status': order_data['status'],
                'zoho_data': order_data['zoho_data'],
                'promo_code': order_data.get('promo_code') or None,
                'promo_label': order_data.get('promo_label') or '',
            }
        )
        order_map[order_data['order_number']] = order
        if created:
            print(f"   ✅ Created: {order.order_number}")
        else:
            print(f"   ℹ️  Exists: {order.order_number}")
    print(f"   Total: {len(order_map)} orders\n")
    
    # 5. Create Order Items
    print("🛒 Creating Order Items...")
    items_created = 0
    for item_data in ORDER_ITEMS_DATA:
        try:
            order = order_map.get(item_data['order_number'])
            product = product_map.get(item_data['product_name'])
            
            if not order or not product:
                print(f"   ⚠️  Skipping: {item_data['name']} (order/product not found)")
                continue
            
            item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                name=item_data['name'],
                defaults={
                    'unit_price': Decimal(str(item_data['unit_price'])),
                    'quantity': item_data['quantity'],
                    'line_total': Decimal(str(item_data['line_total'])),
                    'cancel_reason': item_data['cancel_reason'],
                }
            )
            if created:
                items_created += 1
        except Exception as e:
            print(f"   ⚠️  Error creating order item: {e}")
    print(f"   Created: {items_created} order items\n")
    
    # 6. Create Blog Posts
    print("📝 Creating Blog Posts...")
    post_map = {}
    for post_data in POSTS_DATA:
        post, created = Post.objects.get_or_create(
            slug=post_data['slug'],
            defaults={
                'title': post_data['title'],
                'excerpt': post_data['excerpt'],
                'cover_image_url': post_data['cover_image_url'],
                'published_at': datetime.fromisoformat(post_data['published_at']) if post_data['published_at'] else None,
                'author_name': post_data['author_name'],
            }
        )
        post_map[post_data['slug']] = post
        if created:
            print(f"   ✅ Created: {post.title}")
        else:
            print(f"   ℹ️  Exists: {post.title}")
    print()
    
    # 7. Create Post Blocks
    print("📄 Creating Post Blocks...")
    blocks_created = 0
    for block_data in POST_BLOCKS_DATA:
        try:
            post = post_map.get(block_data['post_slug'])
            if not post:
                print(f"   ⚠️  Skipping block (post not found: {block_data['post_slug']})")
                continue
            
            block, created = PostBlock.objects.get_or_create(
                post=post,
                order=block_data['order'],
                defaults={
                    'kind': block_data['kind'],
                    'text': block_data['text'],
                    'level': block_data['level'],
                    'image1_url': block_data['image1_url'],
                    'image2_url': block_data['image2_url'],
                    'caption': block_data['caption'],
                    'prod_query': block_data['prod_query'],
                }
            )
            if created:
                blocks_created += 1
        except Exception as e:
            print(f"   ⚠️  Error creating post block: {e}")
    print(f"   Created: {blocks_created} post blocks\n")
    
    # 8. Create FX Rates
    print("💱 Creating FX Rates...")
    for fx_data in FX_RATES_DATA:
        fx, created = FxRate.objects.get_or_create(
            base=fx_data['base'],
            quote=fx_data['quote'],
            defaults={
                'rate': Decimal(str(fx_data['rate'])),
            }
        )
        if created:
            print(f"   ✅ Created: {fx.base}/{fx.quote}")
        else:
            print(f"   ℹ️  Exists: {fx.base}/{fx.quote}")
    print()
    
    # Summary
    print("=" * 70)
    print("🎉 Seeding Complete!")
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"   Products: {Product.objects.count()}")
    print(f"   Product Components: {ProductComponent.objects.count()}")
    print(f"   Orders: {Order.objects.count()}")
    print(f"   Order Items: {OrderItem.objects.count()}")
    print(f"   Promo Codes: {PromoCode.objects.count()}")
    print(f"   Blog Posts: {Post.objects.count()}")
    print(f"   Post Blocks: {PostBlock.objects.count()}")
    print(f"   FX Rates: {FxRate.objects.count()}")
    print("=" * 70)


if __name__ == "__main__":
    seed_database()
