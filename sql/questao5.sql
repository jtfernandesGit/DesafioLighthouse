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