# Зміни в коді: 127593 — інтеграція служби доставки Seur для обраних продавців (avtopro.es)

> Код показує, ЩО перевіряти. Очікуваний результат — тільки з вимог.

| | |
| --- | --- |
| Репозиторій | `/Users/oleksandrpc/Desktop/ABP/avto/AvtoPro` (тільки читання) |
| Гілка | `delivery/seller/feat-seur-delivery` · HEAD `1e2ca603fa` (03.11.2026) |
| База | `origin/master` `11d09ca104` · merge-base `29e3155a19` |
| Обсяг | 132 файли · +9253 / −1627 рядків · 63 коміти |
| Дата аналізу | 2026-11-04 |

**Звʼязок з `task-context.md`.** QA аналізував HEAD `de7009dacb` (база `ad7b886128`). Гілку відтоді перебазовано на новий master, і зміни гілки не змінились: ті самі 132 файли, +9253 / −1627, коміти ті самі за змістом. Між `de7009dacb` і `1e2ca603fa` у файлах гілки різняться лише 3 `.csproj`, і ці зміни прийшли з master. Тож факти `task-context.md` § 3 лишаються актуальними. Цей файл їх **не повторює**, а доповнює тим, чого там немає, і посилається на § 3 там, де факт уже описано.

## Коротко

- **Що зроблено.** Гілка додає розрахунок доставки Seur за статичними тарифами з БД (паливна надбавка, доплати, fallback на Genei), а також ТТН, етикетку, скасування, трекінг і службові API. Seur увімкнено для одного продавця 1082119 на avtopro.es і avtopro.pt.
- **Спільний модуль.** Розрахунок ваги й габаритів посилки винесено з `GeneiDeliveryManager` у спільний `ShipmentDetailsManager`. Тепер ним користуються кошик, оформлення, картка товару, договір дистанційного продажу і створення відправлень Genei.
- **Нове порівняно з `task-context.md`, головні ризики:**
  1. **Рекалві у фронтенді.** Нова адреса Рекалві, ймовірно, зберігається з типом 25 замість 26: для неї ціну рахує Genei, а відповідь Genei не містить `DeliveryTypeId`.
  2. **Рекалві при оформленні.** До типу 26 у Рекалві тепер застосовуються правила Genei, яких раніше не було: помилка «немає агентства» і фіксована ціна, коли Genei недоступний.
  3. **Рекалві при скасуванні.** Скасування будь-якого замовлення типу 26 з ТТН (зокрема Рекалві) викликає скасування сбору в SEUR.
  4. **Службові API `api/v1/seur/shipments*`** завжди звертаються до **бойового** SEUR, навіть для тестових користувачів.
  5. **Порожній кошик.** Розрахунок Seur для кошика без позицій повертає 200 з ціною 0 і типом 26.
  6. **Доступ до етикетки** змінено: тепер її віддають тільки продавцю або покупцю замовлення. Це стосується й Genei.
- **Обсяг змін.** Перекладів і міграцій у гілці немає. Нові тексти помилок бекенду — тільки англійською, у коді.

## Що змінено

| Група | Файли | Що змінилось |
| --- | --- | --- |
| Бекенд / API | `ShoppingCartController.cs`, `SeurDeliveryController.cs`, `SeurTariffController.cs`, `GeneiDeliveryController.cs`, `OrderActionsController.cs` | Новий `GET api/v1/cart/seur-delivery-cost`; службові API `api/v1/seur/*`. Ендпоінт наявності етикетки `api/v1/genei/shipments/{orderId}/label-exists` тепер обслуговує й Seur і перевіряє, що запит робить продавець. Завантаження етикетки — з перевіркою «продавець або покупець» |
| Бекенд / логіка | `Common/Library/Seur/*` (нові), `ShipmentDetailsManager.cs` (новий, 989 рядків), `GeneiDeliveryManager.cs` (−1004), `DeliveryPriceManager.cs`, `OrderManager.cs`, `OrderActionManager.cs`, `SellerOrderActionResolver.cs`, `DistanceSalesContractManager.cs`, `GeneiManager.cs` (лише перейменування типів), `GeneiPostalCodeResolver.cs` (новий) | Розрахунок, кеш ціни, оформлення, ТТН, скасування, етикетка; перенесення розрахунку весогабаритів |
| Бекенд / інтеграція | `Abp.Avtopro.Dal.Seur/*` (клієнти, DTO, опції), `SeurPlugin.cs`, `SeurTrackingNumberHandler.cs` (новий) | Тестове й робоче середовища SEUR, токени, логування HTTP, перевірка ТТН через трекінг SEUR |
| Фронт | `cart/constants.ts`, `cart/models/Model.js`, `cart/services/CartService.js`, `api/v1/model/Cart.js`, `cart/containers/AddressFormContainer.jsx`, `cart/components/AddressForm.jsx`, `cart/components/Order/style.less` | Для 1082119 ціну рахує Seur; тип адреси (25 / 26) береться з відповіді; при зміні країни ціна скидається і для 26; список збережених адрес; шрифт суми групи на xs |
| Переклади | — | **Змін немає.** Нових ключів немає. Помилки Seur з бекенду — англійські рядки в коді (див. «Тексти і переклади») |
| Міграції БД | — | **Немає в репозиторії.** Процедури `seur.get/update_*_shipping_tariffs`, `seur.get_fuel_surcharge_rates`, `seur.update_fuel_surcharge_rate` викликаються з `SeurRepository.cs`, але їх створення в гілці не видно |
| Конфіг / прапорці | `appsettings.json` (SiteCore), `Settings.cs`, `AzureKeyVaultConfig.cs`, `Program.cs`, `DependanceInjection.cs` | Секція `Seur`: `Ccc`, `CccTest`, `BaseUrl`, `BaseUrlTest`; нові налаштування `SeurBaseUrlTest`, `SeurCcc`, `SeurCccTest`. **Feature flag немає** — увімкнення списком ID у коді |
| Фонові задачі | `Abp.Avtopro.OrdersFunctions/Services/AutoRefresherDeliveryTrackingStatusesService.cs` | Трекінг SEUR вибирає середовище за покупцем і продавцем замовлення |
| Тести | `Tests/Library.Tests/Seur/*` (11 файлів), `SellerOrderActionResolverTests.cs` (+18) | Unit-тести алгоритму ціни, доплат, надбавки, кешу, rollout, трекінгу, дії «завантажити етикетку» |
| Інше | `Docs/ai-context/projects/Abp.Avtopro.Dal.Seur.md` | Опис проєкту для розробників |

