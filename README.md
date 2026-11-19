# Zuzu Beauty Studio — GitHub + TrueNAS YAML + iOS App

## 1. Upload to GitHub (Auto-Builds Your Docker Image)
1. Create a new GitHub repository (e.g. `zuzu-beauty-studio`).
2. Upload all files from this unzipped folder (make sure `.github/workflows/docker-publish.yml` is included).
3. GitHub Actions will automatically build and publish `ghcr.io/<your-github-username>/zuzu-beauty-studio:latest`.
   *(In GitHub → Package settings, set the package visibility to Public, or log in on TrueNAS.)*

## 2. Deploy in TrueNAS (Install via YAML)
1. Create a TrueNAS ZFS dataset (e.g. `tank/zuzu-data` → `/mnt/tank/zuzu-data`).
2. In TrueNAS **Apps → Discover Apps → Custom App (Install via YAML)**, paste `truenas-app.yaml` (updating `YOUR_GITHUB_USERNAME` and `/mnt/tank/zuzu-data`).
3. Open `http://<truenas-ip>:8080`!

## 3. Install on iPhone (iOS Home Screen App)
1. Open your TrueNAS URL in **Safari on iPhone**.
2. Tap **Share → Add to Home Screen**. It opens full-screen with your Zuzu Beauty Studio icon.

## 4. 2-Way Radicale Sync
- In **Schedule & Sync**, enter your Radicale calendar URL, username, and password, then click **Sync 2-Way**.
- Built-in `/api/radicale-proxy` handles CalDAV `PUT`, `DELETE`, and `REPORT` directly from your TrueNAS container without extra CORS setup.
