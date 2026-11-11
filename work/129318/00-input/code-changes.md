# Зміни в коді: 129318 — ліміт запитів за держномером і підтвердження телефону

> Код показує, ЩО перевіряти. Очікуваний результат — тільки з вимог.
> Шляхи — від кореня репозиторію AvtoPro; `…/sources/` = `AvtoproSite/Abp.Avtopro.SiteCore/Client/js/sources/`.

| | |
| --- | --- |
| Репозиторій | `/Users/oleksandrpc/Desktop/ABP/avto/AvtoPro` |
| Гілка | `delivery/seller/es-plate-phone-confirm-limit` · HEAD `bdf29f628a` |
| База | `origin/master` (`df5d2d613a`) · merge-base `b3d6f420ff` (2026-11-02); гілка відстає від master на 240 комітів |
| Обсяг | 11 файлів · +168 / −13 рядків · 2 коміти |
| Коміти | `23ec8542d8` бекенд, 2026-11-02: «підтвердження телефону і ліміт 3 на добу для пошуку по держномеру ES **#129794**»; `bdf29f628a` фронт, 2026-11-04: «добавлен модал подтверждения телефона при ограничении госномера» |
| Дата аналізу | 2026-11-11 |

## Коротко

Змінено тільки **іспанську гілку** пошуку за держномером (Inforauto, `countryISO=es`) — на сайті це avtopro.es (30). Перед запитом до Inforauto бекенд тепер вимагає підтверджений телефон (`403 PhoneNotConfirmed`), ліміт знижено з 5 до 3, вікно лічильника збільшено з 1 до 24 годин. На фронті при `403` відкривається модалка введення / підтвердження телефону, після підтвердження пошук повторюється автоматично. Спільний `SearchEngine` змінено, тож нова поведінка зʼявляється всюди, де є поле держномера на ES — зокрема в місцях, яких немає в Regression List (кошик, ТО, індикативна ціна). Головні ризики: модалка підтверджує телефон через інші дані, ніж перевіряє пошук; тексти «спробуйте через годину» лишились; гілка конфліктує з master у тих самих файлах; коміт посилається на #129794, а не на 129318.

## Що змінено

| Група | Файли | Що змінилось |
| --- | --- | --- |
| Бекенд / API | `Controllers/Api/SearchEngineController.cs`, `Common/Library/Search/BLL/SearchByInfoautorManager.cs`, `Common/Library/Search/BLL/PhoneNotConfirmedException.cs` (новий) | перевірка підтвердженого телефону; ліміт 5 → 3; TTL 1 год → 24 год; новий код відповіді `403` |
| Фронт | `…/search/model/SearchEngine.js`, `…/search/model/SearchEngineError.ts`, `…/search/components/PhoneConfirmationModal.jsx` (новий), `…/search/Search.jsx`, `…/search/components/SearchError.jsx`, `…/components/car-search/CarSearch.tsx`, `…/main/containers/EditPhoneModalContainer.jsx`, `…/components/phone-confirmation-modals/components/PhoneApproveCode.jsx` | модалка телефону при `403`, повтор пошуку після підтвердження, скидання держномера при закритті модалки, приховування помилки під модалкою |
| Переклади | — | **не змінювались**; модалка використовує наявні ключі |
| Міграції БД | — | немає |
| Конфіг / прапорці | — | немає; нового feature flag немає |
| Фонові задачі | — | немає |
| Тести | — | немає |

## Факти для тестування

### Ендпоінти

