# Звіт прогону: 127593 · 2026-11-10 16:20

| | |
| --- | --- |
| Стенд | es.seller1.vus.us, pt.seller1.vus.us (VPN) |
| Збірка | `feat-seur-delivery--d-20261110.3-seller1 77cec0ce` (BUG-001, 003, 004 виправлено; BUG-002 — 2026-11-09) |
| Браузер | Chromium (Playwright MCP), десктоп / 390×844 |
| Кейси | TC-001 … TC-027 (статус «чернетка», прогін дозволив QA; повний прогін — запит QA 2026-11-10) |
| Запустив | QA (a.yakimov) — `/qa-agent-run`, Claude Code + Playwright MCP, локальний компʼютер |
| Попередні прогони | `2026-11-05-1942` (збірки .5 / 20261106.3) — завершено; `2026-11-05-1327`, `-1512` — старі збірки, не продовжуються. Прайс `Seur_test_pricelist_v3.xlsx` (T01…T27) |

**Підсумок:** прогін **завершено** 2026-11-10 17:37 (1 год 17 хв). 27 з 27 кейсів: PASS — 21 (з них TC-007, TC-013 — за рішенням QA 2026-11-06, та сама поведінка); PASS з частковим BLOCKED — 4 (TC-002, TC-004, TC-005 — немає T21 у продавця; TC-018 — CHK-067); PASS з FAIL «потребує рішення QA» — 1 (TC-027 / CHK-155); BLOCKED — 1 (TC-026 / CHK-120). CHK (70 агентних у прогоні): **64 Pass, 5 Blocked, 1 Fail (рішення QA)**; після відповідей QA — **66 Pass, 4 Blocked** (CHK-067, CHK-155 → Pass; лишаються CHK-024, 028, 035 — T21, CHK-120 — QA вручну). Нових дефектів без рішення QA немає — чернеток багів не створено. BUG-001…004 виправлено й підтверджено повторно в повному прогоні. Головне: рух грошей Seur відповідає Genei (`holded` → `succeeded` на «PEDIDO ENTREGADO»; скасування / відхилення / автоскасування до відправлення → `reversed`); межі тарифу T22…T27 збіглися до 0,01 €; ТТН, етикетка й трекінг Seur працюють. Створено 14 тестових замовлень (усі тестова картка Stripe).

## Потребує рішення QA

| № | Що | Де |
| --- | --- | --- |
| 1 | **CHK-155**: при автоскасуванні до «CONFIRMAR» (емуляція `emulate-auto-reject-order`) повідомлення «Hemos liberado el importe…» двічі, перше — раніше за «Cancelado automáticamente…». Гроші повернуто (`reversed`). Дефект чи особливість емуляції? | TC-027, 10788037 |
| 2 | **CHK-120**: після зсуву дат на −15 днів у покупця відправленого замовлення Seur немає дії відмови. Від якої дати «доба після крайньої дати відправки» і чи є відмова для Seur (Q-025)? | TC-026, 10787679 |
| 3 | **CHK-067**: після виправлення BUG-001 адреси типу 26 в оформленні Genei не показуються (фільтр за службою) — сценарій «адреса типу 26 у Genei» через UI не виникає. Перевірка неактуальна (Pass) чи перевіряти через API? | TC-018 |
| 4 | **CHK-024, 028, 035**: T21 VAG 1H0521101 зник із продажу в 1082119 (немає пропозиції «SAA» після завантаження прайсу v3). Перевірити склад «Seur Test» / прайс | TC-002, 004, 005 |
| 5 | Діалог скасування покупця в «WaitingDeparture»: «Si cancelas el pedido, perderás el prepago…», а фактично холд повернуто (`reversed`) — текст не відповідає поведінці | TC-023, 10788056 |
| 6 | Зарахування продавцю: Seur — сума з доставкою (476.09 = 459.80 + 16.29), Genei — лише товар (30.25, доставка 7.15 не зараховується). Q-031: так задумано для Seur? | TC-022, TC-025 |
| 7 | Картка товару показує доставку без IVA (4,76), оформлення — з IVA (5,76) | повторна перевірка BUG-004 |

### Відповіді QA (2026-11-10)

- п. 2 (CHK-120) — QA перевіряє сам; лишається Blocked.
- п. 3 (CHK-067) — **Pass за рішенням QA**: в оформленні Genei адреси типу 26 не мають підставлятися; тип 26 — лише для продавців із підключеним Seur.
- п. 4 (CHK-024, 028, 035) — T21 треба змінити ціну в прайсі; у прогоні `2026-11-05-1942` ці перевірки пройшли (T21 / 28001 137.47; T21 / Palma 186.45; T21 / Франція → тип 25, 100.24).
- п. 5 — замовлення 10788056 (діалог «perderás el prepago» у «WaitingDeparture»); для порівняння 10788044 («WaitingSellerComfirmation»: «los fondos se devolverán a la tarjeta…»).
- п. 6 — Seur: 10788066 (+476.09), 10787679 (+17.74); Genei: 10788004 (+30.25), 10788100 (Genei через 1082119, +11.98).
- п. 7 — у замовленні доставка має бути з IVA (так і є: `DeliveryPrice` 5.76).
- п. 1 (CHK-155) — **не дефект, Pass за рішенням QA**: подвійне «Hemos liberado el importe…» при автоскасуванні лишаємо як є.
- п. 7 (картка товару) — доставка на картці без IVA (4,76) — **не дефект**, лишаємо як є.

## Для QA в логах

