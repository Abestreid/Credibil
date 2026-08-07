FROM python:3.12-slim AS base

WORKDIR /app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl gnupg \
    # Playwright browser dependencies
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libdbus-1-3 libxkbcommon0 libatspi2.0-0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2t64 \
    # Xvfb for headed browser mode (bypasses Cloudflare)
    xvfb xauth \
    # System Chromium (not Playwright's bundled one) for undetected browsing
    chromium \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ ./

RUN pip install --no-cache-dir uv && uv pip install --system -e ".[dev]"

# Install Playwright Chromium browser to shared location
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/lib/playwright
RUN mkdir -p /usr/lib/playwright && playwright install chromium

EXPOSE 8000

CMD ["uvicorn", "credibil.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS production

RUN useradd --create-home --shell /bin/bash credibil
WORKDIR /app/backend
RUN chown -R credibil:credibil /app
USER credibil

CMD ["uvicorn", "credibil.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