| Метод і маршрут | Що нового | Валідації / коди помилок | Права | Код |
| --- | --- | --- | --- | --- |
| `PUT /api/v1/search/licensecarnumber?licenseCarNumber=&countryISO=es` | новий `403` з тілом `ApiResponse("Phone is not confirmed", "PhoneNotConfirmed")` | формат ES `^(?:\d{4}[A-Z]{3}\|[A-Z]\d{4}[A-Z]{2})$` (інакше виняток → 500 [ПРИПУЩЕННЯ]); гість → `401`; немає підтвердженого телефону → `403`; ліміт → `429` без тіла | без авторизації; без `[EnableAntiParsing]` | `SearchEngineController.cs:229`–`284` |
| `PUT …/licensecarnumber?countryISO=UA` (і будь-яка країна ≠ `es`) | без змін — реєстр МВД, без ліміту й перевірки телефону | — | — | `SearchEngineController.cs:290`–`293` |
| `POST /api/v1/account/phone/confirmation` | не змінено; викликається з нової модалки — запит коду | гість → `403`; `+38…` → SMS; інший мобільний → дзвінок з голосовим кодом; стаціонарний ES / PT → IVR без коду | авторизований | `Login.js:112`; `AccountController.cs:474` |
| `POST /api/v1/account/phone` | не змінено; підтвердження коду з модалки | неправильний код → `409`; 5 невдалих спроб → `429` | авторизований | `Login.js:122`; `AccountController.cs:533` |

### Валідації і ліміти

| Поле / параметр | Правило в коді | Значення | Код |
| --- | --- | --- | --- |
| Хто проходить до Inforauto | номера немає в локальному кеші (`GetInfoCarByLicenseCarNumber`) → далі перевірки; номер **є** в кеші → результат одразу, **без** перевірок і ліміту, будь-якому користувачу, і гостю | — | `SearchByInfoautorManager.cs:57`–`59` |
| Гість | `userId == 75` → `UnauthorizedAccessException` → `401` (без змін) | — | `SearchByInfoautorManager.cs:61`, `103` |
| Підтверджений телефон | `_profileManager.GetPhones(userId).Any(x => x.IsVerification)`; немає → `403`. Перевіряється **до** ліміту, лічильник не збільшується | хоча б один підтверджений телефон у списку `api_getAllUserPhones` | `SearchByInfoautorManager.cs:63`–`66` |
| Ліміт на користувача | `inforcar_ratelimit_user:{userId}` < 3 | **3** (було 5) | `SearchByInfoautorManager.cs:68`–`74` |
| Ліміт на IP | `inforcar_ratelimit_ip:{IP}` < 3; обидві умови разом | **3** (було 5) | там само |
| Вікно ліміту | TTL ключа в Redis = 24 год, **перезаписується при кожному врахованому запиті** → ліміт скидається через 24 год після **останнього** врахованого запиту, а не о півночі; часового поясу немає | **24 год** (було 1 год) | `SearchByInfoautorManager.cs:79`–`80` |
| Що рахується | лічильник збільшується **до** запиту в Inforauto → «номер не знайдено» теж витрачає спробу; запити понад ліміт TTL не продовжують | — | `SearchByInfoautorManager.cs:76`–`99` |
| IP клієнта | перше значення `X-Forwarded-For`, інакше `RemoteIpAddress` | — | `SearchEngineController.cs:249`–`266` |
| Перевищення | `InvalidOperationException` → `429` без тіла | — | `SearchByInfoautorManager.cs:98`; `SearchEngineController.cs:276`–`279` |

### Тексти і переклади

Нових ключів немає. Що бачить користувач (ключі наявні, `Abp.Avtopro.Resources/Site/…`):

