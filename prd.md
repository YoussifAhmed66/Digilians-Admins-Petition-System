# Digilians External Exit Petition System (DEEPS)
## Product Requirements Document (PRD)

---

# 1. Project Overview

## Project Name
Digilians External Exit Petition System (DEEPS)

## Purpose

The system allows students to submit temporary exit requests electronically through a public-facing form integrated with the LMS ecosystem.

Students can:
- submit exit requests
- upload supporting attachments
- generate official DOCX and PDF documents automatically

The system stores all data in Supabase PostgreSQL and generates formal documents using the official Word template located at:

```text
docs/external.docx
```

The generated documents preserve all official formatting while automatically filling student-related fields only.

Administrative sections remain empty for later manual processing.

---

# 2. Core Objectives

## Primary Goals

- Allow students to submit exit requests online
- Generate official DOCX and PDF documents
- Store petitions securely
- Support Arabic RTL UI
- Prevent duplicate active requests
- Support responsive desktop/mobile usage
- Use lightweight stack without frontend frameworks

---

# 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Backend | FastAPI |
| Database | Supabase PostgreSQL |
| Storage | Supabase Storage |
| DOCX Generation | docxtpl |
| PDF Conversion | LibreOffice Headless |
| Hosting | Hugging Face Docker Space |
| Searchable Dropdowns | Choices.js |

---

# 4. System Architecture

```text
Student Browser
        ↓
Frontend (HTML/CSS/JS)
        ↓
FastAPI REST API
        ↓
Supabase PostgreSQL
        ↓
Supabase Storage

FastAPI
        ↓
DOCX Template Rendering
        ↓
PDF Conversion
        ↓
Generated Documents Storage
```

---

# 5. Official Template

## Template Path

```text
docs/external.docx
```

## Template Type

Official Arabic Word document.

## Rendering Strategy

The template uses Jinja placeholders via `docxtpl`.

Only student-related fields are auto-filled.

Administrative sections remain empty.

---

# 6. User Scope

## Current Scope

Only student-side submission workflow is included.

## Excluded For Now

- Admin dashboard
- Authentication
- Notifications
- Digital signatures
- Approval workflow

---

# 7. Student Form Requirements

# 7.1 Form Type

- Single-page form
- Arabic RTL interface
- Responsive design
- Desktop-first with mobile support

---

# 7.2 Input Fields

| Field | Type | Required |
|---|---|---|
| الاسم | Text | Yes |
| الرقم العسكري | Text | Yes |
| البرنامج | Searchable Dropdown | Yes |
| المسار | Searchable Dropdown | Yes |
| كود المعمل | Searchable Dropdown | Yes |
| تاريخ الخروج | Date Picker | Yes |
| وقت الخروج | Time Picker | Yes |
| تاريخ العودة | Date Picker | Yes |
| وقت العودة | Time Picker | Yes |
| سبب الخروج | Multi Checkbox | Yes |
| الوصف | Textarea | Conditional |
| المرفقات | Multiple File Upload | Optional |

---

# 7.3 Program Options

Programs are stored in database.

Initial values:

```text
مكثف
متخصص
```

---

# 7.4 Track Behavior

Tracks depend on selected program.

Relationship:

```text
Program → Many Tracks
```

Tracks are fetched dynamically from backend.

---

# 7.5 Lab Behavior

Labs depend on selected track.

Relationship:

```text
Track → Many Labs
```

Lab selection is mandatory.

Labs are fetched dynamically from backend.

---

# 7.6 Exit Reasons

Students may select multiple reasons.

Available reasons:

- حالة عائلية طارئة
- حضور امتحان خارجي
- ظرف خاص آخر يُرجى التوضيح
- حالة طارئة

---

# 7.7 Description Rules

Description field:
- always visible
- optional normally
- required when:
  ```text
  ظرف خاص آخر يُرجى التوضيح
  ```
  is selected

Maximum length:

```text
2000 characters
```

---

