# Orthopaedic Abstract Deadline Calendar

A GitHub Pages website plus live iCal feed for orthopaedic conference abstract deadlines.

## What it does

- Checks official conference source pages weekly using GitHub Actions.
- Builds `docs/conferences.json` for the website.
- Builds `docs/ortho-abstract-deadlines.ics` for Google Calendar, Apple Calendar, and Outlook subscriptions.
- Keeps curated deadlines unless the scraper only detects uncertain text. This avoids hallucinated deadline changes.
- Labels meetings by specialty, US/international, high-acceptance strategy, and indexed/publication notes.

## Setup

1. Create a new GitHub repository.
2. Upload this project.
3. In GitHub, go to **Settings → Pages**.
4. Set source to **Deploy from branch**, branch `main`, folder `/docs`.
5. Wait for Pages to publish.
6. Your website will be at `https://YOUR_USERNAME.github.io/YOUR_REPO/`.
7. Your calendar feed URL will be:
   `https://YOUR_USERNAME.github.io/YOUR_REPO/ortho-abstract-deadlines.ics`

## Google Calendar subscription

Google Calendar → Other calendars → `+` → From URL → paste the `.ics` URL.

## Add more conferences

Edit `data/conferences.json`. Add official source URLs only. The scraper checks each URL weekly.

## Important limitation

Some societies hide deadlines behind portals, PDFs, or JavaScript-heavy pages. Those are marked as `watch` or `source check failed` rather than guessed. For high-stakes submissions, verify the official source before submitting.