| Ситуація | Ключ | es | ua (uk) | Код |
| --- | --- | --- | --- | --- |
| Гість, `401` (поле в банері / основний пошук) | `Search.SearchRegnumRequestsLimitForGuest` | «Se ha superado el límite de consultas por matrículas. Inicie sesión para realizar más consultas.» | «Перевищено ліміт запитів за номерними знаками. Увійдіть, щоб виконувати більше запитів.» | `CarSearch.tsx:146`–`152`; `SearchError.jsx:88`–`92` |
| Ліміт, `429`, банер `CarSearch` | `Search.SearchRegnumRequestsExceeded` | «… Intente nuevamente **dentro de una hora**.» | «-» (заглушка; так само pt, pl, en) | `CarSearch.tsx:23`–`27`, `155`–`160` |
| Ліміт, `429`, основний пошук | `Search.SearchErrorExceededLimitNumberQueries` | «Se ha superado el límite de consultas por número de matrícula. Intente nuevamente **dentro de una hora**.» | «… спробуйте ще раз **через годину**.» | `SearchError.jsx:82`–`87` |
| Немає підтвердженого телефону, `403` | — (текст помилки не показується; відкривається модалка) | — | — | `CarSearch.tsx:137`–`140`; `SearchError.jsx:72`–`78` |
| Модалка, крок 1 (номера в профілі немає) | `AccountSettings.AccountSettingsEditingPhoneNumber`, `AccountSettingsSAVE`, `AccountSettingsEnterPhoneNumber`; `Profiles.ManagerFormModalRulePhoneBannedCountry` | «Introduce tu número de teléfono», «Continuar» / «Cancelar», «Marque el número de teléfono», «No atendemos números de este país» | | `EditPhoneModalContainer.jsx:13`–`29`, `113`–`117` |
| Модалка, крок 2 (номер є → одразу тут) | `Profiles.PhoneApproveConfirmModalCaption`, `…CodeModalSubCaption` / `…ByCallSubCaption`, `…PasscodeInputPlaceholder`, `…SendCodeAgainLink`, `ModalButtonSend` | «Confirmación del teléfono»; «…ingrese el código recibido en el SMS» / «…comunicado durante la llamada»; «Ingrese el código recibido»; «Enviar el código nuevamente»; «ENVIAR» | | `PhoneConfirmationModal.jsx:13`–`22` |
| Помилки бекенду в модалці | `LoginChangingResource` | «Codigo erroneo»; «Contar intentos fallidos terminados»; «Se usa el teléfono» | | `AvtoproSite/Abp.Avtopro.WebLibrary/LocalizationResources/LoginChange/LoginChangingResource.es.resx` |

- Повторне надсилання коду — таймер 60 с на фронті (`PhoneApproveCode.jsx:15`); на бекенді ліміту надсилання немає (закоментовано, `PhoneChangingFacade.cs:69`–`87`).
- Екран успіху пропускається (`skipConfirmationSuccessScreen`) — після підтвердження модалка закривається і пошук повторюється.

### Площадки, ролі, прапорці

| Що | Умова в коді | Де діє | Код |
| --- | --- | --- | --- |
| Площадки (бекенд) | гілка за **параметром** `countryISO == "es"`, а не за площадкою | будь-яка площадка, якщо в запиті `countryISO=es` (напряму через API) | `SearchEngineController.cs:242` |
| Площадки (фронт) | поле держномера: `IsRegnumSearchAvailable = (1 \|\| 22 \|\| 30) && !IsСlientSiteAvailable`; країна — перша з `['UA','ES']` у країнах площадки | ES-гілка на сайті — тільки **avtopro.es (30)**; 1 і 22 — гілка UA, без змін; сайти продавців — поля немає | `FeatureFlags.cs:207`; `createGlobalsContext.ts:152`–`157` |
| Ролі | гість (`75`) — `401`; **усі** авторизовані (покупець, продавець, СТО) — однаково: телефон + 3 / 24 год. Розподілу «зареєстрований / верифікований» немає | — | `SearchByInfoautorManager.cs:61`–`74` |
| Тестові користувачі | `StaticUserHelper.TestUsers` не перевіряється; sandbox Inforauto немає → на стенді кожен новий номер — бойовий запит | — | CodeWiki § Поля-ответа-Inforauto-и-отсутствие-sandbox |
| Feature flag | немає — змінити поведінку без релізу не можна | — | — |

### Статуси, фонові задачі, інтеграції, міграції

| Що | Зміна | Наслідок для тесту | Код |
| --- | --- | --- | --- |
| Inforauto | частота запитів знижена; запит тільки після перевірки телефону | для кожної спроби потрібні **нові** номери, яких немає в кеші; кожен — бойовий запит | `SearchByInfoautorManager.cs:84` |
| Redis | ключі `inforcar_ratelimit_user:{id}`, `inforcar_ratelimit_ip:{IP}` (з префіксом `Cache_`) | скинути лічильник на стенді можна тільки видаленням ключа в Redis або чеканням 24 год — спитати розробника | `CacheHelper.cs:196`–`205` |
| Лог | `inforcar` / `information` / `1681` з поточними лічильниками; помилки — `LicenseCarNumberQuery` / `85299` | лічильники можна дивитися в AppLog | `SearchByInfoautorManager.cs:82`; `SearchEngineController.cs:298` |