## Факти для тестування

### Ендпоінти

| Метод і маршрут | Що нового | Валідації / коди помилок | Права | Код |
| --- | --- | --- | --- | --- |
| `GET api/v1/cart/seur-delivery-cost?sellerId&countryIso&postalCode&itemsId` | Ціна Seur або Genei (fallback); `DeliveryTypeId` 26 / 25 | Продавець не зі списку → fallback на Genei. Genei теж не порахував → 400 `{reason}`. Інша помилка → 400 з текстом винятку. Запит скасовано клієнтом → 499. **Кошик без позицій цього продавця → 200, `Price` = 0, `DeliveryTypeId` = 26** | гість і авторизований | `ShoppingCartController.cs:257`, `:285`, `:316`, `:355`; `DeliveryPriceManager.cs:1493`–`1512` |
| `GET api/v1/seur/tariffs`, `POST api/v1/seur/tariffs` | Тарифи National / Europe | Див. `task-context.md` § 3.5. `POST` з порожнім документом → 400 | BPanel: FullAccess, Developer, Support, QA | `SeurTariffController.cs:10`, `:68` |
| `GET` / `POST api/v1/seur/fuel-surcharge-rates` | Паливна надбавка | Без `month` або без `percent` → 400 без тексту; решта — `task-context.md` § 3.5 | те саме | `SeurTariffController.cs:43`–`49` |
| `POST api/v1/seur/shipments` | Створення сбору з довільного тіла | Без тіла → 400 «Request is required». **Середовище не визначається: завжди бойовий SEUR** | те саме | `SeurDeliveryController.cs:39`–`54` |
| `DELETE api/v1/seur/shipments/{collectionCode}` | Скасування сбору | **Завжди бойовий SEUR** (`isTest` не передається) | те саме | `SeurDeliveryController.cs:80`–`88` |
| `GET api/v1/seur/shipments/{collectionCode}/label` | PDF етикетки | **Завжди бойовий SEUR**; номер ТТН зі списку тестових → 404 | те саме | `SeurDeliveryController.cs:130`–`162` |
| `GET api/v1/genei/shipments/{orderId}/label-exists` | Тепер для Genei і Seur. З цього маршруту сторінка замовлення раз на 60 с питає, чи готова етикетка | Замовлення не знайдено → 404. Користувач не продавець замовлення → 403 (**нове й для Genei**). Seur: продавець не зі списку або немає ТТН → 404. Етикетки немає → 404, тож кнопка лишається в стані «Preparando etiqueta...» | авторизований продавець замовлення | `GeneiDeliveryController.cs:458`–`479`; `orders/containers/GeneiStatusPoller.ts` |
| `GET api/v1/orders/{orderId}/download-shipment-document` | Seur-гілка; **змінено передачу користувача**: раніше передавався продавець замовлення, тепер поточний користувач | Не продавець і не покупець → 406 (`OrderActionAccess_AccessError`). PDF немає → 404. Інша помилка → 400 | **продавець або покупець** замовлення | `OrderActionsController.cs:383`; `OrderActionManager.cs:1442`, `:1472` |

### Валідації і ліміти

Ліміти алгоритму ціни (31,5 кг, 175 / 300 см, кубатура 5000, межі доплат 40 / 60 кг, 100 / 175 / 300 / 500 см, префікси індексів, Palma) **звірено з кодом**: вони збігаються з `task-context.md` § 3.4 (`SeurApiManager.cs:38`–`62`, `:89`, `:356`, `:684`, `:736`; `SeurHandlingClassifier.cs:14`–`43`). Нижче — тільки те, чого в § 3.4 немає.

