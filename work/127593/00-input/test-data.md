# Тестові дані: 127593

| Поле | Значення | Джерело |
| --- | --- | --- |
| Код AvtoPro | `/Users/oleksandrpc/Desktop/ABP/avto/AvtoPro` (тільки читання), гілка `delivery/seller/feat-seur-delivery` | [зі слів QA, 2026-11-04] |
| Продавець Seur | 1082119 — змінні `TEST_SELLER_SEUR_*` у `.env` | `.env.example` |
| Співробітник BPanel | змінні `TEST_BPANEL_QA_*` у `.env` | `.env.example` |
| Деталі й індекси | T01…T14, індекси — `task-context.md` § 5 і `qa-context/test-data.md` | [задача 127593] |
| Стенд | `es.seller1.vus.us` (avtopro.es), `pt.seller1.vus.us` (avtopro.pt) з гілкою `feat-seur-delivery`; доступ — через VPN, пароля стенду немає (`TEST_ENV_PASSWORD` порожній). До 2026-11-05 ~14:00 — seller3 (перезібрано іншою збіркою) | [зі слів QA, 2026-11-05, оновлено 2026-11-05] |
| Регіональна версія | es (основна), pt | [зі слів QA, 2026-11-05] |
| Покупець | `TEST_BUYER_ES_*` (1075831) — з нього можна оформлювати замовлення, зокрема в Рекалві і в продавця Genei | [зі слів QA, 2026-11-05] |
| Продавець Genei | 1049862 — змінні `TEST_SELLER_GENEI_*` у `.env`; у видачі «Vendedor: truepaymentvz»; деталь Febi 2569 (`/repuesto-2569-FEBI-700/`) | [зі слів QA, 2026-11-05] |
| Рекалві | 1369756, у видачі «Vendedor: RECAMBIOS AUTO»; деталь Miraglio 301006C (`/repuesto-301006C-MIRAGLIO-564/`) — пропозиція зі складом «Entrega a partir de: Hoy, Vigo» | [зі слів QA, 2026-11-05] |
| Кошик `TEST_BUYER_ES` | можна очищати в кейсах | [зі слів QA, 2026-11-05] |
| Cookie | `showTestUsers` = `true` | [зі слів QA, 2026-11-05] |
| 1082119 у видачі | «Vendedor: SAA»; прайс завантажено, склад «Seur Test» у розділі «Mis almacenes» | [зі слів QA, 2026-11-05] |