# 8. Frontend UI Requirements

# 8.1 UI Style

Hybrid design:
- formal administrative appearance
- modern clean UI

---

# 8.2 Direction

Entire interface must use:

```css
direction: rtl;
```

---

# 8.3 Fonts

Recommended frontend fonts:

- Cairo
- Noto Sans Arabic

---

# 8.4 Responsive Layout

## Desktop
- two-column layout

## Mobile
- single-column stacked layout

---

# 8.5 Searchable Dropdowns

Library:

```text
Choices.js
```

Requirements:
- searchable
- RTL compatible
- keyboard accessible
- mobile friendly

---

# 8.6 File Upload UX

Features:
- multiple file upload
- file preview
- file removal before submission
- upload validation

---

# 8.7 Validation Rules

| Validation | Type |
|---|---|
| Arabic-only names | Regex |
| Trim spaces | Yes |
| Return datetime > exit datetime | Yes |
| Active petition prevention | Backend |
| Max files | 5 |
| Max size | 10MB per file |
| Allowed file types | PDF/JPG/JPEG/PNG |
| Description required for special reason | Yes |

---

# 9. Petition Lifecycle

# 9.1 Active Petition Rule

A student cannot create another petition while current petition is active.

## Active Condition

```text
current_date <= return_date
```

Validation performed in backend.

---

# 9.2 Submission Success

Frontend displays:

```text
تم إرسال طلب الخروج بنجاح

رقم الطلب:
EXT-20260511-0001
```

No automatic download.

---

# 10. Database Design

# 10.1 programs

```sql
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name_ar TEXT NOT NULL UNIQUE,

    created_at TIMESTAMP DEFAULT now()
);
```

---

# 10.2 tracks

```sql
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    program_id UUID REFERENCES programs(id)
    ON DELETE CASCADE,

    name_ar TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT now()
);
```

---

# 10.3 labs

```sql
CREATE TABLE labs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    track_id UUID REFERENCES tracks(id)
    ON DELETE CASCADE,

    code TEXT NOT NULL UNIQUE,

    created_at TIMESTAMP DEFAULT now()
);
```

---

# 10.4 petitions

```sql
CREATE TABLE petitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    petition_code TEXT NOT NULL UNIQUE,

    student_name_ar TEXT NOT NULL,

    military_number TEXT NOT NULL,

    program_id UUID REFERENCES programs(id),

    track_id UUID REFERENCES tracks(id),

    lab_id UUID REFERENCES labs(id),

    exit_datetime TIMESTAMP NOT NULL,

    return_datetime TIMESTAMP NOT NULL,

    submitted_date DATE NOT NULL,

    description TEXT,

    reasons JSONB NOT NULL,

    generated_docx_url TEXT,

    generated_pdf_url TEXT,

    created_at TIMESTAMP DEFAULT now()
);
```

---

# 10.5 petition_attachments

```sql
CREATE TABLE petition_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    petition_id UUID REFERENCES petitions(id)
    ON DELETE CASCADE,

    original_name TEXT NOT NULL,

    stored_name TEXT NOT NULL,

    file_url TEXT NOT NULL,

    file_size BIGINT,

    mime_type TEXT,

    created_at TIMESTAMP DEFAULT now()
);
```

---

# 11. Reasons Storage

Reasons are stored as JSON array.

Example:

```json
[
  "حالة عائلية طارئة",
  "حضور امتحان خارجي"
]
```

---

# 12. Petition Numbering System

Format:

```text
EXT-YYYYMMDD-XXXX
```

Example:

```text
EXT-20260511-0001
```

Components:
- EXT → external exit request
- date stamp
- daily sequence number

---

# 13. File Storage Structure

# Attachments

```text
attachments/
    petition_code/
        timestamp_filename.ext
```

Example:

```text
attachments/
    EXT-20260511-0001/
        EXT-20260511-0001_20260511153022_report.pdf
```

---

# Generated Documents