| Поле / параметр | Правило в коді | Значення | Код |
| --- | --- | --- | --- |
| Межі доплат за вантаж | Нерівності строгі: рівно 40 кг, рівно 175 см, рівно 300 см суми — без Fuera de Norma A; рівно 60 кг — без B. No Encintable — вага **< 40** кг і сторона **> 100** см | 40 / 60 кг; 100 / 175 / 300 / 500 см | `SeurHandlingClassifier.cs:41`–`43` |
| Ключ кешу ціни | `seur:quote:{userId}:{sellerId}:{COUNTRY}:{POSTAL}:{hash позицій і кількостей}`; індекс лише обрізається від пробілів і переводиться у верхній регістр | TTL 2 год | `SeurDeliveryManager.cs:69`, `:91` |
| Оформлення: кеш ціни | Кеш шукається за `userId` того, хто оформлює, і за індексом **збереженої адреси**. Якщо гість увійшов в акаунт або індекс записано інакше, ніж у кошику, — помилка «quote has expired» | — | `OrderManager.cs:1232`–`1238` |
| Оформлення: умова розрахунку Seur | Ціна рахується лише тоді, коли весогабарити визначено для **кожної одиниці** товару і вибрано магазин; інакше `DeliveryPrice` не задається | — | `OrderManager.cs:1201` |
| Дата забору | `DateTime.Today + 1` день, субота й неділя пропускаються; час **сервера**; свята не враховуються | 10:00 | `SeurDeliveryManager.cs:168`–`180` |
| Місяць паливної надбавки | `DateTime.UtcNow` | 1-ше число місяця за UTC | `SeurApiManager.cs:145` |

### Тексти і переклади

Ключів перекладів у гілці не додано й не змінено. Покупець і продавець бачать такі тексти:

| Ключ / текст | ua | es | pl | pt | tr | avto | Код |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `DeliveryNotAvailableText` (наявний; тепер його показує й Seur, коли не порахували ні Seur, ні Genei) | не перевірялось | «La entrega en la ciudad indicada no está disponible.» | не перевірялось | «A entrega na cidade indicada não está disponível. Por favor, verifique os dados introduzidos ou selecione outra localidade mais próxima.» | не перевірялось | не перевірялось | `Cart.es.resx`, `Cart.pt.resx`; `cart/models/Model.js:688` |
| `OrderActionsButtonTitleDownloadShipment` / `…Preparing` / `…Downloading` / `…Error` (наявні; тепер і для Seur) | не перевірялось | «Descargar etiqueta» / «Preparando etiqueta...» / «Descargando...» / «Error, inténtelo de nuevo» | не перевірялось | «Descarregar etiqueta» / «Preparando etiqueta...» / «Baixando...» / «Erro, tente novamente» | не перевірялось | не перевірялось | `Cart.es.resx`, `Cart.pt.resx`; `orders/components/OrderActions/index.jsx:719`–`790` |
| «SEUR cart quote has expired. Refresh the cart delivery price before checkout.» | **немає ключа** | **немає** | **немає** | **немає** | **немає** | **немає** | `OrderManager.cs:1238` — англійський рядок у коді |
| «SEUR delivery is not enabled for this seller.» | **немає ключа** | **немає** | **немає** | **немає** | **немає** | **немає** | `OrderManager.cs:647`; `SeurDeliveryManager.cs:102` |
| «Order cannot be confirmed with delivery until it is paid.» (такий самий рядок уже є для Genei) | **немає ключа** | **немає** | **немає** | **немає** | **немає** | **немає** | `OrderActionManager.cs:522` |

> Як ці англійські рядки потрапляють в інтерфейс (показуються як є чи замінюються загальним текстом), з коду контролерів оформлення не видно — це Q-005.

### Площадки, ролі, прапорці

| Що | Умова в коді | Де діє | Код |
| --- | --- | --- | --- |
| Площадки | Окремої перевірки площадки для Seur немає. Форма адреси вмикає логіку Seur для ES / PT (`isEsOrPt`); тип тарифу визначає країна отримувача (ES / PT — National, решта — Europe) | avtopro.es (30), avtopro.pt (618); на інших площадках — те, що дозволяє форма адреси | `AddressFormContainer.jsx:578`; `SeurApiManager.cs` |
| Продавці Seur (бекенд) | `StaticUserHelper.s_seurSellers` = {1082119}, `IsSeurForcedSeller()` | кошик, оформлення, ТТН, дія «завантажити етикетку», `label-exists` | `StaticUserHelper.cs:62`–`68` |
| Продавці Seur (фронт) | `SEUR_TEST_SELLER_ID` = 1082119 — **тільки** для нього викликається `seur-delivery-cost`. `SEUR_SELLER_IDS` = [1369756, 1082119] — тип адреси 25 / 26 і фільтр збережених адрес [18, 19, 25, 26] | кошик | `cart/constants.ts:5`–`12`; `cart/models/Model.js:653`–`657` |
| Тестові користувачі | **`StaticUserHelper.TestUsers` у гілці не змінено**; 1082119 там уже був (рядок «Delivery Team») | див. «Тестові користувачі й середовище SEUR» нижче | `StaticUserHelper.cs:22`–`40` |
| Ролі BPanel | `BPanelCustomAuthorize(roles: "FullAccess,Developer,Support,QA")` на `SeurTariffController` і `SeurDeliveryController` | службові API | `SeurTariffController.cs:10`; `SeurDeliveryController.cs:19` |
| Feature flag | **немає** | — | — |

