param(
    [string]$ArchivePath = 'D:\GoogleDrive\Projects\Credibil\FINAL_OUTPUT\FINAL_OUTPUT.zip',
    [string]$RepositoryUrl = 'https://github.com/Abestreid/Credibil.git',
    [string]$Branch = 'main'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-Command {
    param([Parameter(Mandatory)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Команда '$Name' не найдена. Установи Git for Windows и повтори запуск."
    }
}

Assert-Command -Name 'git'

if (-not (Test-Path -LiteralPath $ArchivePath -PathType Leaf)) {
    throw "Архив не найден: $ArchivePath"
}

$workRoot = Join-Path $env:TEMP ("credibil-import-" + [guid]::NewGuid().ToString('N'))
$repoPath = Join-Path $workRoot 'repo'
$stagePath = Join-Path $workRoot 'stage'

New-Item -ItemType Directory -Path $workRoot, $stagePath -Force | Out-Null

try {
    Write-Host "1/7 Клонирование $RepositoryUrl"
    & git clone --branch $Branch --single-branch $RepositoryUrl $repoPath
    if ($LASTEXITCODE -ne 0) {
        throw 'Не удалось клонировать репозиторий. Проверь авторизацию GitHub в Git Credential Manager.'
    }

    Write-Host "2/7 Распаковка $ArchivePath"
    Expand-Archive -LiteralPath $ArchivePath -DestinationPath $stagePath -Force

    Write-Host '3/7 Удаление вложенных дубликатов'
    $duplicatePaths = @(
        (Join-Path $stagePath 'credibil-scroll-story\credibil-scroll-story'),
        (Join-Path $stagePath 'credibil-wow-site\credibil-wow-site')
    )

    foreach ($duplicatePath in $duplicatePaths) {
        if (Test-Path -LiteralPath $duplicatePath) {
            Remove-Item -LiteralPath $duplicatePath -Recurse -Force
        }
    }

    Write-Host '4/7 Нормализация пятого проекта'
    $boltOuter = Join-Path $stagePath 'project-bolt-sb1-3bvarghr'
    $boltSource = Join-Path $boltOuter 'project'
    $boltDestination = Join-Path $stagePath 'credibil-bolt-vite'

    if (Test-Path -LiteralPath $boltSource) {
        if (Test-Path -LiteralPath $boltDestination) {
            Remove-Item -LiteralPath $boltDestination -Recurse -Force
        }

        Move-Item -LiteralPath $boltSource -Destination $boltDestination
        Remove-Item -LiteralPath $boltOuter -Recurse -Force
    }

    Write-Host '5/7 Подготовка корневой страницы и README'

    $readme = @'
# Credibil landing concepts

Репозиторий содержит пять самостоятельных вариантов лендинга Credibil и один отдельный пример секции.

## Структура

- `credibil-public-landing` - статический HTML/CSS/JS лендинг.
- `credibil-scroll-story` - статический лендинг со scroll-story подачей.
- `credibil-site-v3` - проект React/Next/Vinext.
- `credibil-wow-site` - статический визуальный концепт.
- `credibil-bolt-vite` - проект React + Vite из Bolt.
- `credibil-section` - отдельный пример секции.

Откройте корневой `index.html`, чтобы перейти к каждому варианту. Проекты со сборкой запускаются командами из соответствующих `package.json` и README.
'@

    $index = @'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Credibil - варианты лендинга</title>
  <meta name="description" content="Галерея пяти вариантов лендинга Credibil и отдельного примера секции.">
  <style>
    :root{color-scheme:dark;--bg:#07120f;--panel:#0e1d18;--line:#28473d;--text:#f4f7f5;--muted:#a9bbb4;--accent:#7ef0b8}
    *{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at 20% 0,#16382d 0,transparent 35%),var(--bg);color:var(--text)}
    main{width:min(1180px,calc(100% - 40px));margin:auto;padding:72px 0}h1{font-size:clamp(40px,7vw,84px);line-height:.95;margin:0 0 22px;letter-spacing:-.055em}.lead{max-width:760px;color:var(--muted);font-size:20px;line-height:1.6;margin:0 0 48px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}.card{display:flex;min-height:230px;flex-direction:column;padding:26px;border:1px solid var(--line);border-radius:24px;background:linear-gradient(145deg,rgba(20,43,35,.92),rgba(9,22,18,.96));text-decoration:none;color:inherit;transition:.2s transform,.2s border-color}.card:hover{transform:translateY(-4px);border-color:var(--accent)}
    .n{font-size:13px;color:var(--accent);letter-spacing:.12em;text-transform:uppercase}.card h2{font-size:27px;margin:34px 0 12px;letter-spacing:-.03em}.card p{color:var(--muted);line-height:1.55;margin:0 0 22px}.open{margin-top:auto;color:var(--accent);font-weight:700}.note{margin-top:34px;color:var(--muted);font-size:14px;line-height:1.6}
  </style>
</head>
<body><main><div class="n">Credibil design archive</div><h1>5 вариантов лендинга<br>и отдельная секция</h1><p class="lead">Единая стартовая страница для просмотра и дальнейшей разработки всех концептов Credibil.</p><section class="grid">
<a class="card" href="credibil-public-landing/index.html"><span class="n">Вариант 01</span><h2>Public Landing</h2><p>Статический HTML/CSS/JS лендинг с готовыми ассетами.</p><span class="open">Открыть вариант</span></a>
<a class="card" href="credibil-scroll-story/index.html"><span class="n">Вариант 02</span><h2>Scroll Story</h2><p>Концепт с последовательной визуальной историей при прокрутке.</p><span class="open">Открыть вариант</span></a>
<a class="card" href="credibil-site-v3/README.md"><span class="n">Вариант 03</span><h2>Site V3</h2><p>Исходный проект React/Next/Vinext. Требует локального запуска и сборки.</p><span class="open">Открыть README</span></a>
<a class="card" href="credibil-wow-site/index.html"><span class="n">Вариант 04</span><h2>WOW Site</h2><p>Статический визуальный концепт с расширенным набором изображений.</p><span class="open">Открыть вариант</span></a>
<a class="card" href="credibil-bolt-vite/dist/index.html"><span class="n">Вариант 05</span><h2>Bolt / Vite</h2><p>React + Vite проект. Ссылка ведет на готовую сборку из архива.</p><span class="open">Открыть сборку</span></a>
<a class="card" href="credibil-section/index.html"><span class="n">Отдельный пример</span><h2>Credibil Section</h2><p>Самостоятельная секция для переноса или интеграции в выбранный лендинг.</p><span class="open">Открыть секцию</span></a>
</section><p class="note">Статические варианты открываются напрямую. Проекты Site V3 и Bolt/Vite сохранены полностью с исходниками и конфигурацией.</p></main></body>
</html>
'@

    Set-Content -LiteralPath (Join-Path $stagePath 'README.md') -Value $readme -Encoding utf8
    Set-Content -LiteralPath (Join-Path $stagePath 'index.html') -Value $index -Encoding utf8

    Write-Host '6/7 Копирование файлов и создание коммита'
    Get-ChildItem -LiteralPath $repoPath -Force |
        Where-Object { $_.Name -ne '.git' } |
        Remove-Item -Recurse -Force

    Get-ChildItem -LiteralPath $stagePath -Force |
        Copy-Item -Destination $repoPath -Recurse -Force

    & git -C $repoPath config user.name 2>$null
    if ($LASTEXITCODE -ne 0) {
        & git -C $repoPath config user.name 'Abestreid'
    }

    & git -C $repoPath config user.email 2>$null
    if ($LASTEXITCODE -ne 0) {
        & git -C $repoPath config user.email '121676892+Abestreid@users.noreply.github.com'
    }

    & git -C $repoPath add --all
    & git -C $repoPath diff --cached --quiet

    if ($LASTEXITCODE -eq 0) {
        Write-Host 'Изменений для загрузки нет.'
        exit 0
    }

    & git -C $repoPath commit -m 'Add five Credibil landing variants and section example'
    if ($LASTEXITCODE -ne 0) {
        throw 'Не удалось создать Git-коммит.'
    }

    Write-Host '7/7 Отправка в GitHub'
    & git -C $repoPath push origin "HEAD:$Branch"
    if ($LASTEXITCODE -ne 0) {
        throw 'Не удалось отправить изменения. Проверь авторизацию GitHub в Git Credential Manager.'
    }

    Write-Host 'Готово: архив распакован и загружен в Abestreid/Credibil.' -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $workRoot) {
        Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
