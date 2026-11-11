# Повторна перевірка BUG-001, BUG-003, BUG-004 (друга) і деталей прайсу v3

| | |
| --- | --- |
| Дата | 2026-11-10, ~14:27–14:50 UTC |
| Стенд | es.seller1.vus.us |
| Збірка | `feat-seur-delivery--d-20261110.3-seller1 77cec0ce` |
| Покупець | тестовий 1075831 (`TEST_BUYER_ES`, cookie `showTestUsers`) |
| Продавець | тестовий 1082119 (`TEST_SELLER_SEUR`), окремий контекст `seller-es` |
| Деталь | T01 BOSCH 0986452024 |

## Підсумок

| Баг | Перевірки | Результат |
| --- | --- | --- |
| Блокер «Seur не рахує» (`…20261110.2`) | — | **Знято.** `seur-delivery-cost` T01: «28001» → 4.76, тип 26; «08001» → 4.76, тип 26 |
| BUG-004 (картка товару) | 9 | **Виправлено.** `product-card/delivery-cost?…&deliveryType=26` → `cost` 4.76; картка «SAA» — «Entrega 4,76 EUR» |
| BUG-001 (збережена адреса Seur) | 65 | **Виправлено.** Нова адреса типу 26 зі замовлення (2043617, «Calle Seur QA 20», «28001») підставилась при повторному оформленні, є в «Direcciones guardadas», `Price` 4.76, тип 26 |
| BUG-003 (ТТН) | 71, 69, 81, 89 | **Виправлено.** Нове замовлення Seur 10787679 → «CONFIRMAR» 204 → «PEDIDO ENTREGADO» 204 → «Departed», ТТН `REC000000733782`, етикетка SEUR PDF |

## Деталі прайсу v3 на стенді

Усі шість карток мають пропозицію «Vendedor: SAA» з описом «… (prueba SEUR, T2x)», «Entrega a partir de: Pasado mañana, Madrid»; ціна з IVA = ціна прайсу × 1,21:

| Деталь | Картка | Ціна на картці |
| --- | --- | --- |
| T22 REMSA 001440 | `/repuesto-001440-REMSA-250/` | 30,25 EUR |
| T23 MEYLE 1007500002 | `/repuesto-1007500002-MEYLE-581/` | 42,35 EUR |
| T24 BOSCH 0121715014 | `/repuesto-0121715014-BOSCH-91/` | 217,8 EUR |
| T25 MAHLE 0039280 | `/repuesto-0039280-MAHLE-66/` | 114,95 EUR |
| T26 FEBI 32485 | `/repuesto-32485-FEBI-905/` | 169,4 EUR |
| T27 TRW JTR3558 | `/repuesto-JTR3558-TRW-56/` | 36,3 EUR |

## BUG-004 — подробиці

- Картка пропозиції «SAA» (`VER MÁS`, `#/products/0986452024;96;0000;445949`), покупець, «Entrega a partir de: Pasado mañana, Madrid»: блок «Entrega» — **«4,76 EUR»**.
- Запит сторінки: `GET /api/v1/product-card/delivery-cost?descriptor=0986452024;96;0000;445949&price=9.9&deliveryType=26` → 200 `{"assessedCost":9.9,"cost":4.76,…}`. Для порівняння `deliveryType=25` → `cost` 6.1.
- На картці ціна доставки **без IVA** (4,76), в оформленні «Envío» — з IVA (5,76EUR); ціна товару на картці — з IVA («IVA incluido»). Так само картка показувала й Genei (6,10 = `cost`). Очікування рядка № 9 — «4,76 € без IVA» → Pass; чи має картка показувати доставку з IVA — питання QA.
- Гостя не перевірено.
- Скриншот — `bug004-card.png`.

## BUG-001 — подробиці

- Автопідстановка на оформленні 1082119: «28004», «Calle Ruiz de Alarcón, 26» → `seur-delivery-cost` 4.76, тип 26; «Envío» «5,76EUR». Скриншот — `bug001-checkout-auto.png`.
- `GET /api/v1/addresses` (оформлення 1082119): 292 адреси, 24 з типом 26.
- «Direcciones guardadas» → «Portugal, 1000-001, Lisboa, …» → `seur-delivery-cost?countryIso=PT&postalCode=1000-001` → 4.76, «LISBOA», тип 26; «Envío» «5,76EUR». Скриншот — `bug001-saved-pt-type26.png`.
- **Повний сценарій бага:** замовлення 10787679 на нову адресу «Calle Seur QA 20», «28001» (`POST /api/v1/addresses` → Id 2043617, `DeliveryType` 26 «Seur») → знову T01 у кошик → оформлення 1082119: підставилось «28001», «MADRID», «Calle Seur QA 20»; у «Direcciones guardadas» — першою «España, 28001, MADRID, Calle Seur QA 20»; `Price` 4.76, тип 26. Скриншот — `bug001-recheckout.png`.
- «Perfiles de contacto» → «Direcciones» не перевірено.