### Тестові користувачі й середовище SEUR (`StaticUserHelper.cs`)

- **Що змінено:** додано лише `s_seurSellers` = {1082119} і `IsSeurForcedSeller()` (+8 рядків). Список `TestUsers` і `IsAdminOrTestUser` **не змінювались**.
- **Як вибирається середовище:** `isTest = TestUsers.Contains(покупець) || TestUsers.Contains(продавець)`. Так визначається середовище для розрахунку в кошику, оформлення, ТТН, скасування, етикетки на сторінці замовлення, трекінгу й перевірки ТТН (`DeliveryPriceManager.cs:1556`, `OrderManager.cs`, `SeurDeliveryManager.cs`, `OrderActionManager.cs:1134`, `:1475`, `AutoRefresherDeliveryTrackingStatusesService.cs`, `SeurTrackingNumberHandler.cs:32`).
- **Наслідки для тестування:**
  1. 1082119 є в `TestUsers`, тому **будь-який** покупець, навіть не тестовий, отримує для нього SEUR PRE (`servicios.apipre.seur.io`, тестовий CCC). На стенді з цим продавцем бойові сбори не створюються.
  2. Бойовий шлях SEUR (робочий CCC, «ABPWORLD») на стенді безпечно не перевірити: потрібен продавець зі списку Seur, якого немає в `TestUsers`, і нетестовий покупець. Це заборонено правилами репозиторію. Бойовий шлях покривають лише unit-тести (`SeurOptionsTests`, `SeurRolloutTests`).
  3. Реальні акаунти, які розробники додадуть у `s_seurSellers` перед релізом, **не входять** у `TestUsers`. Для них ТТН створюються в **бойовому** SEUR, якщо покупець не тестовий. Тестувати під такими акаунтами на стенді можна тільки з тестовим покупцем.
  4. Довідники SEUR (міста й послуги між депо) **завжди** беруться з бойового API, незалежно від `isTest` (`SeurDeliveryClient.cs:66`, `:101`). Тож розрахунку в кошику потрібен доступ стенду до бойового SEUR.
  5. Службові API `api/v1/seur/shipments*` `TestUsers` **не враховують** і завжди йдуть у бойовий SEUR. `POST /shipments` із заповненим тілом створить справжній (платний) сбір.
  6. `SeurOptions.GetBaseUrl(isTest)` повертає `BaseUrlTest` без запасного значення, хоча коментар у коді обіцяє його (`SeurOptions.cs:26`–`32`). Налаштування `SeurBaseUrlTest` / `SeurCccTest` додано в `appsettings.json` сайту. У `Abp.Avtopro.OrdersFunctions/local.settings.json` є лише `SeurBaseUrl`. Якщо на стенді у фонових функціях `SeurBaseUrlTest` не задано, трекінг тестових ТТН поверне «статус не визначено».

### Статуси, фонові задачі, інтеграції, міграції

| Що | Зміна | Наслідок для тесту | Код |
| --- | --- | --- | --- |
| «Замовлення відправлено», тип 26 | Для продавця зі списку Seur створюється сбір; продавець не зі списку з типом 26 (Рекалві) йде звичайним шляхом — статус «Відправлено» без ТТН | Рекалві: поведінка як на master | `OrderActionManager.cs:517`–`525` |
| Помилка SEUR при створенні ТТН | `CreateShipmentAsync` кидає виняток (немає `collectionRef`, відмова SEUR, недоставний напрямок) | Що бачить продавець, з коду дії не видно; статус не змінюється | `SeurDeliveryManager.cs:202`–`205` |
| Скасування / відхилення замовлення | Якщо тип 26 і є ТТН → `CancelShipmentAsync`. **Перевірки продавця зі списку Seur немає; номери тестових ТТН не виключаються** (для Genei виключаються) | Скасування замовлення Рекалві з ТТН «Seur 24 Horas» викличе скасування в SEUR (бойовий, якщо учасники не тестові). Помилка лише логується | `OrderActionManager.cs:1131`–`1159`; порівняти з Genei `:1065`–`1066` |
| Трекінг (OrdersFunctions) | Для SEUR потрібне замовлення (інакше виняток). Середовище — за покупцем і продавцем | Замовлення Рекалві тестового покупця тепер трекаються в SEUR PRE (раніше — бойовий) | `AutoRefresherDeliveryTrackingStatusesService.cs:178`–`196`; `SeurPlugin.cs:44`–`50` |
| Ручне введення ТТН для типу 26 | Новий `SeurTrackingNumberHandler`: номер приймається, якщо SEUR його знаходить (або він зі списку тестових) | Ручне введення ТТН продавцем для замовлень типу 26, зокрема Рекалві, тепер перевіряється через SEUR | `SeurTrackingNumberHandler.cs:27`–`38`; `TrackingManager.cs:660`–`679` |
| Міграції | Немає в гілці | Наявність процедур `seur.*` на стенді — передумова | — |

