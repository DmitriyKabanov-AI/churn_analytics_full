-- Начинаем транзакцию (все изменения после COMMIT/ROLLBACK)
BEGIN;

-- Проверка таблиц
DO $$
BEGIN
    -- Таблица users
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Таблица users отсутствует';
    END IF;
    -- Таблица subscriptions
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        RAISE EXCEPTION 'Таблица subscriptions отсутствует';
    END IF;
    -- Таблица events
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'events') THEN
        RAISE EXCEPTION 'Таблица events отсутствует';
    END IF;
    -- Таблица ltv
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ltv') THEN
        RAISE EXCEPTION 'Таблица ltv отсутствует';
    END IF;
    -- Таблица daily_metrics
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'daily_metrics') THEN
        RAISE EXCEPTION 'Таблица daily_metrics отсутствует';
    END IF;

    -- Проверка ключевых колонок
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'income') THEN
        RAISE EXCEPTION 'Колонка income в users отсутствует';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'plan') THEN
        RAISE EXCEPTION 'Колонка plan в users отсутствует';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'end_date') THEN
        RAISE EXCEPTION 'Колонка end_date в subscriptions отсутствует';
    END IF;

    RAISE NOTICE '✅ Проверка схемы пройдена';
END $$;

-- Проверка функции generate_churn_data (вызовем с маленькими числами, откатим)
DO $$
BEGIN
    PERFORM generate_churn_data(1, 10);
    RAISE NOTICE '✅ Функция generate_churn_data работает';
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'Ошибка в generate_churn_data: %', SQLERRM;
END $$;

-- Откатываем транзакцию (данные не меняются)
ROLLBACK;