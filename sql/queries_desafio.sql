-- 1.1 Quantidade total de linhas tabela orders
SELECT
    COUNT(*) AS total_rows,
    MIN(created_at) AS min_date,
    MAX(created_at) AS max_date,
    MIN(total) AS min_total,
    MAX(total) AS max_total,
    AVG(total::numeric) AS avg_total
FROM raw.orders;

-- 1.2 Quantidade colunas
SELECT COUNT(*) AS total_colunas
FROM information_schema.columns
WHERE table_schema = 'raw'
  AND table_name = 'orders';

--1.3 Intervalo de datas analisado (data mínima e máxima) da coluna created_at
SELECT
    MIN(created_at) AS data_minima,
    MAX(created_at) AS data_maxima
FROM raw.orders;

-- 3.2 Total de linhas somadas das seguintes tabelas: customers, orders, order_items e payments
SELECT 'customers' AS tabela, COUNT(*) AS total_linhas
FROM raw.customers

UNION ALL

SELECT 'orders', COUNT(*)
FROM raw.orders

UNION ALL

SELECT 'order_items', COUNT(*)
FROM raw.order_items

UNION ALL

SELECT 'payments', COUNT(*)
FROM raw.payments

UNION ALL

SELECT 'TOTAL',
       (SELECT COUNT(*) FROM raw.customers) +
       (SELECT COUNT(*) FROM raw.orders) +
       (SELECT COUNT(*) FROM raw.order_items) +
       (SELECT COUNT(*) FROM raw.payments);

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

-- Questão 5 - dimensão de calendário

-- 5.1 Construa uma dimensão de datas utilizando sql
WITH limites AS (
    SELECT
        MIN(placed_at::date) AS data_inicial,
        MAX(placed_at::date) AS data_final
    FROM raw.orders
)

SELECT
    data AS data,
    EXTRACT(ISODOW FROM data) AS numero_dia_semana,
    CASE EXTRACT(ISODOW FROM data)
        WHEN 1 THEN 'Segunda-feira'
        WHEN 2 THEN 'Terça-feira'
        WHEN 3 THEN 'Quarta-feira'
        WHEN 4 THEN 'Quinta-feira'
        WHEN 5 THEN 'Sexta-feira'
        WHEN 6 THEN 'Sábado'
        WHEN 7 THEN 'Domingo'
    END AS dia_semana
FROM limites,
GENERATE_SERIES(
    data_inicial,
    data_final,
    INTERVAL '1 day'
) AS calendario(data)
ORDER BY data;

-- 5.2 - Cruzar calendário com as vendas
WITH limites AS (
    SELECT
        MIN(placed_at::date) AS data_inicial,
        MAX(placed_at::date) AS data_final
    FROM raw.orders
),

calendario AS (
    SELECT
        data::date AS data,
        EXTRACT(ISODOW FROM data)::int AS numero_dia_semana,
        CASE EXTRACT(ISODOW FROM data)
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
            WHEN 7 THEN 'Domingo'
        END AS dia_semana
    FROM limites,
    GENERATE_SERIES(
        data_inicial,
        data_final,
        INTERVAL '1 day'
    ) AS gs(data)
),

vendas_diarias AS (
    SELECT
        o.placed_at::date AS data,
        SUM(o.total::numeric) AS vendas_do_dia
    FROM raw.orders o
    WHERE LOWER(o.channel) = 'pos'
    GROUP BY o.placed_at::date
),

calendario_vendas AS (
    SELECT
        c.data,
        c.numero_dia_semana,
        c.dia_semana,
        COALESCE(v.vendas_do_dia, 0) AS vendas_do_dia
    FROM calendario c
    LEFT JOIN vendas_diarias v
        ON c.data = v.data
)

SELECT
    numero_dia_semana,
    dia_semana,
    ROUND(AVG(vendas_do_dia), 2) AS media_vendas_diarias
FROM calendario_vendas
GROUP BY
    numero_dia_semana,
    dia_semana
ORDER BY
    media_vendas_diarias ASC;