### Поведінка фронту

| Що | Як у коді | Код |
| --- | --- | --- |
| Відкриття модалки | після відповіді `403 PhoneNotConfirmed` у `SearchEngine.putRegnum` — у **будь-якому** місці, що шукає через `SearchEngine` | `SearchEngine.js:188`–`194` |
| Перший крок модалки | номер у профілі є (`globals.user.phoneNumber`) → одразу крок підтвердження (з поверненням до введення іншого номера); немає → форма введення номера | `PhoneConfirmationModal.jsx:13`–`22`; `EditPhoneModalContainer.jsx:46`–`47` |
| Успіх | `putRegnum` повторюється з тим самим номером | `SearchEngine.js:203`–`207` |
| Закриття / «Cancelar» | подія `phoneConfirmation.cancel` → держномер скидається, але **тільки** в основному пошуку (`Search.jsx`); в інших місцях підписника немає | `SearchEngine.js:209`–`213`; `Search.jsx:214`–`219` |
| Неправильний код | помилка показується в модалці, модалка лишається відкритою | `EditPhoneModalContainer.jsx:104`–`108`; `PhoneApproveCode.jsx:95`–`98` |
| Повторний виклик | поки модалка відкрита, друга не відкривається (спільний Promise) | `PhoneConfirmationModal.jsx:38`–`40` |
| Помилка під модалкою | приховано в `CarSearch` і `EmptyResultError`; в інших компонентах (кошик, гараж `VehicleForm`, індикативна ціна) — не змінено, що там видно при `403`, — перевірити | `CarSearch.tsx:137`; `SearchError.jsx:72` |
| Контекст пошуку | при `403` контекст не змінюється (на відміну від `401` / `429`) | `SearchEngine.js:388`–`401` |

## Вплив і регрес

Усі місця з полем держномера, де країна береться з `globals.regnumSearchCountryIso` (на ES → `ES`):

| Модуль / місце | Чому зачеплено | У Regression List | Автотести | Код |
| --- | --- | --- | --- | --- |
| Основний пошук (шапка, сторінка пошуку) | `Search.jsx` / `SearchView.jsx` → `putRegnum`; єдине місце зі скиданням номера при закритті модалки | «поиск» | невідомо | `…/search/Search.jsx`, `…/search/views/SearchView.jsx:596`, `1196`; `…/common/search.js:683` |
| Сторінки `/vin-code/`, `/vin-decoder/`, `/check-auto/` (банер `CarSearchBanner` → `CarSearch`) | `CarSearch` змінено | «Запчасти по вин-коду» | невідомо | `…/vin-code-search/App.tsx:377` |
| Carfax `/carfax-report/` | той самий банер; але сторінка є тільки на 1 і 22 (гілка UA) | «carfax» — на ES сторінки немає, на UA зміна не діє | невідомо | `…/carfax-reports/components/CarfaxSearch.tsx` |
| Гараж: банер додавання і форма авто | `CarSearchBanner`; `VehicleForm` → `vehicle-select` → `RegnumVinSearch` | «гараж» | невідомо | `…/garage/containers/VehicleAddBanner.tsx:267`; `…/garage/components/VehicleForm.tsx:380` |
| Замовлення: вибір авто в замовленні | `components/order/SearchVinCode.tsx` → `RegnumVinSearch` | «заказы» | невідомо | `…/orders/components/VehicleSetupMode/VehicleInfo/index.tsx`; `…/components/order/SearchVinCode.tsx:223` |
| **Кошик / оформлення**: модалка VIN і форма адреси | той самий `SearchVinCode` | **немає** | невідомо | `…/cart/components/SearchVinCodeModal.tsx`; `…/cart/components/AddressForm.jsx` |
| **Запчастини для ТО** | `CarSearchBanner` | **немає** | невідомо | `…/parts-for-maintenance/PartsForMaintenanceVinSearch.tsx:325` |
| **Індикативна ціна** | `RegnumVinCatalog` → `RegnumVinSearch` | **немає** | невідомо | `…/indicative-price/containers/PricePageContainer.tsx:82`; `…/indicative-price/containers/SearchFormContainer.tsx:326` |
| Модалка телефону в налаштуваннях акаунта / кошику | змінено `EditPhoneModalContainer` (новий проп, помилка коду тепер прокидається далі) і `PhoneApproveCode` | **немає** | невідомо | `…/main/containers/EditPhoneModalContainer.jsx`; `…/components/phone-confirmation-modals/components/PhoneApproveCode.jsx` |
| Інші форми підтвердження телефону | спільний `PhoneApproveCode.jsx` змінено (помилка коду тепер перехоплюється): налаштування покупця (`_buyer`, `_buyer-es`) і продавця, «стати продавцем», PayCredit (`ConfirmPhoneForm`), рахунок замовлення (`PhoneConfirmationForm`), відгук на замовлення, онлайн-магазин, підключення СТО | **немає** | невідомо | `…/components/phone-confirmation-modals/index.jsx:97` (доповнено 2026-11-11) |
| UA-площадки (1, 22) — пошук за держномером | спільні фронтові компоненти змінено, бекенд UA — ні; регрес: поведінка без змін | неявно | невідомо | — |

