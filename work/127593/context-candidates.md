# Кандидати в контекст: 127593

> Непідтверджені. Записуються в `qa-context/` тільки після відповіді QA («так», «так 1, 3», «ні»).

Записано 2026-11-04 («да сохрани контекст»): пункти 1–10 — glossary (Seur, тип 25 / 26, паливна надбавка, зони Medio / Largo, Fuera de Norma), domain/delivery.md (BR-127593-01…03, рядок Seur у «Служби за площадками»), test-data (1082119 із Seur, деталі T01…T14, поштові індекси для Seur), `.env.example` (`TEST_SELLER_SEUR_*`, `TEST_BPANEL_QA_*`), PROJECT.md § 6 (рядок Seur).

Записано 2026-11-04 («сохрани контекст»): пункти 11–26 — domain/delivery.md (BR-127593-03 оновлено, BR-DLV-01, ендпоінти кошика й етикетки, мапінг статусів), domain/order.md (переходи, скасування), domain/payment.md (продовжений холд, вирахування доставки), PROJECT.md § 11 (Seur `POST /shipments`), glossary.md (терміни й назви в UI), sources.md (зони CodeWiki), howto/order-dates.md.


Записано 2026-11-04 («да сохрани контекст»): пункти 27–31 — domain/payment.md (без готівки на es, IVA), domain/delivery.md (BR-127593-04, іконка етикетки), PROJECT.md § 10 (автотести Genei).

Записано 2026-11-05 («да сохрани контекст»): пункт 32 — domain/delivery.md (поля відповіді `seur-delivery-cost`, що видно тільки в лозі).

Записано 2026-11-05 (QA описав рецепти): пункти 33, 34 — `howto/unpaid-order.md`, `howto/saved-address-genei.md` + рядки в `howto/README.md`.

Записано 2026-11-05 («добавь контекст»): пункти 35–46 — test-data.md (cookie, seller3 через VPN, 1082119 «Vendedor: SAA» / «Seur Test», 1049862, 1075831, індекси 99999 і 9000-001), domain/delivery.md (автопідстановка адрес, 10 € при недоступному Genei, Мадейра й Азори, де рахується доставка), domain/payment.md («Envío», «A pagar»), glossary.md (назви es / pt, повний `DeliveryNotAvailableText`, примітки «до релізу 129469»).

Записано 2026-11-05 («да сохраняем контекст»): пункти 47–51 і дані QA — test-data.md (`TEST_BUYER_ES` «test1», кошик спільний з автотестами й дозволено очищати; 1049862 «truepaymentvz» / Febi 2569; Рекалві «RECAMBIOS AUTO» / Miraglio 301006C, склад Vigo), glossary.md (кабінет продавця, статуси, «Entrega a partir de:», pt), domain/payment.md (IVA pt 23 %), howto/agent-login.md + README.

Записано 2026-11-06 («да запиши контекст»): пункти 52–66 — test-data.md (вага з бази, T15…T21, seller1 і збірки, «Hoy / Mañana, Vigo»), glossary.md (дії продавця й покупця на es, «ENVIAR» виправлено, «Portugal (islas)», країни pt), domain/delivery.md (вага з бази, `suspicious`), domain/order.md (дії продавця es, неоплачене), domain/payment.md (66 — дубль, оновлено «перевірено»), sources.md (паливна надбавка SEUR), howto/agent-login.md (Stripe, роль після перезапуску), howto/unpaid-order.md (перевірено, відомі проблеми), новий howto/part-dimensions.md + README.

Записано 2026-11-06 («да запиши контекст»): пункти 67–68 — domain/delivery.md (автопідстановка 25 / 26 для Рекалві й продавців Seur — конфлікт вирішено, було / стало в рядку; гість без збережених адрес), domain/order.md (без оплати немає «CONFIRMAR»).

<!-- оброблено -->
## 2026-11-06 — після рішень QA по прогону (оброблено)

67. [domain/delivery.md] **Конфлікт.** Було: «підставляється адреса, тип якої збігається з типом доставки продавця (Genei — 25, Seur / Рекалві — 26) … Адреса типу 25 підставляється й у Рекалві». Стало: «До продавця Рекалві (а після релізу 127593 — до продавців із Seur) можуть підставлятися збережені адреси і типу 25, і типу 26 — так працює на проді» [зі слів QA, 2026-11-06].
68. [domain/order.md] До пункту про неоплачене замовлення: «поки покупець не оплатив, кнопки підтвердження («CONFIRMAR») у продавця немає — очікувана поведінка» [зі слів QA, 2026-11-06]; гість на оформленні es: збережених адрес немає, після повернення з кошика форма не зберігає індекс — очікувано [зі слів QA, 2026-11-06] → `domain/delivery.md`.

## 2026-11-06 — прогін API-рядків

69. [test-data.md] Індекс «99999» не підходить як «неіснуючий» для Seur на es: довідник SEUR повертає «NOW VALENCIA», Seur рахує ціну (T01 — 4,76 €, тип 26); Genei для 99999 → 400 `PriceUnavailable` (seller1, 2026-11-06) [задача 127593].
70. [domain/delivery.md] Ручне введення ТТН для типу 26 (`PATCH /api/v1/orders/{id}/tracking-info`) перевіряє належність номера в SEUR: вигаданий номер → 400 «TrackingNumber does not belong to buyer»; у кабінеті продавця поля введення ТТН для Seur немає (seller1, 2026-11-06) [задача 127593].

Записано 2026-11-08 (QA: «логіку руху грошей … пометь в контексте», діє для ES, PT): пункти 71–76 з відповідями на Q-030…Q-034 — новий `howto/payment-status.md` + рядок у `howto/README.md`, domain/payment.md (статуси Профіту, таблиці «Статус оплати ↔ статус замовлення» і «Повернення» з позначкою ES / PT), domain/order.md (коди статусів), glossary.md («Finanzas» → «Historial de operaciones», «Cuenta», «SE HA GENERADO EL PEDIDO», Профіт). Пункт 77 — чекає відповіді.