- `Seur:GetDeliveryPrice` — T25 / T27 (`Used` vs `*Mm`), T26 / T27 `Handling` (No Encintable); T06 вага 15.72 vs 15.63 на етикетці.
- `CollectionCreated` 10788066 (~15:55 UTC); `TrackingRefreshed` 10788066 (`StatusId` → 3 до 16:07 UTC).
- `Seur:CancelShipment` — не має бути для 10788044, 10788056, 10788129, 10788176, 10788037 (ТТН не створювались).
- Автоскасування 10788176, 10788037 — емуляція QA API, а не фонова задача (Q-033).


## По кейсах

| TC | Результат | Спроб | Коротко | Докази |
| --- | --- | --- | --- | --- |
| TC-001 | PASS | 1 | гість (контекст `guest-run`) і `TEST_BUYER_ES` (1075831): T01 / «España» «28001» → `seur-delivery-cost?countryIso=ES&postalCode=28001&sellerId=1082119` 200, тип 26, `Price` 4.76, «MADRID»; «Ciudad» заповнено «MADRID»; «Envío» «5,76EUR»; `genei-delivery-cost` не викликався; блок «Entrega» — «Entrega a domicilio», «País», «Codigo postal», «Ciudad», «Dirección», тексту «Seur» немає. Гостю країну за геолокацією підставлено «UA» (запит `countryIso=UA` → 400 `PriceUnavailable`) — до вибору «España» (П-3.1) | `TC-001/v1-guest-28001.png`, `TC-001/v2-buyer-28001.png` |
| TC-002 | PASS, варіант 11 BLOCKED | 1 | гість, один кошик з усіма деталями; кожен варіант — запит `seur-delivery-cost` лише з `itemsId` деталей варіанта (той самий запит, що шле сторінка; перевірено: T01 окремо = 4.76 як в оформленні TC-001). Усі 200, тип 26, «MADRID»: T01 4.76, T03 5.46, T15 6.12, T07 7.46, T17 8.86 (T18 8.86), T06 11.14, T08 13.56, T19 16.1 (T20 16.1), T11 7.46, T16 / FR 75001 16.81 «PARIS», T05 × 2 (кількість через кошик, `PATCH /api/v1/cart/items/{id}` `Count` 2) 8.86, T01 + T06 11.14 (`itemsId` двома параметрами). **T21 VAG 1H0521101 — пропозиції «SAA» на картці немає** (лише «Used World Parts», «DOICHEV AUTO PARTS») → варіант 11 BLOCKED | запити — у звіті; `TC-001/v1-guest-28001.png` (той самий кошик) |
| TC-003 | PASS | 1 | гість, T06 (`itemsId` 29175009): Medio 28001, 33001, 47001, 15001 і 11 індексів варіанта 2 — усі 200, тип 26, 11.14; Largo 08001 «BARCELONA», 41001, 46001, 19001, 26001 — 13.46; PT 1000-001 «LISBOA», 4000-001 «PORTO» (`countryIso=PT`) — 13.46, тип 26 | запити — у звіті |
| TC-004 | PASS, варіант 5 BLOCKED | 1 | гість, T01: 07001 і **07010** — «PALMA DE MALLORCA», 7.94 (BUG-002 виправлено); 07500 «MANACOR» 10.94; 07800 «SANTA EULARIA DES RIU», 07860 «LA SAVINA/FORMENTERA», 07701 «MAHON» — 19.04; усі тип 26. Варіант 5 (T21) — BLOCKED: немає пропозиції «SAA» | запити — у звіті |
| TC-005 | PASS, варіант 8 BLOCKED | 1 | гість: T15 / FR 75001 «PARIS» 14.55 тип 26; T01: DE 10115 11.22, IT 00184 12.37, PL 00-001 12.93, DK 1050 12.93, SE «111 20» 20.93, FI 00100 24.33 — тип 26; GB SW1A 1AA → 18.17 тип 25 «Londres», CH 8001 → 24.62 тип 25 «Zurich». Варіант 8 (T21 до Франції) — BLOCKED: немає пропозиції «SAA» | запити — у звіті |
| TC-006 | PASS | 1 | гість, T01: 35001 13.45 «Las Palmas de Gran Canaria», 38001 13.45 «Santa Cruz de Tenerife», 51001 7.8 «Ceuta», 52001 7.8 «Melilla» — 200, тип 25 (фіксованої 8,2645 немає); PT 9000-001, 9500-001 → 400 `PriceUnavailable`, під полем «La entrega en la ciudad indicada no está disponible. Por favor, revise los datos ingresados o elija otra localidad cercana.», «Envío» без суми | `TC-006/v2-PT-9000-001.png`, `TC-006/v2-PT-9500-001.png` |
| TC-007 | PASS (рішення QA 2026-11-06 для варіанта 4) | 1 | гість (`guest-021`), окремий кошик на варіант. В1 T06: «28001» 11.14 («13,48EUR») → «08001» новий запит 13.46 «BARCELONA» («16,29EUR»). В2 T01: «28001» 4.76 тип 26 → «35001» 13.45 тип 25 → «28001» 4.76 тип 26, по одному запиту. В3 T06: «28001» → «País» «Portugal»: «Codigo postal» і «Ciudad» очищено, «Envío» без суми, нового запиту немає. В4 T05: «28001» 7.46 → кількість 2 у кошику (`PATCH …/cart/items/{id}` `Count` 2) → «Tramitar Pedido»: форма гостя порожня (країна не вибрана), запиту немає; після «España» + «28001» — 8.86, «10,72EUR». Поведінка в4 — як 2026-11-06 (рішення QA: PASS) | `TC-007/v3-country-pt.png`, `TC-007/v4-qty2.png` |
| TC-008 | PASS | 1 | покупець 1075831: T01, «28001», нова адреса «Calle de Prueba 8» → 4.76 тип 26, «Envío» «5,76EUR»; спосіб оплати — лише «PAGAR CON TARJETA» (готівки немає); оплата → `POST /api/v1/addresses` `DeliveryTypeId` 26 → Id 2043671 «Seur»; замовлення **10788044** `DeliveryType` «Seur», `DeliveryPrice` 5.76. Повторне оформлення 1082119: підставилась «Calle de Prueba 8»; «Direcciones guardadas» — першою «España, 28001, MADRID, Calle de Prueba 8»; вибір → 4.76, тип 26 (BUG-001 виправлено). Крок 6 (рішення QA: будь-яка пропозиція Рекалві, склад не важливий): «RECAMBIOS AUTO» (1369756, склад Sevilla) → `/cart/checkout/1369756/` підставилась «Calle de Prueba 8», «28001» (Id 2043671, тип 26), `genei-delivery-cost` 8.68; не оплачувалось, кошик очищено | `TC-008/recheckout-1082119.png`, `TC-008/recalvi-checkout-address.png` |
| TC-009 | PASS | 1 | покупець 1075831; передумова — адреса Genei «28001» «Calle Genei QA 25» (Id 2043665, тип 25) з TC-025. T01 у кошик (кошик покупця був порожній — T01 з повторної перевірки зник, покупцем користуються автотести) → `/cart/checkout/1082119/`: підставилась «Calle Genei QA 25», «28001»; «Direcciones guardadas» — «España, 28001, Madrid, Calle Genei QA 25» (×2), «España, 28001, MADRID, Calle Seur QA 20»; вибір адреси Genei → `seur-delivery-cost` 200, 4.76, тип 26, «Envío» «5,76EUR». Оплата → замовлення **10788037**: `UserAddressId` 2043668 — нова адреса тип «Seur» з тими самими даними; `DeliveryType` «Seur», `DeliveryPrice` 5.76, `DeliveryIVA` 1, оплачено (Stripe `cs_test_`, 18,23 €) | `TC-009/genei-addr-selected.png` |
| TC-010 | PASS | 1 | гість (`guest-010`): T01, «España» «28001» → 4.76, тип 26. Вхід на сторінці оформлення (форма «Cuenta personal» → «ENTRAR») під `TEST_BUYER_ES` → «ID: 1075831», кошик гостя збережено (T01 `itemsId` 29175335), підставилась збережена «Calle de Prueba 8» «28001» → 4.76, «Envío» «5,76EUR»; оплата → замовлення **10788056** «Seur», `DeliveryPrice` 5.76 (= 4.76 × 1,21), без помилок, тексту «SEUR cart quote has expired…» немає | запити — у звіті |
| TC-011 | PASS | 1 | покупець 1075831: T01 + T13 (без ваги) → один запит `seur-delivery-cost?…itemsId=29175352&itemsId=29175351…` 200, тип 26, `Price` 5.46, «Envío» «6,61EUR»; оплата (56,40 € = 54,89 + 1,51) → замовлення **10788061** (`Items` [29175352, 29175351]), `DeliveryType` «Seur», `DeliveryPrice` 6.61, `DeliveryIVA` 1.15 — доставка в замовленні = «Envío» | запити — у звіті |
| TC-012 | PASS | 1 | покупець: T06 / «08001» «Carrer de Prova 12» → `seur-delivery-cost` 200, тип 26, 13.46 «BARCELONA», «Envío» «16,29EUR»; адреса тип 26 (Id 2043676) → замовлення **10788066** «Seur», `DeliveryPrice` 16.29 (`DeliveryIVA` 2.83), оплачено (489,19 €). Продавець 1082119: до відправлення кнопки — «CONFIRMAR» / після нього «PEDIDO ENTREGADO», «CANCELAR PEDIDO», «ENVIAR» (етикетки немає); «PEDIDO ENTREGADO» → «Departed» (15:55 UTC), ТТН **REC000000733788**, «SEUR», `TrackingUrl` seur.com; кнопки — «FINALIZAR EL PEDIDO», «DESCARGAR ETIQUETA», «ENVIAR» (скасування немає); «DESCARGAR ETIQUETA» → `GET …/download-shipment-document` 200 `application/pdf` 39 668 байт, етикетка SEUR «S-24/ESTD», `REC000000733788`, «de MADRID a BARCELONA», отримувач «CARRER DE PROVA 12, 08001 BARCELONA», «Peso: 15.63». Покупець: ТТН і «Seguimiento del envío» (seur.com), `AvailableActions` порожній — дії відмови немає. Трекінг: о 16:07 UTC (+12 хв) `TrackingInfo.StatusId` null → «3»; текст на сторінці не змінився («El pedido está pendiente de entrega o recepción.») | `TC-012/b1-checkout-08001.png`, `TC-012/b3-seller-before-ship.png`, `TC-012/b4-seller-departed.png`, `TC-012/label-10788066.pdf`, `TC-012/b7-buyer-departed.png`, `TC-012/b8-buyer-tracking.png` |
| TC-013 | PASS (рішення QA 2026-11-06 — та сама поведінка) | 1 | передумова за `howto/unpaid-order.md`: покупець, T01 → «Pagar con tarjeta» → Stripe `cs_test_` → не платити → замовлення **10788098** «WaitingPayment», `IsPrepaymentPaid` false, «Seur». Продавець 1082119: «El pedido está pendiente de pago hasta el 11 de noviembre, 19:00»; `AvailableActions` [«Modification»]; кнопки «PEDIDO ENTREGADO» немає — дію виконати неможливо; статус не змінився, ТТН немає | `TC-013/b1-unpaid-seller.png` |
| TC-014 | PASS | 1 | покупець: T01 / «35001» → `seur-delivery-cost` 200, тип 25, 13.45 «Las Palmas de Gran Canaria», «Envío» «16,27EUR»; `POST /api/v1/addresses` `DeliveryTypeId` 25 (Id 2043681) → замовлення **10788100** «Genei», `DeliveryPrice` 16.27. Продавець 1082119: «CONFIRMAR» 204 → дія відправлення для Genei — «PREPARADO» → «Departed», ТТН «PQ6BR10710691110133001H», «Correos», «Servicio de entrega: Correos Paq Estándar»; «DESCARGAR ETIQUETA» → `GET …/download-shipment-document` 200 `application/pdf` 1757 байт. Покупець: «CANCELAR PEDIDO» → діалог «Cancelación del pedido» («Si cancelas el pedido, perderás el prepago…») → «Error de selección» → `PUT …/rejection` 204 → «Rejected», «Pedido 10788100 cancelado por el comprador», «Para solicitar el reembolso, contacte con el servicio «Solicitar soporte técnico».», етап «Cancelado». Запитів до `/seur/` у браузері немає | `TC-014/b3-preparado-view.png`, `TC-014/label-10788100.pdf`, `TC-014/b5-buyer-cancelled.png` |
| TC-015 | PASS | 1 | pt, `TEST_BUYER_ES` (1075831): T06 (`/pecas-415026110-LUK-582/`, «ADICIONAR») → оформлення: підставилась остання адреса «Espanha» 35001 (54.5) → «Portugal» «1000-001» → `seur-delivery-cost?countryIso=PT` 200, тип 26, 13.46, «LISBOA», «Envio» «16,56EUR»; `POST /api/v1/addresses` `DeliveryTypeId` 26, `CountryIso` PT (Id 2043684) → замовлення **10788119** (`CountryISO` PT), Stripe `cs_test_` 497,27 € → «WaitingSellerComfirmation», «Seur», `DeliveryPrice` 16.56 (`DeliveryIVA` 3.10) | `TC-015/pt-lisboa.png` |
| TC-016 | PASS | 1 | es гість (`guest-021`), T01: «28001» 4.76, «Envío» «5,76EUR», «Pagar con tarjeta» активна → «Portugal» «9000-001» → 400 `PriceUnavailable`, під полем «La entrega en la ciudad indicada no está disponible. Por favor, revise los datos ingresados o elija otra localidad cercana.», «Envío» без суми, «Pagar con tarjeta» неактивна; клік (force) — жодного не-GET запиту, URL без змін. pt гість (`guest-pt`, `/pecas-0986452024-BOSCH-66/`, «ADICIONAR»): «Portugal» «9000-001» → 400, «A entrega na cidade indicada não está disponível. Por favor, verifique os dados introduzidos ou selecione outra localidade mais próxima.», «Envio» без суми | `TC-016/v1-es-9000-001.png`, `TC-016/v3-pt-9000-001.png` |
| TC-017 | PASS | 1 | гість (`guest-021`), T06, «España»; CDP `latency` 2000 мс, 50 000 Б/с: «28001» → запит +851 мс; через ~0,9 с «08001» → запит +2205 мс, запит «28001» скасовано +2209 мс (`net::ERR_ABORTED`); відповідь «08001» +4226 мс 200 13.46; «Ciudad» «BARCELONA», «Envío» «16,29EUR»; пізньої відповіді «28001» немає. Мережу відновлено | `TC-017/race-08001.png` |
| TC-018 | PASS (CHK-067 — за рішенням QA 2026-11-10) | 1 | покупець: кошик T01 («SAA», 1082119) + Febi 2569 («truepaymentvz», 1049862). Група 1082119: підставилась остання адреса PT «1000-001» (з TC-015) → обрано «España» і «28001», «Calle de Prueba 8» → `seur-delivery-cost` 200, тип 26, 4.76 → замовлення **10788129** «Seur», 5.76. Група 1049862: «Direcciones guardadas» і `GET /api/v1/addresses` на `/cart/checkout/1049862/` — лише адреси типу 25 («Calle Canarias QA 1», «Calle Genei QA 25», «Calle Ruiz de Alarcón, 26»); адрес типу 26 (зокрема «Calle de Prueba 8», Id 2043671) немає — обрати неможливо. Обрано «España, 28001, Madrid, Calle Genei QA 25» (тип 25) → `genei-delivery-cost` 5.91 → замовлення **10788148** «Genei», 7.15. На Stripe зʼявилось вікно Stripe Link «Подтвердите, что это вы» (телефон) — закрито «Назад», оплачено карткою; браузер Playwright перезапустився під час повернення, обидва замовлення оплачені | `TC-018/genei-checkout.png` |
| TC-019 | PASS | 1 | вікно 390×844, `TEST_BUYER_ES`: T01 → оформлення 1082119: підставилась «28001», «Calle Genei QA 25» → `seur-delivery-cost` 200, тип 26, 4.76 «MADRID», «Envío» «5,76EUR» (як у десктопі); оплата → `POST /api/v1/addresses` `DeliveryTypeId` 26 → Id 2043668 (існуюча адреса Seur) → замовлення **10788176** «Seur», `DeliveryPrice` 5.76 | `TC-019/mobile-28001.png` |
| TC-020 | PASS | 1 | Рекалві: Miraglio 301006C, «RECAMBIOS AUTO» (1369756, склад Sevilla — рішення QA: склад не важливий) → `/cart/checkout/1369756/`: у «Direcciones guardadas» є адреси обох типів; обрано «España, 28001, MADRID, Calle de Prueba 8» (Id 2043671, тип 26) → `genei-delivery-cost` 200, 8.68 «Madrid», «Envío» «10,50EUR»; оплата (109,76 €) → замовлення **10788182** (`UserAddressId` 2043671), `DeliveryType` «Seur», `DeliveryPrice` 10.50, оформлення без помилок | `TC-020/recalvi-checkout.png` |
| TC-021 | PASS | 1 | гість, окремий контекст `guest-021`, кожна деталь — окремий кошик з 1 позиції, «España» «28001»: T22 4.76 / «5,76EUR»; T23 5.46 / «6,61EUR»; T24 7.46 / «9,03EUR»; T25 8.86 / «10,72EUR»; T26 7.46 / «9,03EUR» (100 см — без No Encintable); T27 8.96 / «10,84EUR» (101 см — +1,50); усі 200, тип 26, «MADRID», один запит на варіант. Ті самі суми — і в спільному кошику гостя (`itemsId` окремо) | `TC-021/v-T22-28001.png`, `TC-021/v-T27-28001.png` |
| TC-022 | PASS | 1 | на замовленні TC-012 (**10788066**, T06 «08001»). Продавець до оплати: «Cuenta» 1 567,23, останній запис «Paga 17.74 € por pedido #10787679». Після оплати: Профіт `holded` (знімок для 10788066 втрачено через тайм-аут сторінки Профіту — той самий стан підтверджено на оплаченому T01 / «28001» 10788044: `holded`). «CONFIRMAR» → «WaitingDeparture», Профіт `holded`, «Cuenta» 1 567,23 без змін, нових записів немає. «PEDIDO ENTREGADO» → «Departed», ТТН REC000000733788, Профіт `succeeded`, «Historial de operaciones» «10 noviembre 16:55 +476.09 Paga 476.09 € por pedido #10788066», «Cuenta» 2 043,32. Сума зарахування = `SumPrice` 476.09 (товар 459,80 + доставка 16,29, з IVA, без комісії 2,75 %) | `TC-012/b3-seller-before-ship.png`, `TC-012/b4-seller-departed.png` |
| TC-023 | PASS | 1 | замовлення цього прогону T01 / «28001», оплачені (новими не створювались — стан той самий). В1 **10788044** («WaitingSellerComfirmation», Профіт `holded`): покупець «CANCELAR PEDIDO» → діалог «¿Está seguro de que quiere rechazar el pedido? En caso de cancelación, los fondos se devolverán a la tarjeta de la que se debitaron.» → «Error de selección» → `PUT …/rejection` 204 → «Rejected», Профіт `reversed`; коментарі (від старіших): «Cancelado por el comprador. Error de selección.» → «Hemos liberado el importe retenido en tu tarjeta. Tu banco puede tardar unos días en reflejarlo.». В2 **10788056** (продавець «CONFIRMAR» → «WaitingDeparture», Профіт `holded`): діалог «Si cancelas el pedido, perderás el prepago. El prepago cubre los gastos de preparación y logística del vendedor…» → «Rejected», Профіт `reversed`, ті самі повідомлення в тому самому порядку. У «Historial de operaciones» продавця записів по 10788044, 10788056 немає | `TC-023/v1-cancelled-10788044.png`, `TC-023/v2-cancelled-10788056.png` |
| TC-024 | PASS | 1 | замовлення **10788129** (T01 «28001», оплачено, продавець «CONFIRMAR» → «WaitingDeparture», Профіт `holded`). Продавець «CANCELAR PEDIDO» → діалог «¿Está seguro de que desea cancelar el pedido?» → причина «El comprador no responde» → `PUT …/rejection` 204 (`WithPaymentReturn` false) → одразу «Rejected» (через «RejectedRequest» не проходить); Профіт одразу після — `holded`, через ~1 хв — `reversed`. Покупець бачить: «Cancelado por el vendedor. El comprador no responde.» → «Hemos liberado el importe retenido en tu tarjeta…» (у продавця другого повідомлення немає). У «Historial de operaciones» продавця запису по 10788129 немає | `TC-024/seller-reject-10788129.png`, `TC-024/buyer-view-10788129.png` |
| TC-025 | PASS | 1 | покупець 1075831: Febi 2569 «truepaymentvz» → `/cart/checkout/1049862/` «28001», «Calle Genei QA 25» → `genei-delivery-cost` 5.91, «Envío» «7,15EUR», «A pagar» «38,43EUR»; `POST /api/v1/addresses` `DeliveryTypeId` 25 → Id 2043665; замовлення **10788004** (Stripe `cs_test_`: 38,43 € = 37,40 + 1,03; картку на Stripe ввів QA — скрипт агента втратив цифри номера, виправлено). Профіт: після оплати `holded` (каса «STRIPE TEST ABPWORLD», мерчант «наш»); продавець 1049862 «CONFIRMAR» → `PUT …/confirmation` 204, «WaitingDeparture», Профіт `holded`, «Historial de operaciones» без змін (останній запис 09.11); «PREPARADO» → `PUT …/departure-confirmation` 204, «Departed», ТТН «PQ6BR10710691110133001H» «Correos», Профіт `succeeded`, у «Historial de operaciones» «10 noviembre 16:41 +30.25 Paga 30.25 € por pedido #10788004», «Cuenta» 13 458,04 → 13 488,29 | `TC-025/genei-history.png` |
| TC-026 | BLOCKED | 1 | замовлення **10787679** (T01 «28001», «Departed», ТТН REC000000733782, Профіт `succeeded`, продавцю зараховано 17.74). Покупець: дій немає (`AvailableActions` []). `shift-date -5` ×3 (разом −15 днів, межа кейсу): кожен 200, дедлайн «Departed» 02.12 → 27.11 → 22.11 → 17.11; після кожного зсуву в покупця дій немає — дія відмови не зʼявилась, крок 3 виконати неможливо | запити — у звіті |
| TC-027 | PASS (CHK-155 — за рішенням QA 2026-11-10) | 1 | QA API з вкладки покупця (`TEST_BUYER_ES`, роль TestUsers — доступ є). В1 **10788176** («WaitingDeparture» після «CONFIRMAR», Профіт `holded`): `PATCH /api/v1/qa/orders/shift-date?…&shiftDay=-5` 200 (дедлайн 02.12 → 27.11) → `GET …/emulate-auto-reject-order` 200 «Успех! Предоплата: Refunded» → «Rejected», Профіт `reversed`; повідомлення (від старіших): «El pedido fue cancelado automáticamente con un reembolso del prepago. Sin respuesta al pedido.» → «Hemos liberado el importe retenido en tu tarjeta…». В2 **10788037** («WaitingSellerComfirmation», `holded`): `shift-date -5` 200 (дедлайн 14.11 → 09.11, минув) → emulate 200 «Успех! Предоплата: Refunded» → «Rejected», Профіт `reversed`; повідомлення (від старіших): «Hemos liberado el importe…» → «Comentario: Sin respuesta al pedido» → «Cancelado automáticamente. Sin respuesta al pedido.» → «Hemos liberado el importe…» (звільнення коштів двічі, перше — до повідомлення про скасування). У «Historial de operaciones» продавця записів по обох немає | `TC-027/auto-reject-10788176.png`, `TC-027/auto-reject-10788037.png` |

