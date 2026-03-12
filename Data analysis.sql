--5.Brand Affinity Score by Class
SELECT
    class_label,
    ROUND(AVG((branded_quality + brand__is_confidence +
               mumbai_brand_influence + mall_influence) / 4.0), 2) AS brand_affinity_score,
    ROUND(AVG(branded_quality), 2)          AS avg_branded_quality,
    ROUND(AVG(brand__is_confidence), 2)     AS avg_brand_confidence,
    ROUND(AVG(mumbai_brand_influence), 2)   AS avg_brand_influence,
    ROUND(AVG(mall_influence), 2)           AS avg_mall_influence
FROM fact_respondents
GROUP BY class_label
ORDER BY brand_affinity_score DESC;

--6.Brand Affinity Score by Area
SELECT
    area_of_residence,
    ROUND(AVG((branded_quality + brand__is_confidence +
               mumbai_brand_influence + mall_influence) / 4.0), 2) AS brand_affinity_score,
    COUNT(*) AS total_respondents
FROM fact_respondents
GROUP BY area_of_residence
ORDER BY brand_affinity_score DESC;

--7.Brand Affinity Ranked within each Class by Area
SELECT
    class_label,
    area_of_residence,
    ROUND(AVG((branded_quality + brand__is_confidence +
               mumbai_brand_influence + mall_influence) / 4.0), 2) AS brand_affinity_score,
    RANK() OVER (
        PARTITION BY class_label
        ORDER BY AVG((branded_quality + brand__is_confidence +
                      mumbai_brand_influence + mall_influence) / 4.0) DESC
    ) AS rank_within_class
FROM fact_respondents
GROUP BY class_label, area_of_residence
ORDER BY brand_affinity_score DESC;

--8.Who believes branded = better quality, by class
SELECT
    class_label,
    ROUND(AVG(branded_quality), 2)      AS avg_quality_belief,
    ROUND(AVG(unbranded_is_vfm), 2)     AS avg_vfm_belief,
    ROUND(AVG(branded_quality) - AVG(unbranded_is_vfm), 2) AS brand_vs_value_gap
FROM fact_respondents
GROUP BY class_label
ORDER BY brand_vs_value_gap DESC;

--9.Overall Buying Behaviour Distribution
SELECT
    CASE buying_behaviour
        WHEN 1 THEN 'Smart Spender'
        WHEN 2 THEN 'Status-oriented'
        WHEN 3 THEN 'Combination'
        WHEN 4 THEN 'Depends on situation'
    END AS behaviour_label,
    COUNT(*) AS total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM fact_respondents
GROUP BY buying_behaviour
ORDER BY total DESC;