## Вплив і регрес

| Модуль / місце | Чому зачеплено | Автотести | Код |
| --- | --- | --- | --- |
| Genei: розрахунок у кошику | Весогабарити, магазин відправника, індекс відправника — тепер з `ShipmentDetailsManager` / `GeneiPostalCodeResolver` | немає (є лише інтеграційний `GeneiApiClientIntegrationTests`) | `DeliveryPriceManager.cs`; `ShipmentDetailsManager.cs` |
| Genei: оформлення | Ті самі методи; гілка Genei тепер також для «Рекалві + тип 26» | немає | `OrderManager.cs:1000`–`1180` |
| Genei: створення відправлення, етикетка, скасування | `GeneiDeliveryManager` переписано на `ShipmentDetailsManager`; змінено передачу користувача при завантаженні етикетки; `label-exists` — нова перевірка «тільки продавець» | дія «завантажити етикетку» — є unit-тест `SellerOrderActionResolverTests`; решта — немає | `GeneiDeliveryManager.cs`; `OrderActionsController.cs:383`; `GeneiDeliveryController.cs:458` |
| Картка товару: оцінка доставки | `GetDeliveryCostAsync` → `ShipmentDetailsManager.ResolveProductCardPackageAsync` (перенесено) | немає | `DeliveryPriceManager.cs:206`, `:226` |
| Договір дистанційного продажу | `GetSelectedShop` з `ShipmentDetailsManager` | немає | `DistanceSalesContractManager.cs:560` |
| Форма адреси (ES / PT): підказки індексів Genei | Тип `GeneiPostalCodeResponse` → `PostalCodeResponse` | немає | `GeneiManager.cs:458`–`636` |
| Рекалві (1369756): адреси | `AddressFormContainer`: тип 26 тепер береться з відповіді розрахунку; для Рекалві розрахунок іде через Genei, а у відповіді Genei немає `DeliveryTypeId` | немає | `AddressFormContainer.jsx:684`–`700`, `:775`–`781`; `GeneiDeliveryPriceDTO.cs` |
| Рекалві: оформлення | Гілка Genei тепер кидає `GeneiPriceNotAvailableException`, якщо не призначено агентство, а при недоступності Genei ставить фіксовану ціну. Раніше обидва правила діяли лише для типу 25 | немає | `OrderManager.cs:1140`, `:1174` |
| Рекалві: скасування, трекінг, ручне введення ТТН | Див. «Статуси, фонові задачі…» | немає | `OrderActionManager.cs:1131`; `SeurPlugin.cs`; `SeurTrackingNumberHandler.cs` |
| Кошик: перемикання країни, скасування запитів | Спільний `getDeliveryPrice` для Genei і Seur, лічильник запитів | немає | `cart/models/Model.js:644`–`700`; `AddressForm.jsx:1303`–`1311` |
| Мобільна версія кошика | Шрифт `cart-item-group__total-value` = 16 на xs | немає | `cart/components/Order/style.less:331` |

## Звірка із задачею

### Неописані зміни

| Що в коді | Код | Що робити |
| --- | --- | --- |
| Службові API `api/v1/seur/shipments*` завжди звертаються до бойового SEUR, навіть для ТТН тестових замовлень | `SeurDeliveryController.cs:51`, `:88`, `:137` | Питання розробнику (Q-016); у чек-листі — не викликати `POST /shipments` з тілом |
| `seur-delivery-cost` для кошика без позицій продавця повертає 200, `Price` = 0, тип 26 | `DeliveryPriceManager.cs:1493`–`1512` | Питання (Q-017); перевірка через API |
| Етикетку може завантажити покупець замовлення, а не лише продавець; чужий користувач отримує відмову (раніше етикетку будь-якого замовлення віддавали будь-кому) | `OrderActionManager.cs:1442`; `OrderActionsController.cs:383` | Питання (Q-018); перевірка доступу, зокрема для Genei |
| `label-exists` відповідає 403 усім, хто не є продавцем замовлення, — і для Genei | `GeneiDeliveryController.cs:462`–`463` | Регрес Genei |
| Скасування сбору в SEUR для **будь-якого** замовлення типу 26 з ТТН, зокрема Рекалві; тестові номери ТТН не виключаються | `OrderActionManager.cs:1131` | Питання (Q-019); регрес Рекалві |
| Рекалві + тип 26 при оформленні: нова помилка «немає агентства» і фіксована ціна при недоступності Genei | `OrderManager.cs:1140`, `:1174` | Питання (Q-020); регрес Рекалві |
| Трекінг і ручне введення ТТН для типу 26 перевіряють номер через SEUR; для тестових учасників — у PRE | `SeurTrackingNumberHandler.cs`; `AutoRefresherDeliveryTrackingStatusesService.cs:178` | Регрес Рекалві; перевірка ручного введення ТТН |
| Оцінка доставки на картці товару для 1082119 лишилась Genei, а в кошику — Seur | `DeliveryPriceManager.cs:145`–`330` (Seur не викликається) | Питання (Q-021) |
| Довідники SEUR (міста, послуги) — завжди з бойового API | `SeurDeliveryClient.cs:66`, `:101` | Передумова стенду; для відома |
| Етикетки для ТТН із PRE немає → `label-exists` 404 → кнопка «Descargar etiqueta» назавжди в стані «Preparando etiqueta...», опитування раз на 60 с | `GeneiDeliveryController.cs:473`–`479`; `GeneiStatusPoller.ts` | Уточнює Q-007 |

