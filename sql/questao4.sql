-- Questão 4.1 - Calcule o Ticket Médio e a Diversidade de Categorias para cada customer_id.
WITH ticket AS (
    SELECT
        customer_id,
        ROUND(AVG(total::NUMERIC), 2) AS ticket_medio
    FROM raw.orders
    GROUP BY customer_id
),

categorias AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM raw.orders o
    JOIN raw.order_items oi
        ON oi.order_id = o.id
    JOIN raw.product_variants pv
        ON pv.id = oi.product_variant_id
    JOIN raw.products p
        ON p.id = pv.product_id
    GROUP BY o.customer_id
)

SELECT
    t.customer_id,
    t.ticket_medio,
    c.diversidade_categorias
FROM ticket t
JOIN categorias c
    ON c.customer_id = t.customer_id
ORDER BY t.ticket_medio DESC;

-- Questão 4.2: Filtre os 10 clientes com o maior Ticket Médio que atendam ao critério de diversidade (13 ou + categorias).
WITH ticket AS (
    SELECT
        customer_id,
        ROUND(AVG(total::NUMERIC), 2) AS ticket_medio
    FROM raw.orders
    GROUP BY customer_id
),

categorias AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM raw.orders o
    JOIN raw.order_items oi
        ON oi.order_id = o.id
    JOIN raw.product_variants pv
        ON pv.id = oi.product_variant_id
    JOIN raw.products p
        ON p.id = pv.product_id
    GROUP BY o.customer_id
)

SELECT
    t.customer_id,
    t.ticket_medio,
    c.diversidade_categorias
FROM ticket t
JOIN categorias c
    ON c.customer_id = t.customer_id
WHERE c.diversidade_categorias >= 13
ORDER BY t.ticket_medio DESC
LIMIT 10;

-- Questão 4.3: Para este grupo específico de 10 clientes, identifique qual categoria de produto concentra a maior quantidade total de itens comprados (sum(quantity))
WITH ticket AS (
    SELECT
        customer_id,
        ROUND(AVG(total::NUMERIC), 2) AS ticket_medio
    FROM raw.orders
    GROUP BY customer_id
),

categorias AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM raw.orders o
    JOIN raw.order_items oi
        ON oi.order_id = o.id
    JOIN raw.product_variants pv
        ON pv.id = oi.product_variant_id
    JOIN raw.products p
        ON p.id = pv.product_id
    GROUP BY o.customer_id
),

top_10_clientes AS (
    SELECT
        t.customer_id,
        t.ticket_medio,
        c.diversidade_categorias
    FROM ticket t
    JOIN categorias c
        ON c.customer_id = t.customer_id
    WHERE c.diversidade_categorias >= 13
    ORDER BY t.ticket_medio DESC
    LIMIT 10
)

SELECT
    p.category_id,
    c.name AS categoria,
    SUM(oi.quantity::NUMERIC) AS total_itens_comprados
FROM top_10_clientes top10
JOIN raw.orders o
    ON o.customer_id = top10.customer_id
JOIN raw.order_items oi
    ON oi.order_id = o.id
JOIN raw.product_variants pv
    ON pv.id = oi.product_variant_id
JOIN raw.products p
    ON p.id = pv.product_id
JOIN raw.categories c
    ON c.id = p.category_id
GROUP BY
    p.category_id,
    c.name
ORDER BY total_itens_comprados DESC
LIMIT 1;