## BUG-003 — повний флоу

| Крок | Результат |
| --- | --- |
| Оформлення T01, «28001», «Calle Seur QA 20» | `seur-delivery-cost` 4.76, тип 26; «Envío» «5,76EUR»; «A pagar» «18,23EUR» = (11,98 + 5,76) × 1,0275 |
| «Pagar con tarjeta» | `POST /api/v1/orders` → **10787679**, «WaitingPayment»; `POST …/payments/stripe` → Stripe Checkout (`cs_test_…`, «Тестовая среда»): 18,23 € = 17,74 € + «Servicios de marketplace» 0,49 € |
| Оплата 4000 0072 4000 0007, 09/30, 111 | без 3-D Secure; повернення на `/orders/10787679/?status=holded…`; замовлення «WaitingSellerComfirmation», `IsPrepaymentPaid` true, `PaymentSystem` stripe, `DeliveryPrice` 5.76, `DeliveryIVA` 1.00, `BuyerDeliveryProfile.DeliveryType` «Seur» |
| Продавець «CONFIRMAR» | `PUT /api/v1/orders/10787679/confirmation` → 204, «WaitingDeparture» |
| Продавець «PEDIDO ENTREGADO» (14:44:00 UTC) | `PUT /api/v1/orders/10787679/departure-confirmation` → **204**; статус **«Departed»** (14:43:56Z) |
| ТТН | `TrackingInfo`: `DeliveryType` «Seur», `TrackingNumber` **REC000000733782**, `DeliveryName` «SEUR», `DeliveryCost` 5.76, `TrackingUrl` `https://www.seur.com/miseur/mis-envios/detalle?tracking=REC000000733782` |
| Дії продавця в «Departed» | «FINALIZAR EL PEDIDO», «DESCARGAR ETIQUETA»; дій скасування немає (№ 89) |
| «DESCARGAR ETIQUETA» | `GET /api/v1/orders/10787679/download-shipment-document` → 200 `application/pdf`, 39 318 байт, `Label-10787679.pdf`: етикетка SEUR «S-24/ESTD», `REC000000733782`, «de MADRID a MADRID», отримувач «ES BUYER, CALLE SEUR QA 20, 28001 MADRID», «Ref.Exp: AVTO-10787679», «Bultos: 1/1», «Peso: 0.492» (= вага T01 у базі) |
| Покупець, сторінка замовлення | посилання «Seguimiento del envío» → трекінг SEUR `REC000000733782` |

Скриншоти: `stripe-filled.png`, `after-payment.png`, `bug003-seller-departed.png`, `bug003-buyer-departed.png`; етикетка — `label-10787679.pdf`.

## Зауваження (потребують рішення QA)

1. **Індекс відправника на етикетці.** «REMITE: … AVDE CONCHA ESPINA, 28036 / **28001** MADRID - ES»: в адресі магазину продавця індекс 28036, а в рядку міста — 28001 (індекс отримувача). Можливо, для відправника береться індекс покупця або індекс за замовчуванням [ПРИПУЩЕННЯ]. Впливає на забір посилки кур'єром SEUR. **QA (2026-11-10):** на етикетці «звідки — куди» (28036 — магазин, 28001 — отримувач), не дефект; контроль — етикетка замовлення на «08001» (№ 119).
2. **`LabelExists` = false** у `GET /api/v1/orders/10787679` після створення ТТН, хоча «DESCARGAR ETIQUETA» віддає PDF. На UI не впливає.
3. **Картка товару — доставка без IVA** (див. BUG-004).

## Для QA в логах

- `Seur:CreateShipment` / `CollectionCreated` для 10787679 (14:43:56–14:44:00 UTC).
- `Seur:GetDeliveryPrice` для `itemsId` 29174388 («28001», 4.76).

## Стан після перевірки

- Замовлення 10787679 — «Departed» (Seur), Профіт не перевірявся — залишено для прогону руху грошей (№ 150).
- У кошику покупця — T01 (`itemsId` 29174524).