### Не знайдено в коді

| Вимога (цитата) | Де шукали | Примітка |
| --- | --- | --- |
| «лишити можливість швидко відкрити його ширше після тестування» (`task-context.md` § 1) | `StaticUserHelper.cs`, `cart/constants.ts`, пошук `FeatureFlag` / `IsFeatureEnabled` у змінених файлах | Прапорця чи налаштування немає. Список продавців зашитий у трьох місцях, і фронт підтримує лише одного продавця (Р-8) |
| Міграції для таблиць і процедур тарифів SEUR | diff гілки (`*.sql`, `Abp.Avtopro.DB`) | Можуть бути в окремому репозиторії БД — не стверджуємо, що їх немає |
| Логування «відстежувати розраховану вартість і якість доставки» (§ 1): відсоток і місяць паливної надбавки | `SeurApiManager.cs` (лог `Priced`) | У лог не пишуться — уже є в task-context § 3.4 п. 15 |

### Розбіжності

| Вимога (цитата) | Що в коді | Код | Пропозиція |
| --- | --- | --- | --- |
| «**Рекалві (1369756):** … Адреси й замовлення мають тип 26, але ціна рахується через Genei» (`task-context.md` § 2) | Нова адреса Рекалві зберігається з типом, який повернув розрахунок. Розрахунок Рекалві йде через `genei-delivery-cost`, у відповіді якого `DeliveryTypeId` немає, тому лишається тип із форми, тобто 25. Раніше фронт примусово ставив 26 | `AddressFormContainer.jsx:684`–`700`, `:775`–`781`; `cart/models/Model.js:653`–`675`; `GeneiDeliveryPriceDTO.cs` | Ймовірний дефект регресу — перевірка № 140 у `03-checklist.md` (v3); RD-001 у коментар розробнику |
| «**Погоджено:** у всіх випадках, коли Seur не може порахувати доставку, ціну рахує Genei» (§ 1 зміни п. 5) | При оформленні fallback на Genei немає: відсутня надбавка або прострочений кеш ціни → помилка оформлення | `OrderManager.cs:1232`–`1238` | Уже в task-context (Р-2), Q-005 |
| «Для обраних продавців розрахунок іде через Seur … У замовленні має бути тип доставки 26» (§ 1) | Кошик без позицій продавця → `Price` 0 і тип 26 | `DeliveryPriceManager.cs:1512` | Q-017 |
| «Тестове середовище вмикається, якщо покупець або продавець є в `StaticUserHelper.TestUsers`» (§ 2) | Для службових API `api/v1/seur/shipments*` це правило не діє — завжди бойовий SEUR | `SeurDeliveryController.cs` | Q-016 |
| «скасування доставки в Seur при скасуванні замовлення» (§ 1) — для обраних продавців | Скасування в SEUR викликається для **всіх** замовлень типу 26 з ТТН, зокрема Рекалві, чиї відправлення створює не Avtopro | `OrderActionManager.cs:1131` | Q-019 |

## Документація ↔ код

> Звірка з CodeWiki (`/Users/oleksandrpc/Desktop/ABP/avto/CodeWiki/CodeWiki/kb`), 2026-11-04. HEAD гілки той самий (`1e2ca603fa`), тож код повторно не аналізувався. Рядки з позначкою «звірено» перевірено точковим читанням коду гілки (`git show` / `git diff` від merge-base `29e3155a19`), щоб розвʼязати суперечність. Усі нотатки CodeWiki мають `status: unverified`: зони про доставку EU датовані 01.09.2026, Genei — 08.08.2026, замовлення — 17.08.2026; PR цієї гілки в них не відображено. Відповіді на питання — `01-answers.md`.

### Де гілка змінила поведінку, описану в CodeWiki

