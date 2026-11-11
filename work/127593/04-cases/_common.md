# Спільне для кейсів 127593

> На цей файл посилаються всі кейси `TC-xxx.md`. Кроки П-1…П-4 агент виконує так, як описано тут; кейс уточнює лише дані (деталь, країну, індекс, роль).

## Обмеження (для всіх кейсів)

- Хост — тільки `es.seller<N>.vus.us` / `pt.seller<N>.vus.us` зі змінних `BASE_URL_ES` / `BASE_URL_PT`; інший хост — зупинись.
- Тільки акаунти з `.env` (тестові користувачі): під іншими працюють бойові контури Stripe і Recalvi.
- Реальні платіжні дані заборонені; Stripe — тестова картка ES 4000 0072 4000 0007, 09/30, CVC 111 (без 3-D Secure). Зʼявилось вікно 3-D Secure або сторінка банку — зупинись, BLOCKED.
- Службові API `/api/v1/seur/*` не викликати (працюють із бойовим SEUR).
- Не натискати у продавця «Заказ доставлен» і дії скасування — якщо кейс прямо не вимагає.
- Капча, 429 або 423 — зупинись, результат BLOCKED.
- Крок неможливо виконати — BLOCKED з описом; не шукай обхідних шляхів і не змінюй кейс.
- Серверних логів агент не бачить. Пункти «у лозі …» з чек-листа в кейси не входять — QA звіряє їх у логах після прогону (перелік — у кожному кейсі, розділ «Для QA після прогону»).

## Як читати ціну

- Ціна — поле `Price` відповіді `GET /api/v1/cart/seur-delivery-cost` (DevTools → Network), **без IVA**. У відповіді є лише `Price`, `Currency`, `Warning`, `DeliveryHours`, `CityName`, `DeliveryTypeId` (код гілки `SeurPriceResponseDTO`, `1e2ca603fa`). Назва зони, тарифний рядок, доплати й надбавка — тільки в лозі, агент їх не перевіряє.
- `DeliveryTypeId` = 26 — порахував Seur; 25 — fallback на Genei; відповідь 400 `{reason}` — не порахував ніхто.
- PASS — `Price` збігається до 0,01 €. Інша сума — FAIL з позначкою «потребує рішення QA»; QA звіряє `Source` / `Used` з логом «Genei package composition». Для деталей з `suspicious` (T09…T12, T21) і без власних замірів (`DefaultBox`: T05, T06, T17…T20) габарити в кошику може змінити AI — очікування в кейсах розраховано без AI (оновлено 2026-11-05).
- Кеш ціни — 2 години на користувача, продавця, країну, індекс і склад кошика: повторний розрахунок того самого кошика показує меншу з цін. На кейси без зміни тарифів і надбавки не впливає.
- «Envío» в інтерфейсі — **з IVA**: на es `Price` × 1,21 (4,76 → 5,76EUR), на pt («Envio») `Price` × 1,23 [зі слів QA, 2026-11-05; розвідка]. «A pagar» = (товари + «Envío») × 1,0275 (комісія маркетплейсу 2,75 %).
- `CityName` приходить великими літерами («MADRID», «LISBOA») — місто порівнюй без урахування регістру.
- Console: 403 на `GET /api/v1/addresses` для гостя і 400 на `seur-delivery-cost` у варіантах, де доставки немає, — очікувані, не FAIL.

## П-1. Доступ і cookie

1. Відкрий `${BASE_URL_ES}` (або `${BASE_URL_PT}`, якщо так у кейсі). Доступ — через VPN QA, пароля стенду немає. Збірка: мітка в шапці сторінки оформлення — `feat-seur-delivery--…-seller1 169b3db0` (на головній під покупцем не видно); додатково функціонально: кошик 1082119 на чекауті викликає `seur-delivery-cost` з `DeliveryTypeId` 26 (T01 / «28001» → `Price` 4.76). Розрахунок пішов через Genei (25) для звичайного індексу Іспанії — зупинись, BLOCKED (оновлено 2026-11-05: стенд seller1).
2. Встанови cookie `showTestUsers` = `true` для хоста стенду (без нього 1082119 у видачі прихований).
3. Увійди під роллю кейсу або лишись гостем, якщо кейс для гостя. Кожна роль — окрема вкладка з власним контекстом (`browser_tabs` → `new`, `isolatedContext`: `buyer-es`, `seller-es`, `buyer-pt`), щоб не перелогінюватись між кроками.
4. Вхід — фрагментом нижче через `browser_run_code_unsafe` (дозвіл QA, 2026-11-05). Фрагмент читає `.env` у браузері через `file://` і сам підставляє значення: **у тексті коду — тільки назви змінних**. Логін і пароль у код, звіт чи чат не вписувати.
5. Перевір у шапці: покупець — «test1 ID: 1075831», продавець Seur — «Seller S. ID: 1082119». Інший акаунт — зупинись.

