# Credibil public landing

Адаптивный публичный B2B-лендинг, собранный по ТЗ и реальным скриншотам продукта Credibil.

## Состав

- `index.html` - семантическая разметка и румынская master-разметка для SEO.
- `styles.css` - локальная дизайн-система, адаптив, состояния фокуса и reduced motion.
- `app.js` - переключение RO/EN, mobile drawer, сохранение поискового запроса, аналитические события.
- `assets/` - SVG-логотипы, favicon, Open Graph и оптимизированные WebP-кропы реального продукта.

## Просмотр

Откройте `index.html` напрямую или запустите локальный сервер:

```bash
python3 -m http.server 8080
```

После этого откройте `http://localhost:8080`.

## Интеграция поиска

Форма сохраняет запрос в `sessionStorage`:

```js
sessionStorage.getItem("credibilSearchQuery")
```

И переходит на:

```text
/ru/login?returnTo=%2Fru%2Fsearch&query=<query>
```

В production auth-flow должен перенести `query` в `/ru/search` после успешной авторизации.

## Аналитика

События отправляются в `window.dataLayer`:

- `public_search_submit`
- `cta_click`
- `language_select`

## Перед релизом

1. Подключить Manrope Variable локально как WOFF2.
2. Подтвердить домен и заменить относительные `canonical` и `hreflang`.
3. Подтвердить юридическое наименование, контакты, privacy и terms URL.
4. Подтвердить перечень источников, периодичность обновления, тарифы и API до добавления соответствующих утверждений.
5. Подключить реальный публичный autocomplete только после продуктового разрешения.
6. Добавить Organization и SoftwareApplication schema только после подтверждения юридических данных.
7. Выполнить редактуру румынской версии носителем языка.

## Предлагаемое разбиение для React/Vite

- `SiteHeader`
- `HeroSearch`
- `MoldovaPositioning`
- `CapabilityGrid`
- `ProductDirections`
- `ProductGallery`
- `CompanyConnections`
- `RiskReportMatrix`
- `MonitoringSection`
- `MoldacSection`
- `HowItWorks`
- `FinalCta`
- `SiteFooter`

Design tokens из `:root` можно перенести в `src/styles/tokens.css` без изменений.