## По перевірках

| CHK | TC | Результат | Факт |
| --- | --- | --- | --- |
| CHK-001 | TC-001 | Pass | обидва варіанти: 200, `DeliveryTypeId` 26, `Price` 4.76; `genei-delivery-cost` немає |
| CHK-002 | TC-001 | Pass | «Entrega a domicilio», полів і тексту «Seur» не додано; «Envío» «5,76EUR» |
| CHK-003 | TC-001 | Pass | «Ciudad» = «MADRID» з `CityName` без вводу |
| CHK-010 | TC-002 | Pass | T01 4.76, тип 26 |
| CHK-012 | TC-002 | Pass | T03 5.46 |
| CHK-014 | TC-002 | Pass | T15 6.12; T07 7.46; T17 8.86; T06 11.14; T08 13.56 |
| CHK-015 | TC-002 | Pass | T19 16.1 (T20 теж 16.1) |
| CHK-025 | TC-002 | Pass | T11 7.46; T16 FR 75001 тип 26 16.81 |
| CHK-028 | TC-002 | Blocked | T21 не продається в 1082119 на стенді — немає пропозиції «SAA» (прайс v3 мав T21; QA перевірити склад «Seur Test») |
| CHK-031 | TC-002 | Pass | T05 × 2 → 8.86, один запит |
| CHK-032 | TC-002 | Pass | T01 + T06 → 11.14 |
| CHK-016 | TC-003 | Pass | 4 індекси — 11.14, тип 26 |
| CHK-017 | TC-003 | Pass | 11 індексів — 11.14, жодного 13.46 |
| CHK-018 | TC-003 | Pass | 5 індексів — 13.46 |
| CHK-019 | TC-003 | Pass | `countryIso=PT`: 13.46, тип 26 |
| CHK-020 | TC-004 | Pass | 07001 7.94 |
| CHK-021 | TC-004 | Pass | 07010 «PALMA DE MALLORCA» 7.94 |
| CHK-022 | TC-004 | Pass | 07500 10.94 |
| CHK-023 | TC-004 | Pass | 07800 / 07860 / 07701 — 19.04 |
| CHK-024 | TC-004 | Blocked | T21 не продається в 1082119 на стенді |
| CHK-033 | TC-005 | Pass | T15 FR 14.55, тип 26 |
| CHK-034 | TC-005 | Pass | 6 країн — суми збіглися, тип 26 |
| CHK-035 | TC-005 | Blocked | T21 не продається в 1082119 на стенді |
| CHK-038 | TC-005 | Pass | GB 18.17 / CH 24.62, тип 25 |
| CHK-039 | TC-006 | Pass | 4 індекси — 200, тип 25, ціна Genei |
| CHK-040 | TC-006 | Pass | 400 `PriceUnavailable`, текст дослівно, «Envío» порожнє |
| CHK-011 | TC-021 | Pass | 1,000 кг → 4.76; 1,001 кг → 5.46 |
| CHK-013 | TC-021 | Pass | 10,000 кг → 7.46; 10,001 кг → 8.86 |
| CHK-026 | TC-021 | Pass | No Encintable: 100 см → 7.46, 101 см → 8.96 (+1,50); частина «понад 50 кг дробова» не покрита — деталі B08 немає |
| CHK-045 | TC-007 | Pass | 11.14 → 13.46, новий запит з `postalCode=08001` |
| CHK-047 | TC-007 | Pass | 26 4.76 → 25 13.45 → 26 4.76 |
| CHK-048 | TC-007 | Pass | індекс і місто очищено, «Envío» порожнє |
| CHK-049 | TC-007 | Pass | 7.46 → 8.86 після повторного вводу індексу (форма гостя очищається при поверненні з кошика — рішення QA 2026-11-06) |
| CHK-042 | TC-016 | Pass | 400 `PriceUnavailable`, текст дослівно, «Envío» порожнє |
| CHK-043 | TC-016 | Pass | кнопка неактивна, запиту створення замовлення немає |
| CHK-127 | TC-016 | Pass | es і pt тексти дослівно |
| CHK-046 | TC-017 | Pass | «28001» `net::ERR_ABORTED`; показано 13.46 / «BARCELONA» / «16,29EUR» |
| CHK-156 | TC-025 | Pass | `holded` → `holded` → `succeeded` на «PREPARADO»; операція продавцю +30.25 лише після «PREPARADO» |
| CHK-066 | TC-009 | Pass | адреса Genei → тип 26, 4.76; замовлення 10788037 «Seur», адреса 2043668 тип 26 |
| CHK-054 | TC-008 | Pass | 10788044: адреса й замовлення тип 26 «Seur» |
| CHK-058 | TC-008 | Pass | лише «PAGAR CON TARJETA» |
| CHK-065 | TC-008 | Pass | адреса типу 26 «28001» у «Direcciones guardadas», підставляється, 4.76 тип 26 |
| CHK-063 | TC-010 | Pass | 4.76 до входу; замовлення 10788056 створено, доставка 5.76 з IVA (4.76 без) |
| CHK-059 | TC-011 | Pass | «Envío» 6,61 = `DeliveryPrice` 6.61 (5.46 + IVA 1.15) |
| CHK-075 | TC-013 | Pass | для неоплаченого замовлення дії «PEDIDO ENTREGADO» немає; статус «WaitingPayment», ТТН немає |
| CHK-057 | TC-014 | Pass | тип 25, 13.45; замовлення «Genei», 16.27 |
| CHK-077 | TC-014 | Pass | ТТН Genei «PQ6BR10710691110133001H», «Correos»; `/seur/` немає |
| CHK-121 | TC-014 | Pass | етикетка PDF 200; відмова покупця → «Rejected» / «Cancelado» |
| CHK-055 | TC-012 | Pass | тип 26, 13.46; «Envío» 16,29 = `DeliveryPrice` 16.29 |
| CHK-082 | TC-012 | Pass | до відправлення «DESCARGAR ETIQUETA» немає |
| CHK-071 | TC-012 | Pass | ТТН REC000000733788, «Departed» |
| CHK-081 | TC-012 | Pass | PDF 200, етикетка з ТТН |
| CHK-089 | TC-012 | Pass | «FINALIZAR EL PEDIDO», «DESCARGAR ETIQUETA», без скасування |
| CHK-069 | TC-012 | Pass | покупець бачить ТТН і посилання SEUR |
| CHK-088 | TC-012 | Pass | у покупця дій немає |
| CHK-119 | TC-012 | Pass | наскрізний сценарій пройдено; трекінг оновив `StatusId` (null → 3) за 12 хв — `TrackingRefreshed` QA звіряє в лозі; видимий текст статусу не змінився |
| CHK-122 | TC-022 | Pass | оплачене замовлення — Профіт `holded` (10788044; для 10788066 — після «CONFIRMAR» теж `holded`), у продавця суми немає |
| CHK-149 | TC-022 | Pass | після «CONFIRMAR» `holded`, «Cuenta» без змін |
| CHK-150 | TC-022 | Pass | після «PEDIDO ENTREGADO» `succeeded`, +476.09 у «Historial de operaciones» |
| CHK-124 | TC-015 | Pass | PT 1000-001: тип 26, 13.46; замовлення 10788119 «Seur» |
| CHK-064 | TC-018 | Pass | 10788129 тип 26 / 4.76; 10788148 тип 25 / Genei 5.91 |
| CHK-067 | TC-018 | Blocked | в оформленні Genei 1049862 адреси типу 26 не показуються (ні в «Direcciones guardadas», ні в `GET /api/v1/addresses`) — після виправлення BUG-001 адреси фільтруються за службою продавця; сценарій «адреса типу 26 у Genei» через інтерфейс не виникає. Рішення QA: перевірка неактуальна → Pass / вручну через API? |
| CHK-068 | TC-019 | Pass | 390×844: 4.76 тип 26, «Envío» 5,76EUR; замовлення 10788176 «Seur» |
| CHK-139 | TC-020 | Pass | ціна Genei 8.68; замовлення 10788182 з адресою типу 26 («Seur») |
| CHK-151 | TC-023 | Pass | 10788044: «Rejected», `holded` → `reversed`, скасування → звільнення коштів, у продавця запису немає |
| CHK-152 | TC-023 | Pass | 10788056 після «CONFIRMAR»: «Rejected», `reversed`, порядок повідомлень той самий, у продавця запису немає |
| CHK-153 | TC-024 | Pass | одразу «Rejected»; Профіт `holded` → `reversed` (~1 хв); повідомлення скасування → звільнення коштів; у продавця запису немає |
| CHK-154 | TC-027 | Pass | 10788176: «Rejected», `holded` → `reversed`, у продавця запису немає |
| CHK-155 | TC-027 | Pass (рішення QA) | 10788037: «Rejected», `reversed` — так; але повідомлення «Hemos liberado el importe…» двічі, перше — до повідомлення про скасування (у ручному скасуванні № 151: скасування → звільнення). Потребує рішення QA: емуляція джоби (`emulate-auto-reject-order`) чи дефект. Рішення QA 2026-11-10: не дефект → Pass |
| CHK-120 | TC-026 | Blocked | після зсуву дат на −15 днів дії відмови в покупця немає (статус «Departed», дедлайн 17.11). Рішення QA: від якої дати рахується «доба після крайньої дати відправки» для Seur і чи є відмова покупця для Seur взагалі (Q-025) |

