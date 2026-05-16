# Admin Petitions — Frontend

Static frontend dashboard for admins to review, approve, and decline student petitions.

## Tech Stack

- Pure HTML / CSS / JavaScript (no build step required)
- Deployed on **Vercel**

## Project Structure

```
frontend/
├── index.html         # Main dashboard page
├── admin.js           # All JS logic + API calls
├── admin_styles.css   # Styling
├── vercel.json        # Vercel routing config
└── .gitignore
```

## Local Development

Since this is plain HTML/JS, just open `index.html` in a browser — or use a simple local server:

```bash
# Python (built-in)
python -m http.server 3000

# Node.js (npx)
npx serve .
```

> ⚠️ Make sure the `API_BASE` in `admin.js` points to your local backend:
> ```js
> const API_BASE = "http://localhost:8000/api/admin";
> ```

## Configuration

Open `admin.js` and set `API_BASE` to your backend URL:

```js
// For local development:
const API_BASE = "http://localhost:8000/api/admin";

// For production (after deploying backend to Cloud Run):
const API_BASE = "https://your-admin-backend.run.app/api/admin";
```

## Deployment (Vercel)

### Option 1: Vercel CLI

```bash
npm i -g vercel
vercel --prod
```

### Option 2: Vercel Dashboard

1. Push this folder as a GitHub repo
2. Go to [vercel.com](https://vercel.com) → New Project
3. Import the repo
4. **Root Directory:** leave as `/` (or set to `frontend/` if importing the parent)
5. **Framework Preset:** Other
6. Click Deploy

> No build step needed — Vercel serves static files directly.