--10.Buying Behaviour breakdown by Class
SELECT
    class_label,
    ROUND(COUNT(CASE WHEN buying_behaviour = 1 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_smart_spender,
    ROUND(COUNT(CASE WHEN buying_behaviour = 2 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_status_oriented,
    ROUND(COUNT(CASE WHEN buying_behaviour = 3 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_combination,
    ROUND(COUNT(CASE WHEN buying_behaviour = 4 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_depends
FROM fact_respondents
GROUP BY class_label
ORDER BY pct_status_oriented DESC;

--11.Status-oriented buyers area
SELECT
    area_of_residence,
    COUNT(*) AS status_buyers,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_all_status_buyers
FROM fact_respondents
WHERE buying_behaviour = 2
GROUP BY area_of_residence
ORDER BY status_buyers DESC;

--12.Buying Behaviour vs Brand Affinity Score
WITH behaviour_affinity AS (
    SELECT
        CASE buying_behaviour
            WHEN 1 THEN 'Smart Spender'
            WHEN 2 THEN 'Status-oriented'
            WHEN 3 THEN 'Combination'
            WHEN 4 THEN 'Depends on situation'
        END AS behaviour_label,
        ROUND(AVG((branded_quality + brand__is_confidence +
                   mumbai_brand_influence + mall_influence) / 4.0), 2) AS brand_affinity_score,
        ROUND(AVG(price_consciousness), 2) AS avg_price_consciousness,
        COUNT(*) AS total
    FROM fact_respondents
    GROUP BY buying_behaviour
)
SELECT * FROM behaviour_affinity
ORDER BY brand_affinity_score DESC;

--13.Overall Factor Frequency
SELECT 'Price' AS factor,                SUM(factor_price) AS total_mentions   FROM fact_respondents
UNION ALL SELECT 'Quality',              SUM(factor_quality)                   FROM fact_respondents
UNION ALL SELECT 'Brand name',           SUM(factor_brand_name)                FROM fact_respondents
UNION ALL SELECT 'Advertisement',        SUM(factor_advertisement)             FROM fact_respondents
UNION ALL SELECT 'Social status',        SUM(factor_social_status)             FROM fact_respondents
UNION ALL SELECT 'Recommendations',      SUM(factor_recommendations_from_others) FROM fact_respondents
ORDER BY total_mentions DESC;

--14.Factor breakdown by Class
SELECT
    class_label,
    SUM(factor_price)                       AS price,
    SUM(factor_quality)                     AS quality,
    SUM(factor_brand_name)                  AS brand_name,
    SUM(factor_advertisement)               AS advertisement,
    SUM(factor_social_status)               AS social_status,
    SUM(factor_recommendations_from_others) AS recommendations
FROM fact_respondents
GROUP BY class_label
ORDER BY class_label;

--15.Top factor per class
WITH factor_counts AS (
    SELECT class_label, 'Price'AS factor,            SUM(factor_price) AS mentions        FROM fact_respondents GROUP BY class_label
    UNION ALL
    SELECT class_label, 'Quality',                   SUM(factor_quality)                  FROM fact_respondents GROUP BY class_label
    UNION ALL
    SELECT class_label, 'Brand name',                SUM(factor_brand_name)               FROM fact_respondents GROUP BY class_label
    UNION ALL
    SELECT class_label, 'Advertisement',             SUM(factor_advertisement)            FROM fact_respondents GROUP BY class_label
    UNION ALL
    SELECT class_label, 'Social status',             SUM(factor_social_status)            FROM fact_respondents GROUP BY class_label
    UNION ALL
    SELECT class_label, 'Recommendations',           SUM(factor_recommendations_from_others) FROM fact_respondents GROUP BY class_label
),
ranked AS (
    SELECT *,
        RANK() OVER (PARTITION BY class_label ORDER BY mentions DESC) AS rnk
    FROM factor_counts
)
SELECT class_label, factor, mentions
FROM ranked
WHERE rnk = 1
ORDER BY mentions DESC;

--16.Price + Brand name cited together by class
SELECT
    class_label,
    COUNT(*) AS respondents_citing_both,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM fact_respondents
WHERE factor_price = 1 AND factor_brand_name = 1
GROUP BY class_label
ORDER BY respondents_citing_both DESC;

--17.Price consciousness vs social status belief by class
SELECT
    class_label,
    ROUND(AVG(price_consciousness), 2)      AS avg_price_consciousness,
    ROUND(AVG(branded_is_social_status), 2) AS avg_social_status_belief,
    ROUND(AVG(price_consciousness) -
          AVG(branded_is_social_status), 2) AS price_vs_status_gap
FROM fact_respondents
GROUP BY class_label
ORDER BY price_vs_status_gap DESC;

--18.Correlation: Income Rank vs Brand Affinity
SELECT ROUND(CORR(
    CASE monthly_income
        WHEN 'Not applicable'    THEN 1
        WHEN 'Below 20,000'      THEN 2
        WHEN '20,001 – 40,000'  THEN 3
        WHEN '40,001 – 60,000'  THEN 4
        WHEN 'Above 60,000'      THEN 5
    END,
    (branded_quality + brand__is_confidence +
     mumbai_brand_influence + mall_influence) / 4.0
)::NUMERIC, 4) AS income_brand_correlation
FROM fact_respondents;

--19.Shopping Frequency vs Buying Behaviour
SELECT
    CASE buying_behaviour
        WHEN 1 THEN 'Smart Spender'
        WHEN 2 THEN 'Status-oriented'
        WHEN 3 THEN 'Combination'
        WHEN 4 THEN 'Depends on situation'
    END AS behaviour_label,
    ROUND(AVG(shopping_frequency), 2) AS avg_shopping_frequency,
    COUNT(*) AS total
FROM fact_respondents
GROUP BY buying_behaviour
ORDER BY avg_shopping_frequency DESC;

--20.Education Level vs Brand Affinity
SELECT
    education_level,
    ROUND(AVG((branded_quality + brand__is_confidence +
               mumbai_brand_influence + mall_influence) / 4.0), 2) AS brand_affinity_score,
    ROUND(AVG(price_consciousness), 2) AS avg_price_consciousness,
    COUNT(*) AS total
FROM fact_respondents
GROUP BY education_level
ORDER BY brand_affinity_score DESC;

--21. Gender vs Buying Behaviour
SELECT
    CASE gender
        WHEN 1 THEN 'Male'
        WHEN 2 THEN 'Female'
        WHEN 3 THEN 'Prefer not to say'
    END AS gender_label,
    ROUND(COUNT(CASE WHEN buying_behaviour = 1 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_smart_spender,
    ROUND(COUNT(CASE WHEN buying_behaviour = 2 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_status_oriented,
    ROUND(COUNT(CASE WHEN buying_behaviour = 3 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_combination,
    ROUND(COUNT(CASE WHEN buying_behaviour = 4 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_depends
FROM fact_respondents
GROUP BY gender
ORDER BY gender;

--22.Category Preference by Class
SELECT
    class_label,
    ROUND(SUM(cat_clothing)               * 100.0 / COUNT(*), 1) AS pct_branded_clothing,
    ROUND(SUM(cat_electronics)            * 100.0 / COUNT(*), 1) AS pct_branded_electronics,
    ROUND(SUM(cat_footwear)               * 100.0 / COUNT(*), 1) AS pct_branded_footwear,
    ROUND(SUM(cat_groceries)              * 100.0 / COUNT(*), 1) AS pct_branded_groceries,
    ROUND(SUM(cat_personal_care_products) * 100.0 / COUNT(*), 1) AS pct_branded_personal_care,
    COUNT(*) AS total_respondents
FROM fact_respondents
GROUP BY class_label
ORDER BY class_label;