## 2026-11-08 — рух грошей і день релізу (дані QA)

71. [howto/payment-status.md, новий] Як перевірити стан грошей замовлення: `https://prft.avto.pro/s/CheckPaymentStatus?orderid=<номер>` (нова вкладка) → блок «СТАТУС ВНУТРИ СИСТЕМЫ ПРОФИТ»: «Статус», «Мерчант», «Касса» («Тестовое окружение» — тестовий контур). Надпис «Оплачен» у картці замовлення списання не підтверджує [зі слів QA, 2026-11-08] + рядок у `howto/README.md`.
72. [domain/payment.md] Статуси Профіту: `holded` — заморожування, `success` — успішне підтвердження холда, `succeeded` — успішний платіж, `reversed` — повернення [wiki, зі слів QA, 2026-11-08].
73. [domain/payment.md, таблиця «Статус оплати ↔ статус замовлення»] ES / PT: після «CONFIRMAR» кошти утримуються, на балансі продавця «Cuenta» їх немає; звичайний продавець — списання на ТТН / «PREPARADO»; дроп — на «SE HA GENERADO EL PEDIDO» [зі слів QA, 2026-11-08].
74. [domain/payment.md, таблиця «Повернення»] Поки кошти утримуються, ручне скасування звільняє холд (спершу повідомлення про скасування, потім — про звільнення коштів); після списання автоповернення немає — текст зі зверненням у підтримку; автоскасування після «CONFIRMAR» — автоповернення вимкнене, випадки враховує аналітика [зі слів QA, 2026-11-08].
75. [domain/order.md] Числові коди статусів замовлення: 0 WaitingSellerComfirmation, 1 WaitingBuyerConfirmation, 10 BeingEdited, 2 WaitingPayment, 3 Paid («замовлення формується» для самовивозу і свого способу), 7 WaitingDeparture, 8 Departed, 4 Delivered, 5 Completed, 11 RejectedRequest (скасування не завершене), 6 Rejected, 14 PrepaymentRefundToBuyer [зі слів QA, 2026-11-08].
76. [glossary.md] «Cuenta» — баланс продавця в кабінеті (es); «SE HA GENERADO EL PEDIDO» — кнопка дропа «замовлення сформовано», на ній списується холд; «Касса: Тестовое окружение» у Профіті — тестовий контур оплати [зі слів QA, 2026-11-08].
77. [domain/delivery.md] Seur, ітерація 1: тарифи й паливну надбавку розробник завантажує вручну; завантаження через API — ітерація 2 [зі слів QA, 2026-11-08, задача 127593]. **Записано 2026-11-09** (QA: «да запиши») — у BR-127593-02.
78. [domain/recalvi.md] У продавця Рекалві є кнопка «CANCELAR PEDIDO»; на проді коректно скасовує замовлення, відображення — не дефект [зі слів QA, 2026-11-09]. **Записано 2026-11-09** (QA: «для контекста»).

## 2026-11-10 — повний прогін (чекає відповіді QA)

79. [howto/order-dates.md] «Перевірено: так (2026-11-10, es.seller1)»: під `TEST_BUYER_ES` (роль TestUsers) `PATCH /api/v1/qa/orders/shift-date?orderId=&shiftDay=-5` → 200; `GET /api/v1/qa/orders/emulate-auto-reject-order?orderId=` → 200 «Успех! Предоплата: Refunded» для «WaitingDeparture» і для «WaitingSellerComfirmation» з минулим дедлайном [прогін 127593].
80. [howto/payment-status.md] «Касса» для тестового контуру показує «STRIPE TEST ABPWORLD» (не «Тестовое окружение»), «Мерчант: наш»; сторінка Профіту відповідає ~30 с [прогін 127593, 2026-11-10].
81. [howto/agent-login.md або test-data.md] Stripe Checkout для тестового email покупця пропонує вхід у Stripe Link («Подтвердите, что это вы», телефон) — закривати «Назад»; email після цього очищується, ввести знову [прогін 127593, 2026-11-10].
82. [domain/payment.md] Зарахування продавцю на «PEDIDO ENTREGADO» / «PREPARADO»: Seur — сума замовлення з доставкою (`SumPrice`), Genei — лише товари; після скасування покупцем відправленого замовлення зарахування лишається («Para solicitar el reembolso, contacte con el servicio «Solicitar soporte técnico».») [прогін 127593, 2026-11-10; Q-031 — уточнити].
83. [glossary.md] es, дії / тексти: «FINALIZAR EL PEDIDO» (продавець, «Departed»), «Cancelación del pedido», «Indique el motivo de la cancelación.», «Hemos liberado el importe retenido en tu tarjeta. Tu banco puede tardar unos días en reflejarlo.», «Cancelado automáticamente. Sin respuesta al pedido.»; pt — «ADICIONAR», «PAGUE COM CARTÃO», «Entrega ao domicílio» [прогін 127593, 2026-11-10].
84. [test-data.md] Рекалві: будь-яка пропозиція «RECAMBIOS AUTO» (1369756), склад не важливий; Miraglio 301006C — склади Sevilla, Madrid, Oviedo, Zaragoza, Vigo зараз немає [зі слів QA, 2026-11-10].
85. [domain/delivery.md] Збережені адреси фільтруються за службою продавця: в оформленні Genei — лише тип 25, у Seur 1082119 — тип 26 і 25, у Рекалві — обидва типи [прогін 127593, 2026-11-10, після виправлення BUG-001].
