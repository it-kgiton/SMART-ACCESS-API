# Command: /deploy — Smart Access API

> Deploy aplikasi ke Railway (staging atau production).
> Usage: `/deploy [staging|production]`

---

## Usage

```
/deploy                  # Deploy ke staging (default)
/deploy staging          # Deploy ke staging
/deploy production       # Deploy ke production (ada konfirmasi)
/deploy --check          # Hanya cek status tanpa deploy
```

---

## Workflow Deploy

### Pre-Deploy Checklist

Sebelum deploy, agent akan otomatis:

1. **Cek tests** — jalankan `pytest` dan pastikan tidak ada failure
2. **Cek .env.example** — pastikan semua variable yang diperlukan terdokumentasi
3. **Cek requirements.txt** — verifikasi tidak ada dependency konfliktif
4. **Cek git status** — pastikan tidak ada uncommitted changes penting
5. **Cek Dockerfile** — validasi syntax dan completeness

### Deploy ke Staging

```bash
# 1. Run tests
pytest --cov=app --cov-fail-under=70 -q

# 2. Build & verify Docker image
docker build -t smart-access-api:staging .

# 3. Deploy ke Railway staging
railway up --environment staging --detach

# 4. Monitor logs (30 detik)
railway logs --environment staging --tail

# 5. Health check
curl -f https://smart-access-api-stg.up.railway.app/health
```

### Deploy ke Production

```bash
# WAJIB: konfirmasi manual sebelum lanjut
echo "⚠️  Deploy ke PRODUCTION. Pastikan sudah:"
echo "  1. Test passing di staging"
echo "  2. Database migration (jika ada) sudah dijalankan"
echo "  3. Approval dari lead developer"
read -p "Ketik 'yes' untuk lanjutkan: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deploy dibatalkan."
    exit 0
fi

# Deploy
railway up --environment production --detach

# Monitor
railway logs --environment production --tail

# Health check production
curl -f https://smart-access-api.up.railway.app/health
```

---

## Environment Variables

Pastikan semua ini di-set di Railway sebelum deploy:

```
DATABASE_URL              ← PostgreSQL connection string
SUPABASE_URL              ← Supabase project URL
SUPABASE_KEY              ← Supabase anon key
SUPABASE_SERVICE_ROLE_KEY ← Supabase service role key
JWT_SECRET_KEY            ← Random 256-bit hex (openssl rand -hex 32)
JWT_ALGORITHM             ← HS256
ACCESS_TOKEN_EXPIRE_MINUTES ← 30
DEVICE_TOKEN_EXPIRE_DAYS  ← 365
FACE_SIMILARITY_THRESHOLD ← 0.55
KGITON_API_URL            ← KGiTON API base URL
KGITON_API_KEY            ← KGiTON API key
FIRMWARE_STORAGE_BUCKET   ← firmware
BIOMETRIC_STORAGE_BUCKET  ← biometric-assets
```

---

## Post-Deploy Verification

```bash
# API health
curl https://smart-access-api.up.railway.app/health

# Docs aksesibel
curl -I https://smart-access-api.up.railway.app/docs

# Test endpoint auth (seharusnya 401 tanpa token)
curl -i https://smart-access-api.up.railway.app/api/v1/wallets/
```

Expected response `/health`:

```json
{
  "status": "ok",
  "database": "connected",
  "biometric_engine": "ready"
}
```

---

## Rollback

```bash
# Lihat deployment history
railway deployments list

# Rollback ke deployment sebelumnya
railway deployments rollback [deployment-id]
```

---

## Troubleshooting

| Masalah                        | Solusi                                              |
| ------------------------------ | --------------------------------------------------- |
| `biometric_engine` gagal load  | Cek apakah model buffalo_l terdownload di container |
| Database connection timeout    | Cek `DATABASE_URL` dan Railway PostgreSQL add-on    |
| 502 Bad Gateway                | Container crash — cek `railway logs --tail`         |
| InsightFace dependencies error | Pastikan Dockerfile include libgl1-mesa-glx         |