```js
async (page) => {
  const PREFIX = 'TEST_BUYER_ES', HOST = 'es.seller1.vus.us';   // роль і хост кейсу
  const f = await page.context().newPage();
  await f.goto('file:///Users/oleksandrpc/Desktop/ABP/avto/qaPipeline-repo/.env');
  const txt = await f.evaluate(() => document.body.innerText); await f.close();
  const get = k => { const m = txt.match(new RegExp('^' + k + '=(.*)$', 'm')); return m ? m[1].trim().replace(/^["']|["']$/g, '') : ''; };
  const login = get(PREFIX + '_LOGIN'), pass = get(PREFIX + '_PASSWORD');
  if (!login || !pass) return { error: 'немає ' + PREFIX + '_* у .env' };
  await page.context().addCookies([{ name: 'showTestUsers', value: 'true', domain: HOST, path: '/' }]);
  await page.goto('https://' + HOST + '/'); await page.waitForTimeout(1500);
  const email = page.getByRole('textbox', { name: 'Email' }).first();
  if (await email.isVisible().catch(() => false)) {
    await email.fill(login);
    await page.locator('input[type=password]').first().fill(pass);
    await page.getByRole('button', { name: /^entrar$/i }).first().click();
    await page.waitForTimeout(5000);
  }
  return { url: page.url(), loggedIn: !(await page.getByRole('textbox', { name: 'Email' }).first().isVisible().catch(() => false)) };
}
```

## П-2. Деталь продавця 1082119 у кошик

1. Очисти кошик (якщо в ньому є позиції) — дозволено QA, 2026-11-05, зокрема для `TEST_BUYER_ES`, яким користуються й автотести.
2. Знайди деталь за артикулом у полі «Nombre de la pieza, código, vehículo, VIN» (напр. «0986452024») і відкрий картку деталі (es — `/repuesto-<артикул>-<бренд>-…/`, pt — `/pecas-…/`).
3. У пропозиції з «Vendedor: SAA» (це 1082119) натисни «A LA CESTA» (pt — «ADICIONAR»).
4. Відкрий кошик `/cart/` («Cesta», pt — «Carrinho» / «Minha cesta»): позиція в групі «SAA». Кількість — полем кількості в кошику. Видалення позиції — кнопка в рядку позиції, далі підтвердження (pt — «Sim, excluir»).
5. Кнопка переходу до оформлення: es — «Tramitar Pedido», pt — «COMPRAR»; оплата: es — «Pagar con tarjeta», pt — «PAGUE COM CARTÃO».

Деталі прайсу «Seur_test_pricelist_v2.xlsx» (склад «Seur Test», завантажено 2026-11-05): T01 BOSCH 0986452024 · T02 BOSCH 0986494338 · T03 BOSCH 0986494191 · T04 BOSCH 0986441566 · T05 BOSCH 0986023450 · T06 LUK 415026110 · T07 BOSCH 0986479H46 · T08 BOSCH 0092S50130 · T09 VAG 02E301107 · T10 VAG 02E301103 · T11 BOSAL 803009 · T12 PRASCO SK3501011 · T13 BOSCH 3397118996 · T14 BOSAL 339157 · T15 VAG 7L6615123T · T16 WALKER 23800 · T17 FEBI 107500 · T18 BREMBO 09N23621 · T19 FEBI 173123 · T20 VAG 2R0609617 · T21 VAG 1H0521101.

Прайс «Seur_test_pricelist_v3.xlsx» (2026-11-10, граничні деталі з бази — `00-input/db-search-boundaries.md` § «Відповідь розробника і відбір»): T22 REMSA 001440 · T23 MEYLE 1007500002 · T24 BOSCH 0121715014 · T25 MAHLE 0039280 · T26 FEBI 32485 · T27 TRW JTR3558. [Діють після повторного завантаження прайсу QA]

**Вага й габарити для доставки — з бази, не з прайсу** (QA, 2026-11-05). Дані з бази й розрахунок — `00-input/db-dimensions.md` (T01…T14), `00-input/part-candidates.md` (T15…T21).

## П-3. Розрахунок доставки в кошику

0. У кошику натисни «Tramitar Pedido» — відкриється оформлення `/cart/checkout/1082119/` («Registro del pedido»). Блок доставки є тільки тут, у кошику його немає.
1. У блоці «Entrega» обери «País» (список відкривається кнопкою поруч із полем) і введи «Codigo postal» посимвольно. Зміна «País» очищає індекс і місто.
2. Дочекайся запиту `GET /api/v1/cart/seur-delivery-cost` і зафіксуй: параметри запиту, статус, `Price`, `DeliveryTypeId`, `CityName`; і суму «Envío» в інтерфейсі.
3. Наступний варіант таблиці на тому самому кошику — зміни лише індекс (або країну й індекс) і повтори п. 2. Новий варіант з іншою деталлю — знову П-2.

## П-4. Оформлення замовлення карткою

1. На сторінці оформлення заповни «Dirección» — «Calle de Prueba 1»; у «Destinatario»: «Apellido» — «Seur», «Nombre» — «QA», «Teléfono» — «612345678», «Email» — логін ролі; «CIF/NIF/DNI» — лише якщо форма вимагає (тестовий номер «12345678Z»). [ПРИПУЩЕННЯ: які з полів обовʼязкові під акаунтом — фіксуй у звіті]
2. Натисни «Pagar con tarjeta», на сторінці Stripe введи картку 4000 0072 4000 0007, 09/30, CVC 111, підтверди оплату.
3. Зафіксуй: номер замовлення, URL сторінки після оплати, запит створення замовлення в Network (метод, статус, `deliveryTypeId` і вартість доставки в тілі запиту або відповіді).