```text
generated/
    petition_code/
        petition.docx
        petition.pdf
```

---

# 14. File Privacy

All attachments and generated documents must be private.

Students must not be able to browse or access other users' files.

Use:
- Supabase private buckets
- signed URLs

---

# 15. DOCX Template Placeholders

Example placeholders:

```text
{{ student_name }}

{{ military_number }}

{{ program }}

{{ track }}

{{ exit_date }}
{{ exit_day }}
{{ exit_time }}

{{ return_date }}
{{ return_day }}
{{ return_time }}

{{ reason_family }}
{{ reason_exam }}
{{ reason_special }}
{{ reason_emergency }}

{{ description }}
```

---

# 16. Checkbox Rendering

Checkboxes rendered dynamically using Unicode:

```text
☑
☐
```

Example:

```text
☑ حالة طارئة
☐ حضور امتحان خارجي
```

---

# 17. Arabic Date/Time Formatting

# Days

Arabic weekday names:

```text
الأحد
الاثنين
الثلاثاء
الأربعاء
الخميس
الجمعة
السبت
```

---

# Time Format

Arabic style:

```text
08:30 ص
02:15 م
```

Timezone:

```text
Africa/Cairo
```

---

# 18. Document Generation Workflow

```text
Student submits form
        ↓
Backend validates request
        ↓
Check active petition
        ↓
Upload attachments
        ↓
Save petition
        ↓
Render DOCX template
        ↓
Convert DOCX → PDF
        ↓
Upload generated documents
        ↓
Save document URLs
        ↓
Return success response
```

---

# 19. API Endpoints

# Student APIs

## Get Programs

```http
GET /api/programs
```

---

## Get Tracks By Program

```http
GET /api/programs/{id}/tracks
```

---

## Get Labs By Track

```http
GET /api/tracks/{id}/labs
```

---

## Submit Petition

```http
POST /api/petitions
```

Content-Type:

```text
multipart/form-data
```

---

# 20. Backend Folder Structure

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── petitions.py
│   │   ├── programs.py
│   │   ├── tracks.py
│   │   └── labs.py
│   │
│   ├── services/
│   │   ├── document_service.py
│   │   ├── storage_service.py
│   │   ├── petition_service.py
│   │   └── validation_service.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   └── database/
│
├── docs/
│   └── external.docx
│
├── generated/
├── uploads/
│
├── requirements.txt
├── Dockerfile
└── .env
```

---

# 21. Environment Variables

```env
APP_NAME=Digilians External Exit Petition System

APP_ENV=development

SECRET_KEY=your_secret

SUPABASE_URL=your_url

SUPABASE_KEY=your_key

SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

SUPABASE_ATTACHMENTS_BUCKET=attachments

SUPABASE_GENERATED_BUCKET=generated

DOCX_TEMPLATE_PATH=docs/external.docx

MAX_FILE_SIZE_MB=10

MAX_FILES_COUNT=5

ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png

TIMEZONE=Africa/Cairo
```

---

# 22. Docker Requirements

Docker image must include:
- Python
- LibreOffice
- Arabic fonts

Recommended fonts:
- Cairo
- Amiri
- Noto Sans Arabic

---

# 23. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Arabic RTL support | Required |
| Mobile responsiveness | Required |
| Private file storage | Required |
| Lightweight frontend | Required |
| No frontend framework | Required |
| Fast document generation | Required |

---

# 24. Future Scope (Excluded From MVP)

- Admin dashboard
- Authentication
- Approval workflow
- Notifications
- Analytics
- LMS auto-prefill
- Digital signatures

---

# 25. Development Phases

# Phase 1
- Database setup
- Supabase storage setup

# Phase 2
- FastAPI backend APIs

# Phase 3
- Frontend RTL form

# Phase 4
- Dynamic searchable dropdowns

# Phase 5
- File upload integration

# Phase 6
- DOCX generation

# Phase 7
- PDF conversion

# Phase 8
- Deployment to Hugging Face Docker Space

---