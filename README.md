# Automated Lead Management & Email Tracking System

A full-stack application for capturing sales leads, automatically emailing them a
personalized thank-you message, tracking whether they opened the email / clicked
the link inside it, classifying each lead with a simple keyword-based "AI"
classifier, and visualizing everything on a dashboard.

Runs **100% on localhost** — no cloud deployment, no Render, nothing external
except Gmail's SMTP server for sending the actual emails.

---

## Tech Stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Frontend   | React + Vite, Tailwind CSS, Recharts     |
| Backend    | FastAPI (Python), Motor (async MongoDB)  |
| Database   | MongoDB                                  |
| Email      | Gmail SMTP (via environment variables)   |

---

## Folder Structure

```
lead-management-system/
├── backend/
│   ├── main.py             # FastAPI app, routes: /lead, /leads, /dashboard
│   ├── database.py         # MongoDB connection (Motor)
│   ├── models.py           # Lead model (internal DB representation)
│   ├── schemas.py          # Request/response Pydantic schemas
│   ├── email_service.py    # Gmail SMTP sending + email body builder
│   ├── tracking.py         # /open/{lead_id} and /click/{lead_id} endpoints
│   ├── ai_classifier.py    # Keyword-based category + priority classifier
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── .env.example
    └── src/
        ├── main.jsx
        ├── App.jsx                  # Nav bar + routing
        ├── index.css
        ├── services/
        │   └── api.js                # Axios client / API calls
        ├── pages/
        │   ├── HomePage.jsx           # Lead capture form page
        │   └── DashboardPage.jsx      # Dashboard page
        └── components/
            ├── LeadForm.jsx           # The lead capture form
            ├── StatCards.jsx          # Dashboard summary cards
            ├── ChartsPanel.jsx        # Recharts visualizations
            └── LeadsTable.jsx         # Searchable leads table
```

---

## Prerequisites

- **Python 3.10+** (tested through **Python 3.13**)
- **Node.js 18+** and npm
- **MongoDB** running locally (default: `mongodb://localhost:27017`)
  - Install from https://www.mongodb.com/try/download/community, or run via Docker:
    ```bash
    docker run -d --name lead-mongo -p 27017:27017 mongo:7
    ```
- A **Gmail account** with an **App Password** (see below) for sending real emails.
  This step is optional to *run* the app — if you skip it, leads are still saved
  and tracked, the system just won't actually send the email (it logs a warning
  instead of crashing).

### Generating a Gmail App Password

1. Enable 2-Step Verification on your Google account.
2. Go to https://myaccount.google.com/apppasswords
3. Create an app password (choose "Mail" as the app).
4. Copy the 16-character password — you'll put this in `.env` as `GMAIL_APP_PASSWORD`.

---

## Backend Setup

```bash
cd backend

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies (requirements.txt is unpinned — always installs the
#    latest stable, mutually-compatible versions of each package)
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and fill in your MongoDB URI and Gmail credentials

# 4. Run the API server
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**.
Interactive API docs (Swagger UI) are auto-generated at **http://localhost:8000/docs**.

### Backend `.env` variables

| Variable             | Description                                            | Example                          |
|-----------------------|----------------------------------------------------------|-----------------------------------|
| `MONGO_URI`          | MongoDB connection string                               | `mongodb://localhost:27017`      |
| `DB_NAME`            | Database name                                           | `lead_management`                |
| `GMAIL_USER`         | Gmail address used to send emails                       | `you@gmail.com`                  |
| `GMAIL_APP_PASSWORD` | 16-character Gmail App Password (not your normal password) | `abcdwxyzabcdwxyz`            |
| `SMTP_HOST`          | SMTP host                                               | `smtp.gmail.com`                 |
| `SMTP_PORT`          | SMTP port (SSL)                                         | `465`                             |
| `BASE_URL`           | This backend's base URL (used to build tracking links)  | `http://localhost:8000`          |
| `FRONTEND_URL`       | Frontend dev server URL (used for CORS)                 | `http://localhost:5173`          |

---

## Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment variables
cp .env.example .env
# Default VITE_API_URL=http://localhost:8000 is correct for local dev