URL сторінок ТО та індикативної ціни на ES не встановлено [ПРИПУЩЕННЯ: уточнити в QA]. `vehicle-select` у відгуках про виробника, СТО і авторозбірках поле держномера не показує (не передають `regnumCountryIso`) — не зачеплено.

## Документація ↔ код

| Тема | CodeWiki (master, 2026-08-17) | Код гілки | Висновок |
| --- | --- | --- | --- |
| Ліміт держномера ES | 5 на годину на користувача і на IP | 3 на 24 год | зміна гілки; CodeWiki оновити після релізу |
| «5 запросов в день» із задачі | у master — **на годину** (TTL 1 год) | — | формулювання задачі не відповідає master → питання |
| Гість | `userId == 75` → `401` | без змін | збігається |
| Підтвердження телефону для пошуку | немає | `GetPhones(userId).Any(IsVerification)` з `api_getAllUserPhones` | нове |
| Де пишеться підтвердження | особисті дані: `POST /api/v1/account/phone/confirmation` → `POST /api/v1/account/phone` | модалка → ті самі ендпоінти → процедура `webrole_account_tel_confirm` (`AccountPhoneChangingRepository.cs:13`–`28`); у контактних профілях — інша, `p_profile_confirm_phone` | **ризик:** чи бачить `api_getAllUserPhones` телефон, підтверджений через `webrole_account_tel_confirm`, з коду не видно (SQL у репозиторії немає). Якщо ні — після підтвердження повтор знову дасть `403` і модалка відкриється знову |
| Ознака підтвердженого телефону в інших лімітах | VIN-ліміт: «Verified» = тип продавця / СТО; email — для покупця | VIN-ліміт читає головний телефон `p_seller_get_main_mobile` (`RateLimitManager.cs:97`–`104`); держномер — `api_getAllUserPhones` | три різні джерела «підтвердженості» → питання |
| Канал коду для ES | не `+38` → дзвінок з голосовим кодом; стаціонарний ES / PT → IVR | без змін | для іспанського користувача — **дзвінок, не SMS**; підпис модалки — варіант «ByCall» |
| Антипарсинг | `/api/v1/` не перевіряється без `[EnableAntiParsing]` | у `licensecarnumber` атрибута немає | захист — тільки ліміт Inforauto |
| Sandbox Inforauto | не знайдено | без змін | тестові запити — бойові |

## Звірка із задачею

### Неописані зміни