## Помічено поза кейсами

- TC-023: **потребує рішення QA:** у «WaitingDeparture» (після «CONFIRMAR») діалог скасування покупця попереджає «Si cancelas el pedido, perderás el prepago…», але фактично холд повернуто (`reversed`, «Hemos liberado el importe…»). Текст не відповідає поведінці (можливо, повʼязано з `HoldPolicy` ES/PT).
- TC-018: Stripe Link: для тестового email Stripe пропонує вхід у Link і просить підтвердити телефон — вікно закривається «Назад», але очищує email; скрипт оплати виправлено.
- TC-022: Зарахування продавцю: Seur — повна сума замовлення з доставкою (10788066: 476.09 = 459.80 + 16.29; 10787679: 17.74 = 11.98 + 5.76); Genei (TC-025, 10788004) — лише товар 30.25 без доставки 7.15. Для Q-031 — QA підтвердити, що доставка Seur має зараховуватись продавцю. Сторінка Профіту відповідає ~30 с (тайм-аут 30 с у першій спробі).
- TC-012: етикетка 10788066: відправник знову «28001 MADRID» при отримувачі «08001 BARCELONA» — індекс відправника береться з даних продавця, не з адреси отримувача (питання QA знято). Вага на етикетці 15.63 кг, а в базі для T06 (`DefaultBox`) — 15.72 кг: на ціну не впливає (той самий рядок «Hasta 20 kg»), QA звірити з логом «Genei package composition». `LabelExists` = false, хоча етикетка завантажується.
- TC-008: Рішення QA 2026-11-10: для кейсів Рекалві підходить будь-яка пропозиція «RECAMBIOS AUTO», склад не важливий (Vigo на картці Miraglio 301006C зараз немає).
- TC-008: Рекалві: у пропозиціях «RECAMBIOS AUTO» для Miraglio 301006C немає складу «Vigo» (дані TC-008 крок 6 і TC-020 — `00-input/test-data.md`) — оновити тестові дані.
- TC-025: Профіт: «Касса» — «STRIPE TEST ABPWORLD» (у рецепті `howto/payment-status.md` — «Тестовое окружение»), мерчант «наш» — уточнити рецепт. Genei ТТН «PQ6BR10710691110133001H» — той самий номер, що в 10774417 (2026-11-06): тестовий контур Genei повторює номер. Операція продавцю 30.25 = ціна товару з IVA (25 × 1,21), без доставки.
## Тестові замовлення прогону

