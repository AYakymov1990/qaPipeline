# Прогін API-рядків: 127593 · 2026-11-06

| | |
| --- | --- |
| Стенд | es.seller1.vus.us (avtopro.es), збірка `feat-seur-delivery--d-20261106.3-seller1 a14808f7` |
| Що | 9 рядків чек-листа з «Виконання: API»: 4, 5, 7, 8, 41, 70, 80, 83, 84 — запити агента зі сторінки стенду під тестовими акаунтами (Playwright MCP); `/api/v1/seur/*` не викликались |
| Ролі | гість (контекст `guest-api`), покупець `TEST_BUYER_ES` 1075831 (`buyer-api`), продавець Seur `TEST_SELLER_SEUR` 1082119 (`seller-api`), продавець Genei `TEST_SELLER_GENEI` 1049862 (`genei-api`) — роль перевірено за «ID: …» у шапці / `GET /api/v1/addresses` 403 |
| Дані | кошик гостя: T01 (позиція 29143789, 1082119), Febi 2569 (29143790, 1049862); замовлення Seur 10774398, 10774403 («WaitingDeparture», без ТТН) |
| Запустив | QA (a.yakimov) — Claude Code + Playwright MCP |

**Підсумок:** Pass — 4 (№ 4, 5, 8, 84); Fail — 2, обидва потребують рішення QA (№ 7 — Q-017, № 41 — індекс 99999); Blocked — 3 (№ 70, 83 — немає замовлення Seur з ТТН через BUG-003; № 80 — перевірено лише «Ожидает отправки»).

## По перевірках чек-листа

| CHK | Результат | Факт |
| --- | --- | --- |
| CHK-004 | PASS | Гість, `seur-delivery-cost?sellerId=1049862&countryIso=ES&postalCode=28001&itemsId=29143790` → 200 `{"Price":5.91,"CityName":"Madrid","DeliveryTypeId":25}`; `genei-delivery-cost` з тими самими параметрами → 200 `Price` 5.91 — ціна Genei, тип 25. Подію `NoDeliveryOffered` у лозі агент не бачить |
| CHK-005 | PASS | Покупець 1075831, кошик лише Febi 2569 (1049862), оформлення `/cart/checkout/1049862/`, «28001», нова вулиця. Агент підмінив у запиті `DeliveryTypeId` 25 → 26: `POST /api/v1/addresses` → 200, адресу 2040784 збережено з типом **26**; `POST /api/v1/orders` (`UserAddressId` 2040784) → **500** без тіла; переходу на Stripe немає, позиція лишилась у кошику — замовлення не створено. На сторінці повідомлення про помилку немає. Кошик очищено |
| CHK-007 | FAIL (потребує рішення QA) | Гість: `itemsId=1` → 200 `{"Price":0,"CityName":null,"DeliveryTypeId":26}`; `itemsId=29143790` (позиція іншого продавця) → те саме. Очікувано 400 (як Genei); фактично — як у ⚠ Код. Рішення — за Q-017 |
| CHK-008 | PASS | Гість, кошик 1082119 з T01: без `postalCode` → 400 «The postalCode field is required.»; `countryIso=XX` → 400 `{"reason":"PriceUnavailable"}`; 500 немає. Текст у кошику для 400 `PriceUnavailable` — «La entrega en la ciudad indicada no está disponible. …» (бачено в прогоні 2026-11-05-1942, CHK-042) |
| CHK-041 | FAIL (потребує рішення QA) | Гість, `postalCode=99999&itemsId=29143789` → 200 `{"Price":4.76,"CityName":"NOW VALENCIA","DeliveryTypeId":26}`: довідник SEUR знаходить «місто» для неіснуючого індексу, Seur рахує як Largo (4,76 € — для T01 як 28001), передачі на Genei немає. Для порівняння `genei-delivery-cost` з 99999 → 400 `PriceUnavailable`. **В інтерфейсі не відтворюється** (перевірено 2026-11-06, гість): на оформленні 1082119 «Codigo postal» «99999» → запиту `seur-delivery-cost` немає (лише `GET /api/v1/addresses` 403), «Ciudad» порожнє, ціни доставки немає — до релізу 129469 оформлення не викликає розрахунок для неіснуючого індексу. «NOW VALENCIA» і 4,76 € — лише при прямому запиті до API. Рішення QA: чи прийнятна ціна Seur для неіснуючого індексу після релізу 129469, коли оформлення почне викликати розрахунок |
| CHK-070 | BLOCKED | Замовлення Seur з ТТН немає (BUG-003). Покупець на своєму 10774398 без ТТН: `download-shipment-document` → 400 «The shipment tracking number was not found». Також відкрите Q-018 |
| CHK-080 | BLOCKED | «Ожидает отправки» (10774403, продавець 1082119): дій у кабінеті — «PERSONALICE», «PEDIDO ENTREGADO», «CANCELAR PEDIDO», «ENVIAR» (коментар), «AÑADIR AVTOPRO» — введення ТТН немає ✓; `PATCH /api/v1/orders/10774403/tracking-info` (`TrackingNumber` «QA26TEST000001») → 400 «TrackingNumber does not belong to buyer», ТТН не збережено, статус «WaitingDeparture» ✓. Статус «Отправлен» — замовлень немає (BUG-003). Відхилення дає перевірка належності номера в SEUR (`SeurTrackingNumberHandler`), а не заборона ручного введення: справжній номер SEUR цього покупця, можливо, буде прийнято [ПРИПУЩЕННЯ] |
| CHK-083 | BLOCKED | Замовлення Seur з ТТН немає (BUG-003); іншого тестового покупця немає в `.env`. Продавець Genei 1049862 на чужому 10774398 без ТТН: `download-shipment-document` → 400, `label-exists` → 404 — без ТТН перевірку доступу від «немає ТТН» не відрізнити |
| CHK-084 | PASS | `GET /api/v1/genei/shipments/10774398/label-exists`: покупець 1075831 → 403; продавець 1082119 (без ТТН) → 404 |

## Помічено поза рядками

- CHK-005: `POST /api/v1/addresses` приймає тип 26 на оформленні продавця Genei — у покупця 1075831 зʼявилась адреса 2040784 «Calle QA Tipo 26 5» типу 26. Помилка оформлення — 500 без тексту, покупець на сторінці нічого не бачить.
- Під час підміни змінився і `POST /api/v1/analytics/push` (у тілі теж був `deliveryTypeId=25`) — на результат не впливає.

## Докази

- `CHK-005-genei-type26-500.png` — оформлення 1049862 після 500, без повідомлення.
- `CHK-041-ui-99999.png` — оформлення з «99999»: «Ciudad» порожнє, ціни немає.
- `CHK-080-seller-10774403.png` — замовлення 10774403 у продавця: кнопки дій, поля ТТН немає.
