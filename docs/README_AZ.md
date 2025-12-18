# SearchNewsRAG - Süni İntellektlə Xəbər Axtarışı və Analitika

[![Production](https://img.shields.io/badge/production-news.aitools.az-blue)](https://news.aitools.az)
[![GitHub](https://img.shields.io/badge/github-SearchNewsRAG-black)](https://github.com/ImranRahimov1995/SearchNewsRAG)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.124-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://react.dev/)

**Azərbaycan xəbərləri üçün RAG (Retrieval-Augmented Generation) texnologiyası, vektor embeddingləri, LLM metadata analizi və interaktiv vizualizasiya ilə korporativ semantik axtarış və analitika platforması.**

---

## 🎯 Layihə Haqqında

SearchNewsRAG xəbər məlumatları ilə istifadəçi qarşılıqlı əlaqəsini dəyişdirən tam-stack tətbiqdir. O özündə birləşdirir:
- **Avtomatik məlumat toplama** Telegram kanallarından
- **Süni intellekt analizi** OpenAI GPT modelləri ilə
- **Vektor semantik axtarış** ChromaDB vasitəsilə
- **İnteraktiv vizualizasiya** xəbərlər kainatı qrafiki şəklində
- **Söhbət Q&A interfeysi**

### Əsas İmkanlar

| Funksiya | Təsvir |
|----------|--------|
| 🔍 **Semantik axtarış** | Məna üzrə axtarış, yalnız açar sözlər deyil |
| 📊 **Avtomatik kateqorizasiya** | Süni intellekt xəbərləri təsnif edir (siyasət, iqtisadiyyat, idman və s.) |
| 🏷️ **Entity çıxarma** | Şəxslərin, təşkilatların, məkanların müəyyənləşdirilməsi |
| 💬 **Sentiment analizi** | Müsbət/neytral/mənfi tonun aşkarlanması |
| 📈 **Əhəmiyyət qiymətləndirilməsi** | Xəbərlərin əhəmiyyətinə görə sıralanması (1-10) |
| 🌐 **Çoxdillilik** | Azərbaycan, İngilis, Rus dillərinin dəstəyi |
| 🌌 **Xəbərlər Kainatı** | İnteraktiv qraf vizualizasiyası |

---

## 🏗️ Sistem Arxitekturası

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MƏLUMAT TOPLAMA QATİ                               │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │ Telegram Fetcher │ -> │ Content Parser   │ -> │ JSON Storage     │       │
│  │ (Telethon)       │    │ (BeautifulSoup)  │    │ (Xam Məqalələr)  │       │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MƏLUMAT İŞLƏMƏ QATİ                                │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │ Text Cleaner     │ -> │ LLM Analyzer     │ -> │ Text Chunker     │       │
│  │ (Təmizləmə)      │    │ (OpenAI GPT-4)   │    │ (LangChain)      │       │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘       │
│                                      │                                       │
│                    Çıxarılan metadata:                                       │
│                    • Kateqoriya, Entitylər, Sentiment                        │
│                    • Əhəmiyyət, Xülasə, Coğrafi əhatə                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SAXLAMA QATİ                                       │
│  ┌──────────────────────────┐    ┌──────────────────────────────┐           │
│  │ ChromaDB                 │    │ PostgreSQL                   │           │
│  │ • Vektor embeddingləri   │    │ • Məqalələr, Entitylər       │           │
│  │ • Semantik axtarış       │    │ • Mənbələr, Əlaqələr         │           │
│  │ • Metadata filtrləmə     │    │ • İstifadəçilər, Analitika   │           │
│  └──────────────────────────┘    └──────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TƏTBİQ QATİ                                        │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                        FastAPI Backend                            │       │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │       │
│  │  │ News API   │ │ Search API │ │ Chat API   │ │ Graph API  │     │       │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘     │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                        React Frontend                             │       │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │       │
│  │  │ Xəbər Lenti│ │ Söhbət     │ │ Kainat     │ │ Analitika  │     │       │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘     │       │
│  └──────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Modulların Ətraflı Təsviri

### 1. Telegram Fetcher Modulu (`telegram_fetcher/`)

**Məqsəd**: Telegram xəbər kanallarından asinxron məlumat toplama.

```
telegram_fetcher/
├── base.py           # TelegramCollector - Telethon client wrapper
├── services.py       # NewsCollectionService - çoxlu mənbə orkestrasiyası
├── config.py         # API credentials idarəetməsi
└── parsers/
    ├── base.py       # Abstrakt interfeyslər (IURLExtractor, IContentParser)
    ├── qafqazinfo.py # Sayt-spesifik parser realizasiyası
    └── __main__.py   # CLI giriş nöqtəsi
```

**Məlumat Axını**:
```
Telegram Kanal → Mesajların alınması → URL çıxarma → Məqalə parsing → JSON
```

**Əsas Texniki Qərarlar**:
- **Telethon** Telegram API üçün (asinxron, səmərəli)
- **aiohttp** paralel HTTP sorğuları üçün (multithreading-dən 2-3 dəfə sürətli)
- **Semaphore** rate limiting üçün (konfiqurasiya olunan paralellik)
- **BeautifulSoup** HTML parsing üçün

**Çıxış Formatı**:
```json
{
  "id": 12345,
  "date": "2024-11-24T10:30:00+00:00",
  "text": "Telegram-dan önizləmə...",
  "url": "https://qafqazinfo.az/news/detail/12345",
  "detail": "Veb-səhifədən çıxarılmış tam məqalə mətni...",
  "image_url": "https://qafqazinfo.az/uploads/image.jpg"
}
```

---

### 2. RAG Modulu (`rag_module/`)

**Məqsəd**: Sənəd emalı və axtarış üçün tam konveyer.

```
rag_module/
├── data_processing/       # Sənəd transformasiyası
│   ├── protocols.py       # İnterfeyslər (ITextAnalyzer, IChunker, ITextCleaner)
│   ├── analyzers/         # OpenAI ilə məzmun analizi
│   ├── chunkers.py        # Mətn bölmə strategiyaları
│   ├── cleaners.py        # Telegram markdown təmizləmə
│   ├── loaders.py         # JSON məlumat yükləmə
│   └── pipeline.py        # Emal orkestrasiyası
│
├── vector_store/          # Vektor DB əməliyyatları
│   ├── chroma_store.py    # ChromaDB realizasiyası
│   ├── embedding.py       # OpenAI embeddings wrapper
│   ├── batch_processor.py # Səmərəli batch emal
│   └── protocols.py       # Storage interfeyslər
│
├── query_processing/      # İstifadəçi sorğusu emalı
│   ├── router.py          # Intent təsnifatı
│   ├── pipeline.py        # Sorğu transformasiyası
│   └── llm_processor.py   # Dil aşkarlanması, NER
│
├── retrieval/             # Axtarış və generasiya
│   ├── pipeline.py        # Axtarış orkestrasiyası
│   ├── llm_generator.py   # Cavab sintezi
│   └── handlers/          # Intent-spesifik handerlər
│
└── services/              # Yüksək səviyyəli API-lər
    ├── vectorization.py   # Sənəd vektorlaşdırma servisi
    ├── vectorization_v2.py# PostgreSQL persistensiyası ilə
    └── qa_service.py      # Sual-cavab servisi
```

#### 2.1 Məlumat Emalı Konveyeri

**Kritik Pattern: "BİR DƏFƏ Analiz et, ÇOX Böl"**

Bu, LLM xərclərini 90%+ qənaət edən əsas optimallaşdırmadır:

```python
# ✅ DÜZGÜN: Tam məqaləni BİR DƏFƏ analiz et, sonra böl
full_article = article["detail"]           # Tam mətn
metadata = analyzer.analyze(full_article)  # 1 LLM çağırışı

chunks = chunker.chunk(full_article)       # Hissələrə böl
for chunk in chunks:
    chunk.metadata = metadata              # Bütün chunk-lar eyni metadata

# ❌ YANLIŞ: Hər chunk-ı ayrıca analiz etmək
for chunk in chunks:
    metadata = analyzer.analyze(chunk)     # N LLM çağırışı - bahalı!
```

**LLM Analiz Çıxışı**:
```json
{
  "category": "politics",
  "entities": ["İlham Əliyev", "Azərbaycan", "Bakı"],
  "sentiment": "neutral",
  "sentiment_score": 0.1,
  "importance": 8,
  "summary": "Prezident İlham Əliyev Bakıda keçirilən...",
  "is_breaking": false,
  "geographic_scope": "national"
}
```

#### 2.2 Vektor Anbarı

**Embedding Strategiyası**:
- Model: `text-embedding-3-small` (qənaətcil) və ya `text-embedding-3-large` (yüksək keyfiyyət)
- Chunk ölçüsü: 100 simvol üst-üstə düşmə ilə 600 simvol
- Bölmə: LangChain RecursiveCharacterTextSplitter

**ChromaDB Konfiqurasiyası**:
- `./chroma_db`-də persistent saxlama
- Embedded və client rejimlərinin dəstəyi
- Hibrid axtarış üçün metadata filtrləmə

#### 2.3 Sorğu Emalı

**Intent Təsnifatı**:
| Intent | Nümunə | Strategiya |
|--------|--------|------------|
| FACTOID | "Prezident kimdir?" | Semantik axtarış |
| STATISTICAL | "Neçə aksiya olub?" | Aggregation + sayma |
| ANALYTICAL | "Qiymətlər niyə artdı?" | Multi-sənəd analizi |
| TASK | "Günün xəbərlərini xülasə et" | Xüsusi handler |

#### 2.4 Sual-Cavab Servisi

Tam RAG konveyeri:
```
İstifadəçi sorğusu → Dil aşkarlanması → Tərcümə → NER → 
Intent təsnifatı → Vektor axtarış → LLM generasiyası → 
Mənbələrlə strukturlaşdırılmış cavab
```

---

### 3. Backend (`backend/`)

**Məqsəd**: Frontend və xarici inteqrasiyalara xidmət edən FastAPI REST API.

```
backend/src/
├── main.py            # Tətbiq girişi, lifespan, middleware
├── config.py          # Environment variables-dən parametrlər
├── database.py        # Asinxron SQLAlchemy quraşdırması
├── dependencies.py    # Dependency injection konteyneri
├── news/
│   ├── router.py      # Xəbər endpointləri (/news, /categories, /graph)
│   ├── schemas.py     # Pydantic modelləri
│   └── services/
│       ├── postgres.py # PostgreSQL sorğuları
│       └── chroma.py   # Vektor axtarış
├── chats/             # Söhbət tarixçəsi idarəetməsi
├── auth/              # JWT autentifikasiya
└── users/             # İstifadəçi idarəetməsi
```

**Əsas Endpointlər**:
| Endpoint | Metod | Təsvir |
|----------|-------|--------|
| `/news/` | GET | Səhifələnmiş xəbər siyahısı |
| `/news/categories` | GET | Say ilə kateqoriyalar |
| `/news/graph` | GET | Qraf vizualizasiya məlumatları |
| `/news/entity-graph` | GET | Entity əsaslı qraf |
| `/news/search` | POST | Semantik axtarış |
| `/chats/ask` | POST | RAG ilə Q&A |

**Miqyaslanma Dizaynı**:
- Stateless arxitektura (horizontal scaling-ə hazır)
- Hər yerdə async I/O (yüksək throughput)
- Verilənlər bazaları üçün connection pooling
- Health check-lərlə Docker-ready

---

### 4. Frontend (`frontend/`)

**Məqsəd**: Xəbər baxışı, söhbət və vizualizasiya üçün React SPA.

```
frontend/src/
├── App.tsx              # Root komponent, routing
├── components/
│   ├── ChatMessages.tsx # Mesaj tarixçəsi göstərilməsi
│   ├── ChatInput.tsx    # Göndərmə ilə giriş sahəsi
│   ├── NewsEventCard.tsx# Xəbər kartı komponenti
│   └── ...
├── universe/
│   ├── UniversePage.tsx # İnteraktiv xəbər qrafı
│   ├── types.ts         # Qraf məlumat tipləri
│   └── api.ts           # Qraf API çağırışları
├── hooks/
│   ├── useChat.ts       # Söhbət state idarəetməsi
│   ├── useTheme.ts      # Qaranlıq/işıqlı tema
│   └── useLanguage.ts   # i18n dəstəyi
└── i18n/                # Tərcümələr (az, en, ru)
```

**Əsas Funksiyalar**:
- **Xəbər Lenti**: Filtrələnə bilən, səhifələnmiş siyahı
- **Söhbət İnterfeysi**: Təbii dildə Q&A
- **Xəbərlər Kainatı**: İnteraktiv qraf:
  - Sürüklənə bilən node-lar (touch + mouse)
  - Pan/zoom naviqasiyası
  - Entity əsaslı əlaqələr
  - Tarix filtrləmə
  - Sentiment rəng kodlaması

---

### 5. İnfrastruktur (`docker/`)

**Docker Compose Servisləri**:
```yaml
services:
  chromadb:    # Vektor verilənlər bazası
  postgres:    # Relyasion verilənlər bazası
  backend:     # FastAPI tətbiqi
  frontend:    # React tətbiqi (nginx)
  nginx:       # Reverse proxy, SSL
```

**Şəbəkə Arxitekturası**:
```
İnternet → Nginx (80/443) → Frontend (statik)
                         → Backend (API /api/*)
                         
Backend → ChromaDB (8000)
       → PostgreSQL (5432)
```

---

## 🔧 Həll Edilən Texniki Problemlər

### 1. LLM Xərc Optimallaşdırması
**Problem**: Hər chunk-ı ayrıca analiz etmək = bahalı  
**Həll**: "BİR DƏFƏ Analiz et, ÇOX Böl" pattern - 90%+ xərc azalması

### 2. Miqyasda Asinxron Emal
**Problem**: Minlərlə məqalənin səmərəli emalı  
**Həll**: 
- Semaphore-kontrollü paralellik (maks. 50 paralel)
- Progress tracking ilə batch emal
- Rate limit-lər üçün eksponensial backoff

### 3. Çoxdilli Axtarış
**Problem**: İstifadəçilər fərqli dillərdə sorğu edir  
**Həll**: 
- Sorğu zamanı dil aşkarlanması
- Axtarış üçün Azərbaycan dilinə tərcümə
- Orijinal dildə cavab

### 4. Real-time Qraf Vizualizasiyası
**Problem**: Çoxlu node ilə səlis qarşılıqlı əlaqə  
**Həll**:
- Animasiyalar üçün React + Framer Motion
- viewOffset ilə virtual mövqeləndirmə
- Mobil üçün touch event dəstəyi

### 5. Məlumat Keyfiyyəti
**Problem**: Telegram mesajlarında markdown, emoji, artefaktlar  
**Həll**: Xüsusi təmizləyicilər:
- Telegram markdown silmə
- Emoji normallaşdırma
- URL çıxarma
- Whitespace normallaşdırma

---

## 🚀 Lokal İnkişaf

### Ön Tələblər

- Docker və Docker Compose
- Python 3.12+ (lokal inkişaf üçün)
- Node.js 20+ (frontend inkişafı üçün)
- OpenAI API açarı
- Telegram API credentials

### Tez Başlanğıc

```bash
# 1. Repozitoriyanı klonlayın
git clone https://github.com/ImranRahimov1995/SearchNewsRAG.git
cd SearchNewsRAG

# 2. Environment şablonunu kopyalayın
cp .env.example .env
# .env-i API açarlarınızla redaktə edin

# 3. Bütün servisləri işə salın
docker-compose up --build

# 4. Tətbiqə giriş
# Frontend: http://localhost
# API: http://localhost/api
# API Docs: http://localhost/api/docs
```

### İnkişaf Əmrləri

```bash
# Asılılıqları quraşdırın
make install

# Testləri işə salın
make test

# Linterləri işə salın
make lint

# Kodu formatlaşdırın
make format

# Tam CI yoxlaması
make ci

# Verilənlər bazası miqrasiyaları
make migrate-up
make migrate-create name="add_new_table"
```

### Məlumat Konveyeri

```bash
# 1. Telegram-dan xəbər toplayın
python -m telegram_fetcher --stop-date 2025-01-01

# 2. Məqalələrin tam mətnini parsing edin
python -m telegram_fetcher.parsers --site qafqazinfo --input data/qafqazinfo.json

# 3. LLM analizi ilə vektorlaşdırın
python -m rag_module vectorize \
  --source data/qafqazinfo.json \
  --source-name qafqazinfo_2025 \
  --collection news_v1

# 4. Kolleksiyanı yoxlayın
python -m rag_module info --collection news_v1
```

---

## 📈 Production Deploy

Ətraflı təlimatlar üçün [docs/DEPLOYMENT.md](DEPLOYMENT.md)-ə baxın.

**Əsas Nöqtələr**:
- GitHub Actions CI/CD pipeline
- Docker multi-stage build-lər
- SSL ilə Nginx reverse proxy
- Bütün servislər üçün health check-lər

---

## 📚 Sənədləşdirmə

| Sənəd | Təsvir |
|-------|--------|
| [DATA_COLLECTION.md](DATA_COLLECTION.md) | Telegram fetcher və content parserlər |
| [VECTORIZATION_SERVICE.md](VECTORIZATION_SERVICE.md) | Sənəd emalı konveyeri |
| [QA_SERVICE.md](QA_SERVICE.md) | Sual-cavab sistemi |
| [DEPLOYMENT.md](DEPLOYMENT.md) | CI/CD və production quraşdırma |

---

## 🛠️ Texnoloji Stek

| Kateqoriya | Texnologiyalar |
|------------|----------------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy, Pydantic |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Framer Motion |
| **AI/ML** | OpenAI GPT-4, text-embedding-3-small, LangChain |
| **Verilənlər Bazaları** | PostgreSQL 16, ChromaDB |
| **Məlumat Toplama** | Telethon, aiohttp, BeautifulSoup |
| **İnfrastruktur** | Docker, Nginx, GitHub Actions |
| **Kod Keyfiyyəti** | Ruff, MyPy, Black, Pytest, Pre-commit |

---

## 📄 Lisenziya

MIT License - [LICENSE](../LICENSE) faylına baxın

---

## 👤 Müəllif

**İmran Rəhimov**  
Email: mr.rahimov.imran@gmail.com  
GitHub: [@ImranRahimov1995](https://github.com/ImranRahimov1995)
