
    -- 1. Top priority queue
            SELECT text, emotion, topic_name, priority_score, priority_level
            FROM topic_assignments
            ORDER BY priority_score DESC
            LIMIT 10;
       
    -- 2. Workload by priority level
            SELECT priority_level, COUNT(*) AS n_items
            FROM topic_assignments
            GROUP BY priority_level
            ORDER BY n_items DESC;
        
    -- 3. Average priority by emotion
            SELECT emotion, ROUND(AVG(priority_score), 2) AS avg_priority, COUNT(*) AS n
            FROM topic_assignments
            GROUP BY emotion
            ORDER BY avg_priority DESC;
       
    -- 4. Top 5 topics by average priority
            SELECT topic_name, ROUND(AVG(priority_score), 2) AS avg_priority, COUNT(*) AS n
            FROM topic_assignments
            GROUP BY topic_name
            ORDER BY avg_priority DESC
            LIMIT 5;
       
    -- 5. Emotion distribution
            SELECT emotion, COUNT(*) AS n,
                   ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM topic_assignments), 2) AS pct
            FROM topic_assignments
            GROUP BY emotion
            ORDER BY n DESC;
       
    -- 6. Topic distribution
            SELECT topic_name, COUNT(*) AS n
            FROM topic_assignments
            GROUP BY topic_name
            ORDER BY n DESC;
       
    -- 7. High-priority items per emotion
            SELECT emotion, priority_level, COUNT(*) AS n
            FROM topic_assignments
            GROUP BY emotion, priority_level
            ORDER BY emotion, priority_level;
       
    -- 8. Urgency-keyword hit rate per emotion
            SELECT emotion,
                   ROUND(100.0 * SUM(CASE WHEN business_score = 100 THEN 1 ELSE 0 END) / COUNT(*), 2) AS urgency_hit_pct
            FROM topic_assignments
            GROUP BY emotion
            ORDER BY urgency_hit_pct DESC;
       
    -- 9. Top emotion+topic combinations by priority
            SELECT emotion, topic_name, ROUND(AVG(priority_score), 2) AS avg_priority, COUNT(*) AS n
            FROM topic_assignments
            GROUP BY emotion, topic_name
            ORDER BY avg_priority DESC
            LIMIT 5;
       
    -- 10. Best models overall
            SELECT Model, "Macro F1"
            FROM model_comparison
            ORDER BY "Macro F1" DESC
            LIMIT 3;
       
    -- 11. Average metrics by model type
            SELECT "Model Type", ROUND(AVG(Accuracy), 4) AS avg_accuracy, ROUND(AVG("Macro F1"), 4) AS avg_macro_f1
            FROM model_comparison
            GROUP BY "Model Type"
            ORDER BY avg_macro_f1 DESC;
       
    -- 12. Models above an F1 quality bar
            SELECT Model, "Macro F1"
            FROM model_comparison
            WHERE "Macro F1" >= 0.80
            ORDER BY "Macro F1" DESC;
      
    -- 13. Macro vs Weighted F1 gap
            SELECT Model, ROUND("Weighted F1" - "Macro F1", 4) AS f1_gap
            FROM model_comparison
            ORDER BY f1_gap DESC;
      
    -- 14. Best classical configuration
            SELECT "N-gram", "Max Features", Model, "Macro F1"
            FROM classical_sweep
            ORDER BY "Macro F1" DESC
            LIMIT 1;
       
    -- 15. Effect of n-gram range
            SELECT "N-gram", ROUND(AVG("Macro F1"), 4) AS avg_macro_f1
            FROM classical_sweep
            GROUP BY "N-gram"
            ORDER BY avg_macro_f1 DESC;
       
    -- 16. Effect of vocabulary cap
            SELECT "Max Features", ROUND(AVG("Macro F1"), 4) AS avg_macro_f1
            FROM classical_sweep
            GROUP BY "Max Features"
            ORDER BY avg_macro_f1 DESC;
       
    -- 17. Human review queue emotion breakdown
            SELECT emotion, COUNT(*) AS n
            FROM human_review_queue
            GROUP BY emotion
            ORDER BY n DESC;
       
    -- 18. Business score by priority level
            SELECT priority_level, ROUND(AVG(business_score), 2) AS avg_business_score
            FROM topic_assignments
            GROUP BY priority_level;
       
    -- 19. Most urgent topic within each emotion
            SELECT emotion, topic_name, COUNT(*) AS n, ROUND(AVG(priority_score), 2) AS avg_priority
            FROM topic_assignments
            WHERE priority_level = 'High'
            GROUP BY emotion, topic_name
            ORDER BY emotion, n DESC;
       
    -- 20. Possible missed-urgent items
            SELECT text, emotion, topic_name, priority_score, priority_level
            FROM topic_assignments
            WHERE text LIKE '%urgent%' AND priority_level != 'High'
            ORDER BY priority_score DESC
            LIMIT 10;
       
    -- 21. دقة كل موديل (JOIN + CASE)
            SELECT pm.model_name,
                   ROUND(AVG(CASE WHEN mp.predicted_label = pt.true_label THEN 1.0 ELSE 0.0 END), 4) AS accuracy
            FROM model_predictions mp
            JOIN predictions_texts pt ON mp.text_id = pt.text_id
            JOIN predictions_models pm ON mp.model_id = pm.model_id
            GROUP BY pm.model_name
            ORDER BY accuracy DESC;
       
    -- 22. ترتيب الموديلات (Window Function: RANK)
            SELECT model_name, accuracy,
                   RANK() OVER (ORDER BY accuracy DESC) AS rank
            FROM (
                SELECT pm.model_name,
                       AVG(CASE WHEN mp.predicted_label = pt.true_label THEN 1.0 ELSE 0.0 END) AS accuracy
                FROM model_predictions mp
                JOIN predictions_texts pt ON mp.text_id = pt.text_id
                JOIN predictions_models pm ON mp.model_id = pm.model_id
                GROUP BY pm.model_name
            );
       
    -- 23. أحسن موديل بس (CTE)
            WITH model_accuracy AS (
                SELECT pm.model_name,
                       AVG(CASE WHEN mp.predicted_label = pt.true_label THEN 1.0 ELSE 0.0 END) AS accuracy
                FROM model_predictions mp
                JOIN predictions_texts pt ON mp.text_id = pt.text_id
                JOIN predictions_models pm ON mp.model_id = pm.model_id
                GROUP BY pm.model_name
            )
            SELECT * FROM model_accuracy ORDER BY accuracy DESC LIMIT 1;
       
    -- 24. أكتر 5 أزواج (حقيقي -> متوقع) غلط عبر كل الموديلات
            SELECT pt.true_label, mp.predicted_label, COUNT(*) AS mistakes
            FROM model_predictions mp
            JOIN predictions_texts pt ON mp.text_id = pt.text_id
            WHERE mp.predicted_label != pt.true_label
            GROUP BY pt.true_label, mp.predicted_label
            ORDER BY mistakes DESC
            LIMIT 5;
       
    -- 25. متوسط طول النص لكل فئة حقيقية
            SELECT true_label, ROUND(AVG(LENGTH(text)), 2) AS avg_char_length
            FROM predictions_texts
            GROUP BY true_label
            ORDER BY avg_char_length DESC;
        
    -- 26. عدد النصوص اللي كل الموديلات اتفقت عليها صح
            SELECT COUNT(DISTINCT pt.text_id) AS unanimous_correct
            FROM predictions_texts pt
            WHERE pt.text_id IN (
                SELECT mp.text_id
                FROM model_predictions mp
                JOIN predictions_texts pt2 ON mp.text_id = pt2.text_id
                WHERE mp.predicted_label = pt2.true_label
                GROUP BY mp.text_id
                HAVING COUNT(DISTINCT mp.model_id) = (SELECT COUNT(*) FROM predictions_models)
            );
        
    -- 27. نسبة الخطأ لكل موديل في الفئة الأقل تمثيلاً
            WITH rarest AS (
                SELECT true_label, COUNT(*) AS n
                FROM predictions_texts
                GROUP BY true_label
                ORDER BY n ASC
                LIMIT 1
            )
            SELECT pm.model_name,
                   ROUND(AVG(CASE WHEN mp.predicted_label != pt.true_label THEN 1.0 ELSE 0.0 END), 4) AS error_rate
            FROM model_predictions mp
            JOIN predictions_texts pt ON mp.text_id = pt.text_id
            JOIN predictions_models pm ON mp.model_id = pm.model_id
            WHERE pt.true_label = (SELECT true_label FROM rarest)
            GROUP BY pm.model_name
            ORDER BY error_rate;
        
    -- 28. أطول 5 نصوص مع تصنيفها الحقيقي
            SELECT text, true_label, LENGTH(text) AS char_length
            FROM predictions_texts
            ORDER BY char_length DESC
            LIMIT 5;
       
    -- 29. متوسط تراكمي للدقة عبر الموديلات (Running Average)
            SELECT model_name, accuracy,
                   ROUND(AVG(accuracy) OVER (
                       ORDER BY accuracy ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                   ), 4) AS running_avg
            FROM (
                SELECT pm.model_name,
                       AVG(CASE WHEN mp.predicted_label = pt.true_label THEN 1.0 ELSE 0.0 END) AS accuracy
                FROM model_predictions mp
                JOIN predictions_texts pt ON mp.text_id = pt.text_id
                JOIN predictions_models pm ON mp.model_id = pm.model_id
                GROUP BY pm.model_name
            );
        
    -- 30. أحسن موديل لكل فئة حقيقية على حدة (Window Function: PARTITION BY)
        
            SELECT true_label, model_name, ROUND(accuracy, 4) AS accuracy
            FROM (
                SELECT pt.true_label, pm.model_name,
                       AVG(CASE WHEN mp.predicted_label = pt.true_label THEN 1.0 ELSE 0.0 END) AS accuracy,
                       RANK() OVER (
                           PARTITION BY pt.true_label
                           ORDER BY AVG(CASE WHEN mp.predicted_label = pt.true_label THEN 1.0 ELSE 0.0 END) DESC
                       ) AS rnk
                FROM model_predictions mp
                JOIN predictions_texts pt ON mp.text_id = pt.text_id
                JOIN predictions_models pm ON mp.model_id = pm.model_id
                GROUP BY pt.true_label, pm.model_name
            )
            WHERE rnk = 1
            ORDER BY true_label;
        
