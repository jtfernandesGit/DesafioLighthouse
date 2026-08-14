-- 1.1 Quantidade total de linhas tabela orders
SELECT
    COUNT(*) AS total_rows,
    MIN(created_at) AS min_date,
    MAX(created_at) AS max_date,
    MIN(total) AS min_total,
    MAX(total) AS max_total,
    AVG(total::numeric) AS avg_total
FROM raw.orders;