| Що в CodeWiki (нотатка) | Що в гілці | Наслідок для тесту |
| --- | --- | --- |
| Seur «вмикається лише для Рекалві», ціна — через Genei, ТТН не створюється, відправлення не скасовується, етикетки немає, трекінг — тільки ТТН Рекалві (`Службы-доставки-EU/Обзор/*`, `Seur/Seur-особый-случай`, `Genei/Seur-что-переиспользуется-от-логики-Genei`) | Для 1082119 — власний розрахунок за тарифами, сбор при «Замовлення відправлено», етикетка, скасування, трекінг, логування (`Common/Library/Seur/*`) | Розділи «Seur» у CodeWiki застаріють після злиття — кандидат на автооновлення вікі. Як базу регресу Рекалві використовувати ці нотатки можна: вони описують master |
| Ціна Seur у кошику й при оформленні рахується гілкою Genei (`Genei/Оформление-заказа-чекаут-с-доставкой-Genei`, `Заказы/Шаг-6.-Стоимость-доставки`: «Genei или Seur → резерв: цена из корзины») | Оформлення Seur: `GetPriceAsync` без fallback; кеш кошика відсутній → `SeurPricingException`; гілка Genei тепер для «Рекалві + тип 26» (`OrderManager.cs:1001`–`1002`, `:1232`–`1238`) | № 60, 61, 125; Q-005 |
| Для типу 26 не діють правила Genei «без агентства замовлення не створюється» і «10 € / IVA при недоступності Genei» (`Genei/Seur-что-переиспользуется-от-логики-Genei`) | Для Рекалві з типом 26 діють (`OrderManager.cs:1140`, `:1174`) | № 141; Q-020 |
| Невідомі помилки оформлення → 500 (`Заказы/Оформление-заказа/Коды-ошибок-оформления`) | **Звірено:** `SeurPricingException` у `OrdersApiController` не обробляється — загальний `catch` пише лог 946133 і прокидає виняток → 500 без тексту (`OrdersApiController.cs:552`) | № 60, 61, 125 |
| Помилки створення накладної: продавцю — локалізований текст, не текст винятку (`Genei/Обработка-ошибок-создания-накладной`) | **Звірено:** винятки Seur потрапляють у загальний `catch` → `OrderDepartureConfirmation_GeneiUnexpectedError`: es «No se ha podido crear el envío. Inténtalo de nuevo o contacta con soporte.», pt «Não foi possível criar o envio. Tente novamente ou contacte o suporte.» (`OrderActionsController.cs:144`). Неоплачене замовлення → `OrderActionDepartedConfirmationException` → `OrderDepartureConfirmation_ValidationError`, перекладу es / pt немає — англійський текст за замовчуванням (`:108`; так само для Genei) | № 79, 126; Q-022 закрито |
| Фіксована регіональна ціна й дефолт 15 € виключають тільки Genei, тож для Seur спрацьовують (`Seur/Seur-особый-случай`; `_questions.md` Q-2026-09-01-205) | **Звірено:** умова та сама (`OrderManager.cs:894`–`917`, `DeliveryTypeId != Genei`), блок виконується до розрахунку Seur | Р-1 з `task-context.md` уточнено: якщо весогабарити визначено не для всіх одиниць, у замовленні буде регіональна ціна продавця для типу 26 або 15 € (лог 946214), а не 0 € — № 59 |
| Ручне введення ТТН для Seur не передбачено; належність ТТН для EU-доставок не перевіряється — обробник не зареєстрований (`Действия-и-ттн/Ввод-ТТН-через-PATCH-tracking-info-проверки`) | Новий `SeurTrackingNumberHandler` для типу 26 (`SeurTrackingNumberHandler.cs`, `DependanceInjection.cs:883`). Він спрацьовує не лише при ручному введенні, а й в автоматичній повторній перевірці при кодах трекінгу 7 / 8 (`TrackingManager.TnnBelongCheckAsync`); непройдена перевірка за CodeWiki (`Заказы/Проверка-ТТН-на-отделении`) скасовує замовлення | № 80, 92, 145; Q-028 — ризик для Рекалві тестових покупців (перевірка в SEUR PRE) |
| `label-exists` уже перевіряв, що запит робить продавець замовлення (`Genei/Служебный-и-публичный-API-Genei`); етикетку завантажує учасник замовлення (`Genei/Этикетка-скачивание-и-кэш-готовности`) | Додано явне `order.SellerId != UserId → Forbid()` для всіх типів і гілку Seur (`GeneiDeliveryController.cs:458`–`479`); у `download-shipment-document` передається поточний користувач замість продавця | Попередній висновок цього файлу «403 — нове й для Genei» може бути неточним — Q-029; № 132 |
| Трекінг Seur: ~120 кодів у `NovaPoshtStatusCode`, помилки глушаться без логування, облікові дані захардкоджено (`Трекинг-и-статусы/*`; `_questions.md` Q-2026-09-01-203, -206) | `SeurPlugin` вибирає середовище за покупцем і продавцем, клієнти SEUR — з `SeurOptions` | Мапінг і автозавершення — № 91 (Q-006 закрито). Відмову отримувача (`RecipientFailure_102`, `_111`) у `SeurPlugin.MapStatus` закоментовано — такі статуси стають «Статус не раскрыт» і замовлення не скасовують (у гілці не перевірялось) |