| Замовлення | TC | Стан |
| --- | --- | --- |
| 10788004 | TC-025 | Genei, «Departed», Профіт `succeeded` |
| 10788037 | TC-009 | Seur, «WaitingSellerComfirmation» (для TC-023 / TC-027 не використовується) |
| 10788044 | TC-008 | Seur, «WaitingSellerComfirmation» |
| 10788056 | TC-010 | Seur, «WaitingSellerComfirmation» |
| 10788061 | TC-011 | Seur, «WaitingSellerComfirmation» |
| 10788098 | TC-013 | Seur, «WaitingPayment» (не оплачено, автоскасується) |
| 10788100 | TC-014 | Genei, «Rejected» покупцем після «Departed» |
| 10788066 | TC-012, TC-022 | Seur, «Departed», ТТН REC000000733788, Профіт `succeeded` |
| 10788119 | TC-015 | Seur (pt), «WaitingSellerComfirmation» |
| 10788129 | TC-018 | Seur, «WaitingSellerComfirmation» |
| 10788148 | TC-018 | Genei, «WaitingSellerComfirmation» |
| 10788176 | TC-019 | Seur, «WaitingSellerComfirmation» |
| 10788182 | TC-020 | Рекалві 1369756, тип 26, «WaitingSellerComfirmation» |
| 10788044 | TC-023 в1 | «Rejected», Профіт `reversed` |
| 10788056 | TC-023 в2 | «Rejected», Профіт `reversed` |
| 10788129 | TC-024 | «Rejected» продавцем, Профіт `reversed` |
| 10788176 | TC-027 в1 | автоскасування після «CONFIRMAR», «Rejected», `reversed` |
| 10788037 | TC-027 в2 | автоскасування до «CONFIRMAR», «Rejected», `reversed` |
| 10787679 | TC-026 | «Departed», дати зсунуто на −15 днів, Профіт `succeeded` |