# 3. Run the dev server
npm run dev
```

The app will be available at **http://localhost:5173**.

---

## Using the App

1. Open **http://localhost:5173** — fill out the **Lead Form** (Name, Email, Phone,
   optional Company, and your Requirement) and submit.
2. The backend:
   - Validates the input
   - Runs the keyword-based AI classifier (assigns `category` + `priority`)
   - Saves the lead to MongoDB
   - Sends a personalized "Thank You For Contacting Us" email containing a
     tracked link and a hidden tracking pixel
3. Open **http://localhost:5173/dashboard** to see:
   - Summary cards: Total Leads, Emails Sent, Emails Opened, Open Rate %, Link
     Clicks, Click Rate %
   - Charts: email engagement funnel, leads by category, leads by priority
   - A searchable table of every lead with full tracking status
4. When the real recipient opens the email, their email client loads the
   tracking pixel, which hits `GET /open/{lead_id}` and flips `email_opened`
   to `true`. If they click the "learn more" link, it hits
   `GET /click/{lead_id}`, flips `link_clicked` to `true`, then redirects them
   to `https://example.com`.

> **Note on email open tracking:** many email clients (e.g. Gmail) cache or
> proxy remote images, and some block remote images by default until the user
> clicks "Display images below". This is a universal limitation of pixel-based
> open tracking, not specific to this implementation.

---

## API Reference

| Method | Endpoint              | Description                                              |
|--------|------------------------|-----------------------------------------------------------|
| POST   | `/lead`                | Create a new lead, classify it, save it, email it        |
| GET    | `/leads?search=...`    | List all leads (optional case-insensitive search filter) |
| GET    | `/dashboard`           | Aggregated stats for the dashboard                        |
| GET    | `/open/{lead_id}`      | Tracking pixel endpoint — marks email as opened           |
| GET    | `/click/{lead_id}`     | Tracked link endpoint — marks link clicked, redirects     |

### Example: `POST /lead`

Request body:
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "9876543210",
  "company": "Acme Corp",
  "requirement": "We need a mobile app for our delivery business, fairly urgent"
}
```

Response:
```json
{
  "id": "2d1af6bb-1d7c-49d5-a16b-c8b834e408df",
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "9876543210",
  "company": "Acme Corp",
  "requirement": "We need a mobile app for our delivery business, fairly urgent",
  "submitted_at": "2026-06-25T09:46:13.745485",
  "email_sent": true,
  "email_opened": false,
  "opened_at": null,
  "link_clicked": false,
  "clicked_at": null,
  "category": "Mobile App",
  "priority": "High"
}
```

---

## AI Lead Classifier (Bonus)

`backend/ai_classifier.py` implements a fully offline, deterministic,
keyword-based classifier (no external AI API calls, so it always works on
localhost with zero extra setup):

- **Category** — scores the requirement text against keyword lists for each
  of: `AI Automation`, `Web Development`, `Mobile App`, `Machine Learning`,
  `Data Analytics`. The category with the most keyword matches wins; if
  nothing matches, the lead is classified as `General`.
- **Priority** — `High` if the text contains urgency signals (e.g. "urgent",
  "asap", "enterprise", "deadline"); `Low` if it contains low-intent signals
  (e.g. "just exploring", "not sure", "maybe"); otherwise `Medium` (or `Low`
  for very short, vague messages).

Both `category` and `priority` are stored on the lead document and shown in
the dashboard table and charts.

---

## Tech Notes

- Lead IDs are UUID strings (not MongoDB ObjectIds), stored directly as `_id`.
  This keeps tracking URLs (`/open/{lead_id}`, `/click/{lead_id}`) simple
  plain strings with no ObjectId serialization headaches.
- The email is sent as a `multipart/alternative` message with both a plain
  text and an HTML body (the HTML body contains the tracking pixel).
- If `GMAIL_USER` / `GMAIL_APP_PASSWORD` are not set, the lead is still saved
  and returned successfully — `email_sent` just stays `false`, and a warning
  is logged. This means you can fully exercise the lead-capture + dashboard
  flow without ever configuring Gmail.
- CORS is enabled for the Vite dev server origin (`http://localhost:5173`).

---

## Troubleshooting

- **"Database not available" / 503 errors** — make sure MongoDB is running
  and `MONGO_URI` in `backend/.env` is correct.
- **Email not sending** — double check you're using a Gmail **App Password**
  (not your regular password), and that 2-Step Verification is enabled on the
  Google account. Check the backend terminal logs for the exact SMTP error.
- **CORS errors in the browser console** — make sure `FRONTEND_URL` in
  `backend/.env` matches the URL the frontend is actually running on.
- **Tracking pixel not marking emails as opened** — many email clients block
  remote images by default; the recipient may need to click "show images".
