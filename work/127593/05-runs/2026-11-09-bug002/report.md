# Повторна перевірка BUG-002 (Palma, доплата +3 €)

| | |
| --- | --- |
| Дата | 2026-11-09 |
| Стенд | es.seller1.vus.us |
| Збірка | `feat-seur-delivery--d-20261109.7-seller1 09764829` (після правок розробника; стенд перезапущено QA) |
| Користувач | тестовий покупець 1075831 (у вкладці вже був вхід; баг відтворювався і під гостем, і під покупцем) |
| Кошик | продавець 1082119 («SAA»), T01 BOSCH 0986452024, 1 шт. (`itemsId` 29158951); cookie `showTestUsers` |
| Перевірка | CHK-021 (TC-004) |
| Результат | **PASS — баг виправлено** |

## API: `GET /api/v1/cart/seur-delivery-cost` (усі 200, `DeliveryTypeId` 26)

| Індекс | `CityName` | `Price` | До виправлення (BUG-002) |
| --- | --- | --- | --- |
| 07001…07005, 07007, 07012, 07014 | PALMA DE MALLORCA | 7.94 | 7.94 — без змін |
| 07006 | PALMA DE MALLORCA | 7.94 | ES PORTITXOL, 10.94 |
| 07008 | PALMA DE MALLORCA | 7.94 | EL RAFAL, 10.94 |
| 07009 | PALMA DE MALLORCA | 7.94 | POL SON FUSTER, 10.94 |
| 07010 | PALMA DE MALLORCA | 7.94 | ESTABLIMENTS, 10.94 |
| 07011 | PALMA DE MALLORCA | 7.94 | POL DE CAN VALERO, 10.94 |
| 07013 | PALMA DE MALLORCA | 7.94 | LOS ALMENDROS, 10.94 |
| 07015 | PALMA DE MALLORCA | 7.94 | LA BONANOVA, 10.94 |
| 07120, 07121, 07600 | PALMA DE MALLORCA | 7.94 | 7.94 — без змін |
| 07198 | PALMA DE MALLORCA | 7.94 | S'HOSTALOT, 10.94 |
| 07199 | PALMA DE MALLORCA | 7.94 | SON GUAL, 10.94 |
| 07610 | PALMA DE MALLORCA | 7.94 | CA'N PASTILLA, 10.94 |

## Регрес (контрольні індекси)

| Індекс | `CityName` | `Price` | Очікувано | Збіг |
| --- | --- | --- | --- | --- |
| 07500 | MANACOR | 10.94 | 10.94 (+3 € Mallorca поза Palma, CHK-022) | так |
| 07800 | SANTA EULARIA DES RIU | 19.04 | 19.04 (реекспедиція, CHK-023) | так, назва як у прогоні 2026-11-05 |
| 07860 | LA SAVINA/FORMENTERA | 19.04 | 19.04 | так |
| 07701 | MAHON | 19.04 | 19.04 | так |
| 28001 | MADRID | 4.76 | 4.76 (CHK-010) | так |

## UI

«Codigo postal» «07010» → «Ciudad» «PALMA DE MALLORCA», «Envío» «9,61EUR» (7,94 × 1,21). Скриншот — `07010-palma.png`.

Замовлення не створювались.
