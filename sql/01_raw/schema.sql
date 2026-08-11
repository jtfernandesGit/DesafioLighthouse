-- ============================================================
-- LH NAUTICAL - RAW SCHEMA
-- ============================================================
--
-- Arquivo gerado automaticamente por generate_schema.py
--
-- Camada RAW:
--     Os dados são preservados sem transformação.
--
-- Os campos são armazenados como TEXT propositalmente.
-- Conversões de tipo devem ocorrer posteriormente na camada
-- STAGING.
--
-- Generated tables:
-- 
--     addresses
--     attributes
--     brands
--     categories
--     customers
--     employees
--     fiscal_invoices
--     goods_receipt_items
--     goods_receipts
--     locations
--     order_items
--     orders
--     payments
--     product_suppliers
--     product_variants
--     products
--     purchase_order_items
--     purchase_orders
--     return_items
--     returns
--     stock_levels
--     stock_movements
--     suppliers
--     variant_attribute_values

-- ============================================================

CREATE SCHEMA IF NOT EXISTS "raw";


-- ============================================================
-- SOURCE: addresses.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."addresses"
(
    "id" TEXT,
    "customer_id" TEXT,
    "address_type" TEXT,
    "postal_code" TEXT,
    "street" TEXT,
    "number" TEXT,
    "complement" TEXT,
    "district" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "is_primary" TEXT
);


-- ============================================================
-- SOURCE: attributes.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."attributes"
(
    "id" TEXT,
    "name" TEXT,
    "data_type" TEXT
);


-- ============================================================
-- SOURCE: brands.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."brands"
(
    "id" TEXT,
    "name" TEXT,
    "country" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: categories.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."categories"
(
    "id" TEXT,
    "name" TEXT,
    "slug" TEXT,
    "parent_category_id" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: customers.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."customers"
(
    "id" TEXT,
    "person_type" TEXT,
    "legal_name" TEXT,
    "trade_name" TEXT,
    "tax_id" TEXT,
    "state_registration" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: employees.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."employees"
(
    "id" TEXT,
    "full_name" TEXT,
    "cpf" TEXT,
    "email" TEXT,
    "role" TEXT,
    "primary_location_id" TEXT,
    "hire_date" TEXT,
    "termination_date" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: fiscal_invoices.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."fiscal_invoices"
(
    "id" TEXT,
    "order_id" TEXT,
    "nfe_number" TEXT,
    "nfe_access_key" TEXT,
    "series" TEXT,
    "issued_at" TEXT,
    "status" TEXT,
    "total_amount" TEXT,
    "xml_storage_uri" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: goods_receipt_items.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."goods_receipt_items"
(
    "id" TEXT,
    "goods_receipt_id" TEXT,
    "purchase_order_item_id" TEXT,
    "quantity_received" TEXT
);


-- ============================================================
-- SOURCE: goods_receipts.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."goods_receipts"
(
    "id" TEXT,
    "purchase_order_id" TEXT,
    "received_by_employee_id" TEXT,
    "received_at" TEXT,
    "notes" TEXT,
    "created_at" TEXT
);


-- ============================================================
-- SOURCE: locations.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."locations"
(
    "id" TEXT,
    "name" TEXT,
    "location_type" TEXT,
    "postal_code" TEXT,
    "street" TEXT,
    "number" TEXT,
    "complement" TEXT,
    "district" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: order_items.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."order_items"
(
    "id" TEXT,
    "order_id" TEXT,
    "product_variant_id" TEXT,
    "quantity" TEXT,
    "unit_price" TEXT,
    "icms_rate" TEXT,
    "ipi_rate" TEXT,
    "line_total" TEXT
);


-- ============================================================
-- SOURCE: orders.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."orders"
(
    "id" TEXT,
    "order_number" TEXT,
    "channel" TEXT,
    "customer_id" TEXT,
    "salesperson_id" TEXT,
    "location_id" TEXT,
    "status" TEXT,
    "subtotal" TEXT,
    "discount_amount" TEXT,
    "total" TEXT,
    "placed_at" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: payments.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."payments"
(
    "id" TEXT,
    "order_id" TEXT,
    "method" TEXT,
    "installments" TEXT,
    "amount" TEXT,
    "status" TEXT,
    "paid_at" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: product_suppliers.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."product_suppliers"
(
    "product_variant_id" TEXT,
    "supplier_id" TEXT,
    "supplier_sku" TEXT,
    "last_quoted_cost" TEXT,
    "lead_time_days" TEXT,
    "is_preferred" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: product_variants.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."product_variants"
(
    "id" TEXT,
    "product_id" TEXT,
    "sku" TEXT,
    "barcode_ean" TEXT,
    "sale_price" TEXT,
    "cost_price" TEXT,
    "weight_kg" TEXT,
    "icms_rate" TEXT,
    "ipi_rate" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: products.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."products"
(
    "id" TEXT,
    "name" TEXT,
    "description" TEXT,
    "brand_id" TEXT,
    "category_id" TEXT,
    "ncm_code" TEXT,
    "unit_of_measure" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: purchase_order_items.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."purchase_order_items"
(
    "id" TEXT,
    "purchase_order_id" TEXT,
    "product_variant_id" TEXT,
    "quantity_ordered" TEXT,
    "unit_cost" TEXT,
    "line_total" TEXT
);


-- ============================================================
-- SOURCE: purchase_orders.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."purchase_orders"
(
    "id" TEXT,
    "po_number" TEXT,
    "supplier_id" TEXT,
    "buyer_id" TEXT,
    "destination_location_id" TEXT,
    "status" TEXT,
    "currency" TEXT,
    "subtotal" TEXT,
    "total" TEXT,
    "placed_at" TEXT,
    "expected_delivery_at" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: return_items.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."return_items"
(
    "id" TEXT,
    "return_id" TEXT,
    "order_item_id" TEXT,
    "quantity" TEXT,
    "action" TEXT,
    "exchange_variant_id" TEXT,
    "unit_refund_amount" TEXT
);


-- ============================================================
-- SOURCE: returns.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."returns"
(
    "id" TEXT,
    "return_number" TEXT,
    "order_id" TEXT,
    "customer_id" TEXT,
    "received_at_location_id" TEXT,
    "status" TEXT,
    "reason" TEXT,
    "total_refund_amount" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: stock_levels.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."stock_levels"
(
    "product_variant_id" TEXT,
    "location_id" TEXT,
    "quantity_on_hand" TEXT,
    "reorder_point" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: stock_movements.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."stock_movements"
(
    "id" TEXT,
    "product_variant_id" TEXT,
    "location_id" TEXT,
    "movement_type" TEXT,
    "quantity" TEXT,
    "reference_table" TEXT,
    "reference_id" TEXT,
    "employee_id" TEXT,
    "notes" TEXT,
    "occurred_at" TEXT,
    "created_at" TEXT
);


-- ============================================================
-- SOURCE: suppliers.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."suppliers"
(
    "id" TEXT,
    "legal_name" TEXT,
    "trade_name" TEXT,
    "country" TEXT,
    "tax_id" TEXT,
    "tax_id_type" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "contact_name" TEXT,
    "is_active" TEXT,
    "created_at" TEXT,
    "updated_at" TEXT
);


-- ============================================================
-- SOURCE: variant_attribute_values.csv
-- ============================================================

CREATE TABLE IF NOT EXISTS "raw"."variant_attribute_values"
(
    "product_variant_id" TEXT,
    "attribute_id" TEXT,
    "value" TEXT
);