### Де CodeWiki застаріла незалежно від гілки

| Нотатка CodeWiki | Що в коді (master і гілка) | Наслідок |
| --- | --- | --- |
| `Действия-и-ттн/Действия-продавца-и-покупателя-по-статусам-EU`, `_questions.md` Q-2026-09-01-204: продавець Seur у «Ожидает отправки» не може скасувати замовлення | **Звірено:** `WaitingDepartureStrategy` з `HoldPolicy.IsExtendedHoldSite` (ES / PT) дає продавцю пряму відмову для передплаченого замовлення будь-якого типу; у гілці стратегії не змінювались | № 87 — оракул «як Genei»; ⚠ Документація |
| `Заказы/Статус-после-подтверждения-продавцом`, `Заказы/Обзор/Региональный-заказ-не-украинский`: на не українських площадках передоплата списується при підтвердженні продавцем | `Common/Library/Ecommerce/Hold/HoldPolicy.cs` (останній коміт `46f454f68f`, 05.10.2026): продовжений холд на ES / PT, `MaxHoldDays = 6`, ознака «відправлено» — `Departed` / `Delivered` / `Completed`. У CodeWiki не описано | № 122 — порівняння з Genei; кандидат у `qa-context/domain/payment.md` після підтвердження QA |
| `Genei/Габариты-одной-позиции`, `Объединение-посылок…`: дефолтна посилка 29 × 34 × 40 см, 10 кг; кошик відмовляє, якщо габаритів немає | **Звірено:** на master (`GeneiDeliveryManager`) і в гілці (`ShipmentDetailsManager`) коробка за замовчуванням 30 × 25 × 15 см, 3 кг, ланцюжок джерел даних (каталог → медіана → AI → типова деталь → коробка) | Регресом гілки не є. Для T13 очікуваний результат за `task-context.md` § 3.3 (№ 30) правильний |
| `Доступность-и-включение/*`: Seur не можна ввімкнути в налаштуваннях | Так само в гілці: увімкнення — списком ID у коді, без налаштування і прапорця | «Швидко відкрити ширше» не реалізовано (див. «Не знайдено в коді»); № 6 |

### Що з CodeWiki зачіпає зміну, але в задачі не описано

| Правило (нотатка) | Чому важливо для Seur | Перевірка / питання |
| --- | --- | --- |
| Вирахування вартості доставки з виплати продавцю — тільки для Genei (`Genei/Деньги-IVA-и-выплата-продавцу-при-Genei`; для Seur — «не выполняется») | **Звірено:** `ProfitPaymentManager.cs:229`, `:352`, `:487` — лише `DeliveryType.Genei`, у гілці файл не змінено. Доставку SEUR оплачує Avtopro (`Payer = ORD`, customer ABPWORLD) | № 123; Q-027 |
| Дії за статусом «Отправлен»: продавцю для «інших доставок» — тільки «Заказ доставлен»; покупцю — відмова через добу після крайньої дати відправки; Genei — свої правила (`Заказы/Действия-*-по-статусам`) | **Звірено:** `DepartedStrategy` у гілці не змінено, для Seur окремої гілки немає. Скасування сбору в SEUR з ТТН досяжне лише через відмову покупця після дедлайну | № 85, 88, 89, 120; Q-025, Q-026 |
| QA API: `api/v1/qa/orders` (`shift-date`, `set-ttn` — тільки FullAccess), `api/v1/qa/delivery-tracking-status` для тестових ТТН (`Заказы/Как-это-тестировать-QA-API`) | Дозволяє дійти до скасування після дедлайну без очікування | № 85, 120 |

## Пропущено

- Перейменування й форматування без зміни логіки: `OrderManager.cs` (скорочення `using` і просторів імен — більшість із 385 рядків), `OrderActionManager.cs`, `DeliveryPriceManager.cs` (перенесення рядків), `GeneiManager.cs`, 7 перейменованих моделей `Genei* → Delivery*`.
- `DependanceInjection.cs` (+147 / −?) — реєстрація Seur-сервісів; переглянуто лише рядок `SeurTrackingNumberHandler` (`:883`).
- Внутрішня реалізація `ShipmentDetailsManager` (989 рядків) порядково не звірялась із старим `GeneiDeliveryManager`. Порядок вибору даних описано в `task-context.md` § 3.3; регрес — через порівняння цін Genei з master.
- Unit-тести (`Tests/Library.Tests/Seur/*`, ~2600 рядків) — переглянуто лише назви й `SellerOrderActionResolverTests`.
- `Docs/ai-context/projects/Abp.Avtopro.Dal.Seur.md`, `.csproj`, `Program.cs`.
- Значення облікових даних SEUR у коді й конфігах не переносились.
