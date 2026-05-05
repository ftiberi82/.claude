# EOL / LTS Reference

Usare questa tabella per verificare lo stato di supporto delle tecnologie citate in un documento di gara brownfield.

**Legenda stato:**
- `EOL` — End of Life: nessuna patch di sicurezza, aggiornamento obbligatorio
- `LTS` — Long Term Support: patch di sicurezza garantite fino a `fine_supporto`
- `active` — Supporto corrente (non LTS), aggiornamenti regolari
- `commercial_only` — supporto gratuito terminato, disponibile solo con licenza commerciale

**Legenda rischio:**
- `alto` — EOL senza patch attive
- `medio` — LTS con fine supporto entro 18 mesi dalla data corrente
- `basso` — active o LTS con orizzonte > 18 mesi

> **Nota**: per versioni non presenti in questa tabella, esegui una web search
> `"{tecnologia} {versione} end of life support date"` e documenta la fonte nel JSON.

---

## Java (OpenJDK / Oracle)

| Versione | Stato | Fine supporto (OpenJDK Temurin) | Rischio |
|---|---|---|---|
| 7 | EOL | 2022-07 | alto |
| 8 | LTS | 2026-11 (Temurin) / commercial_only Oracle | medio |
| 11 | LTS | 2027-09 | basso |
| 17 | LTS | 2029-09 | basso |
| 21 | LTS | 2031-09 | basso |
| 22 | active | 2024-09 | medio |

---

## Node.js

| Versione | Stato | Fine supporto LTS | Rischio |
|---|---|---|---|
| 14 | EOL | 2023-04 | alto |
| 16 | EOL | 2023-09 | alto |
| 18 | LTS | 2025-04 | medio |
| 20 | LTS | 2026-04 | basso |
| 22 | LTS | 2027-04 | basso |

---

## Python

| Versione | Stato | Fine supporto | Rischio |
|---|---|---|---|
| 2.7 | EOL | 2020-01 | alto |
| 3.7 | EOL | 2023-06 | alto |
| 3.8 | EOL | 2024-10 | alto |
| 3.9 | active | 2025-10 | medio |
| 3.10 | active | 2026-10 | basso |
| 3.11 | active | 2027-10 | basso |
| 3.12 | active | 2028-10 | basso |

---

## .NET / .NET Core / .NET Framework

| Versione | Stato | Fine supporto | Rischio |
|---|---|---|---|
| .NET Framework 4.5–4.8 | LTS | 2029-01 (con OS) | basso |
| .NET Core 3.1 | EOL | 2022-12 | alto |
| .NET 5 | EOL | 2022-05 | alto |
| .NET 6 | LTS | 2024-11 | alto |
| .NET 7 | EOL | 2024-05 | alto |
| .NET 8 | LTS | 2026-11 | basso |
| .NET 9 | active | 2026-05 | medio |

---

## Angular

| Versione | Stato | Fine supporto | Rischio |
|---|---|---|---|
| 8–11 | EOL | 2021–2022 | alto |
| 12 | EOL | 2022-11 | alto |
| 13 | EOL | 2023-05 | alto |
| 14 | EOL | 2023-11 | alto |
| 15 | EOL | 2024-05 | alto |
| 16 | LTS | 2024-11 | alto |
| 17 | LTS | 2025-05 | medio |
| 18 | active | 2025-11 | medio |
| 19 | active | 2026-05 | basso |

---

## React

| Versione | Stato | Note | Rischio |
|---|---|---|---|
| < 16 | EOL | non supportata | alto |
| 16.x | LTS de facto | patch sicurezza minori | medio |
| 17.x | LTS de facto | nessuna nuova feature | medio |
| 18.x | active | versione corrente raccomandata | basso |

---

## Vue.js

| Versione | Stato | Fine supporto | Rischio |
|---|---|---|---|
| 2.x | EOL | 2023-12 | alto |
| 3.x | active | corrente | basso |

---

## Spring Boot (Java)

| Versione | Stato | Fine supporto OSS | Rischio |
|---|---|---|---|
| 2.5 e precedenti | EOL | 2022–2023 | alto |
| 2.6 | EOL | 2023-02 | alto |
| 2.7 | EOL | 2023-11 | alto |
| 3.0 | EOL | 2023-11 | alto |
| 3.1 | EOL | 2024-08 | alto |
| 3.2 | active | 2025-02 | medio |
| 3.3 | active | 2025-08 | medio |
| 3.4 | active | 2026-02 | basso |

---

## PHP

| Versione | Stato | Fine supporto | Rischio |
|---|---|---|---|
| ≤ 7.4 | EOL | 2022-11 | alto |
| 8.0 | EOL | 2023-11 | alto |
| 8.1 | LTS | 2025-12 | medio |
| 8.2 | active | 2026-12 | basso |
| 8.3 | active | 2027-12 | basso |

---

## Database

| Tecnologia | Versione | Stato | Fine supporto | Rischio |
|---|---|---|---|---|
| PostgreSQL | 11 | EOL | 2023-11 | alto |
| PostgreSQL | 12 | EOL | 2024-11 | alto |
| PostgreSQL | 13 | LTS | 2025-11 | medio |
| PostgreSQL | 14 | LTS | 2026-11 | basso |
| PostgreSQL | 15 | LTS | 2027-11 | basso |
| PostgreSQL | 16 | active | 2028-11 | basso |
| MySQL | 5.7 | EOL | 2023-10 | alto |
| MySQL | 8.0 | LTS | 2026-04 | basso |
| MySQL | 8.4 | LTS | 2032-04 | basso |
| SQL Server | 2014 | EOL | 2024-07 | alto |
| SQL Server | 2016 | EOL | 2026-07 | medio |
| SQL Server | 2019 | LTS | 2030-01 | basso |
| SQL Server | 2022 | LTS | 2033-01 | basso |
| Oracle DB | 19c | LTS | 2027-04 | basso |
| Oracle DB | 21c | active | 2024-04 | alto |
| MongoDB | 4.x | EOL | 2024-02 | alto |
| MongoDB | 5.x | EOL | 2024-10 | alto |
| MongoDB | 6.x | active | 2025-07 | medio |
| MongoDB | 7.x | active | 2026-08 | basso |

---

## Container / Infrastruttura

| Tecnologia | Versione | Stato | Note | Rischio |
|---|---|---|---|---|
| Kubernetes | < 1.27 | EOL | ciclo di vita ~14 mesi per release | alto |
| Kubernetes | 1.29 | active | supportata fino ~2025-06 | medio |
| Kubernetes | 1.30–1.32 | active | versioni correnti | basso |
| Docker Engine | < 23 | EOL | — | alto |
| Docker Engine | 24–27 | active | versioni correnti | basso |

---

## Sistemi Operativi Server

| Tecnologia | Versione | Stato | Fine supporto | Rischio |
|---|---|---|---|---|
| Ubuntu | 18.04 LTS | EOL | 2023-04 (standard) | alto |
| Ubuntu | 20.04 LTS | LTS | 2025-04 | medio |
| Ubuntu | 22.04 LTS | LTS | 2027-04 | basso |
| Ubuntu | 24.04 LTS | LTS | 2029-04 | basso |
| RHEL / CentOS | 7 | EOL | 2024-06 | alto |
| RHEL | 8 | LTS | 2029-05 | basso |
| RHEL | 9 | LTS | 2032-05 | basso |
| Windows Server | 2012/R2 | EOL | 2023-10 | alto |
| Windows Server | 2016 | LTS | 2027-01 | basso |
| Windows Server | 2019 | LTS | 2029-01 | basso |
| Windows Server | 2022 | LTS | 2031-10 | basso |
