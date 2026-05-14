{% macro calculate_yoy_growth(current_metric, previous_metric) %}
    CASE
        WHEN {{ previous_metric }} = 0 OR {{ previous_metric }} IS NULL THEN 0
        ELSE (({{ current_metric }} - {{ previous_metric }}) * 100.0) / {{ previous_metric }}
    END
{% endmacro %}