| Що в коді | Код | Що робити |
| --- | --- | --- |
| Вікно ліміту 1 год → 24 год, ковзне від останнього запиту | `SearchByInfoautorManager.cs:79`–`80` | питання: «день» = календарна доба чи 24 год? |
| Ліміт на IP теж 3 (спільний IP офісу / мобільного оператора вичерпує ліміт для всіх) | `SearchByInfoautorManager.cs:71`–`74` | питання аналітику |
| Перевірка телефону діє для всіх авторизованих, зокрема продавців і СТО | `SearchByInfoautorManager.cs:63` | питання: чи так задумано |
| Повтор пошуку після підтвердження; скидання номера при закритті (тільки основний пошук) | `SearchEngine.js:203`–`213` | перевірити в кожному місці регресу |
| Зміни модалки телефону зачіпають налаштування акаунта | `EditPhoneModalContainer.jsx`, `PhoneApproveCode.jsx` | регрес: підтвердження телефону в налаштуваннях і кошику |
| Номер з кешу повертається будь-кому без ліміту | `SearchByInfoautorManager.cs:57` | не зміна гілки, але впливає на тест-дизайн (потрібні нові номери) і на ефективність захисту |

### Не знайдено в коді

| Вимога (цитата) | Де шукали | Примітка |
| --- | --- | --- |
| Оновлені тексти помилки ліміту (зараз «через годину» / «dentro de una hora») | `Abp.Avtopro.Resources/Site/Search/*.resx` — змін у гілці немає | вимога прямо не каже; при вікні 24 год текст вводить в оману → питання |
| Змін для UA (1, 22) | `SearchByMvdManager` — без змін | задача не називає площадку; гілка й коміт — тільки ES |

### Розбіжності

| Вимога (цитата) | Що в коді | Код | Пропозиція |
| --- | --- | --- | --- |
| «не давать просто аккаунту 5 запросов в день» | у master 5 запитів **на годину** | master `SearchByInfoautorManager.cs` (TTL 1 год) | Q: що мається на увазі під поточним станом |
| «давать 3 в день» | 3 на 24 год від останнього врахованого запиту, не календарна доба | `SearchByInfoautorManager.cs:74`–`80` | Q: визначення «дня», час скидання, часовий пояс |
| «просить верификацию телефона и давать 3 в день» | без підтвердження — 0 запитів (`403` + модалка); з підтвердженням — 3 | `SearchByInfoautorManager.cs:63`–`74` | Q: трактування (а) / (б) |
| Задача 129318 | коміт бекенду посилається на **#129794** | `23ec8542d8` | Q: чи та сама задача / чи є повʼязана |

## Ризики для тест-дизайну

- **Гілка конфліктує з master**: у master після merge-base змінено `SearchByInfoautorManager.cs` (метод для PiezaExacta, `0237318f23`) і `SearchEngineController.cs`. Тестувати збірку **після** злиття з master; спитати розробника.
- Немає sandbox Inforauto — кожен новий номер на стенді йде в бойовий API. Обмежити кількість, узгодити з розробником.
- Скидання лічильників — Redis або 24 год. Без доступу до Redis кожен акаунт / IP дає одну спробу на добу → потрібно кілька акаунтів і IP (або `debug_ip`, якщо він впливає на `X-Forwarded-For` — [ПРИПУЩЕННЯ], перевірити).
- Для перевірки «без підтвердженого телефону» потрібен акаунт без підтвердженого телефону; підтвердження змінює акаунт назавжди (видалення телефону — `DELETE /api/v1/account/phone`).
- `429` від ліміту і `429` від антипарсингу не розрізнити — агенту за правилами `PROJECT.md` § 7 при `429` треба зупинятися; для цієї задачі `429` — очікуваний результат, це треба явно дозволити в кейсах.

## Пропущено

- Зміни master після merge-base, які не стосуються пошуку за держномером (240 комітів).
- SQL процедур `api_getAllUserPhones`, `webrole_account_tel_confirm`, `p_inforautos_get_by_licenseplate` — у репозиторії немає.
- Перевірка злиття: `git merge-tree --write-tree` показав конфлікти (команда записала тимчасові обʼєкти в `.git/objects` AvtoPro — див. примітку в `pipeline.md`).