## Метрики

- Прогін: `metrics.md` (1 год 17 хв, з них очікування QA 6 хв; 131 виклик моделі; еквівалент API $18.94; 3,5 % місячної підписки). Задача: `../../metrics.md`.
- Висновки: цінові кейси (TC-001…007, 016, 017, 021) зайняли ~15 хв завдяки одному кошику гостя і запитам `seur-delivery-cost` по `itemsId`; основний час — оформлення 14 замовлень і очікування Профіту (~30 с на сторінку); трекінг перевірено паралельно з іншими кейсами.

| Втрата часу | Хв | Як уникнути |
| --- | --- | --- |
| Скрипт оплати губив цифри картки, Stripe Link очищав email (QA ввів картку вручну, 2 повтори) | ~6 | Скрипт `pay.js` виправлено: повільний ввід картки, перевірка значення, закриття вікна Link, повторний email |
| Сторінка Профіту відповідає ~30 с, перший виклик — тайм-аут | ~3 | Чекати `domcontentloaded` до 90 с |
| Перезапуск браузера Playwright під час повернення зі Stripe (втрачено сесії) | ~2 | Повторний вхід за П-1 |
| Остання адреса покупця (PT / Канари) підставлялась у наступні кейси | ~2 | Перед кейсом обирати адресу в «Direcciones guardadas» |

## Що ще можна автоматизувати

- № 87 (відхилення продавцем у «Ожидает отправки») — вручну; фактично виконано в TC-024 (той самий сценарій) — можна перевести в «агент».
- № 85, 90–92 (дії в «Отправлен», завершення) — вручну; QA API (`complete-order`, `shift-date`) тепер доступний агенту — можна перевести в «агент» після рішення по CHK-120.
- № 50–52 (паливна надбавка) — лишаються вручну (зміна даних стенду).
