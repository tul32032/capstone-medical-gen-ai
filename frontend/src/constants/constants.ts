// Toggle this to switch between local dev and production
const USE_LOCAL = false;

export const GOOGLE_CLIENT_ID = "524283018158-p47d378627gbsposbe6058a0ltnkd8q3.apps.googleusercontent.com";

export const API_BASE_URL = USE_LOCAL
  ? "http://localhost:8000"
  : "https://capstone-medical-gen-ai-server-524283018158.us-central1.run.app";

export const GOOGLE_CALLBACK = USE_LOCAL
  ? "http://localhost:3000/auth/callback"
  : "https://capstone-medical-gen-ai-fe-524283018158.us-central1.run.app/auth/callback";
