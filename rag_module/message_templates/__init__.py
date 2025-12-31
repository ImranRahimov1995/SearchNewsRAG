"""Multilingual message templates for handlers."""

TALK_MESSAGES = {
    "az": """Salam! Mən Azərbaycan xəbərləri üzrə AI köməkçisiyəm.

Nə edə bilərəm:
• Xəbərləri axtarmaq və təhlil etmək
• Hadisələr, şəxslər, təşkilatlar haqqında məlumat vermək
• İl, ay, kateqoriya üzrə statistika təqdim etmək
• Mühüm xəbərləri seçmək

Nümunə suallar:
• "Bakıda bu gün nə olub?"
• "İlham Əliyev haqqında son xəbərlər"
• "2025-ci ildə ən önəmli xəbərlər hansılardır?"
• "İdman kateqoriyasında neçə xəbər var?"

Mənə sualınızı verin!""",
    "en": """Hello! I'm an AI assistant for Azerbaijani news.

What I can do:
• Search and analyze news
• Provide information about events, people, organizations
• Present statistics by year, month, category
• Select important news

Example questions:
• "What happened in Baku today?"
• "Latest news about Ilham Aliyev"
• "What are the most important news in 2025?"
• "How many news items in sports category?"

Ask me your question!""",
    "ru": """Привет! Я AI-помощник по новостям Азербайджана.

Что я могу:
• Искать и анализировать новости
• Предоставлять информацию о событиях, людях, организациях
• Показывать статистику по годам, месяцам, категориям
• Выбирать важные новости

Примеры вопросов:
• "Что произошло сегодня в Баку?"
• "Последние новости об Ильхаме Алиеве"
• "Какие самые важные новости в 2025 году?"
• "Сколько новостей в категории спорт?"

Задайте мне свой вопрос!""",
}


ATTACKING_MESSAGES = {
    "az": """Xəbərdarlıq

Sorğunuzda qeyri-adi və ya potensial təhlükəli məzmun aşkar edildi.

Təhlükəsizlik Qaydaları:
• Sistem yalnız xəbər axtarışı və təhlili üçündür
• Prompt injection və ya manipulyasiya cəhdləri qəbul edilmir
• Həssas məlumatlar əlçatan deyil
• Bütün şübhəli fəaliyyətlər qeydə alınır

Nə edə bilərsiniz:
• Xəbərlərlə bağlı suallar verin
• Hadisələr, şəxslər haqqında məlumat alın
• Statistik təhlillər tələb edin

Zəhmət olmasa, düzgün suallar verin. Təşəkkürlər!""",
    "en": """Warning

Unusual or potentially dangerous content has been detected in your query.

Security Rules:
• The system is for news search and analysis only
• Prompt injection or manipulation attempts are not accepted
• Sensitive information is not accessible
• All suspicious activities are logged

What you can do:
• Ask questions about news
• Get information about events and people
• Request statistical analyses

Please ask appropriate questions. Thank you!""",
    "ru": """Предупреждение

В вашем запросе обнаружен необычный или потенциально опасный контент.

Правила безопасности:
• Система предназначена только для поиска и анализа новостей
• Попытки prompt injection или манипуляции не принимаются
• Конфиденциальная информация недоступна
• Все подозрительные действия регистрируются

Что вы можете делать:
• Задавать вопросы о новостях
• Получать информацию о событиях и людях
• Запрашивать статистические анализы

Пожалуйста, задавайте корректные вопросы. Спасибо!""",
}


PREDICTION_MESSAGES = {
    "az": """Proqnozlaşdırma Haqqında

Hal-hazırda sistem gələcək proqnozlarını dəstəkləmir.
Ancaq siz keçmiş məlumatlar əsasında trend təhlili üçün aşağıdakı sualları verə bilərsiniz:

• "2024-2025-ci illərdə hansı mövzular daha çox müzakirə olundu?"
• "Azərbaycanda ən çox təkrarlanan xəbər kateqoriyaları hansılardır?"
• "Son 6 ayda hansı mövzular populyarlıq qazandı?"

Bu cür suallar üçün "statistics" növünü istifadə edin.""",
    "en": """About Predictions

The system currently does not support future predictions.
However, you can ask trend analysis questions based on historical data:

• "What topics were discussed most in 2024-2025?"
• "What are the most frequently repeated news categories in Azerbaijan?"
• "What topics gained popularity in the last 6 months?"

Use "statistics" type queries for such questions.""",
    "ru": """О Прогнозах

Система в настоящее время не поддерживает прогнозы будущего.
Однако вы можете задать вопросы анализа трендов на основе исторических данных:

• "Какие темы обсуждались чаще всего в 2024-2025 годах?"
• "Какие категории новостей чаще всего повторяются в Азербайджане?"
• "Какие темы стали популярны за последние 6 месяцев?"

Используйте запросы типа "statistics" для таких вопросов.""",
}


NO_RESULTS_MESSAGES = {
    "az": """Sorğunuz üzrə məlumat tapılmadı.

Tövsiyələr:
• Başqa sözlərlə ifadə edin
• Daha ümumi terminlər istifadə edin
• Tarix aralığını dəyişin

Yardım üçün "kömək" yazın.""",
    "en": """No information found for your query.

Suggestions:
• Rephrase in different words
• Use more general terms
• Change the date range

Type "help" for assistance.""",
    "ru": """Информация по вашему запросу не найдена.

Рекомендации:
• Перефразируйте другими словами
• Используйте более общие термины
• Измените диапазон дат

Напишите "помощь" для справки.""",
}
