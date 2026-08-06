# Credibil deployment

Permanent branches:

- `dev` deploys to `https://test.abeslab.by/credibil/dev/`
- `prod` deploys to `https://test.abeslab.by/credibil/`

Required GitHub Actions secrets:

- `FTP_SERVER`
- `FTP_PORT`
- `FTP_USERNAME`
- `FTP_PASSWORD`
- `FTP_PROD_DIR`
- `FTP_DEV_DIR`

Recommended flow:

1. Develop and commit to `dev`.
2. Verify the build at `/credibil/dev/`.
3. Open a pull request from `dev` to `prod`.
4. Merge only after successful checks.

The development build receives `robots.txt` with `Disallow: /` and `noindex,nofollow,noarchive` meta tags.
