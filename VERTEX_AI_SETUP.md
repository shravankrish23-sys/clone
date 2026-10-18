# Google Cloud Vertex AI Setup Guide for Gemini Flash

Follow these steps to obtain and configure your Google Cloud credentials to use Gemini Flash on Vertex AI.

---

### Step 1: Create or Select a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top and select an existing project or click **"New Project"**.
3. Copy your **Project ID** (e.g. `my-video-project-123456`).

---

### Step 2: Enable Vertex AI API
1. In the search bar at the top, type **"Vertex AI API"**.
2. Click **Vertex AI API** from Marketplace / APIs.
3. Click **Enable**.

---

### Step 3: Create a Service Account & Download Key
1. In the left navigation menu, go to **IAM & Admin** > **Service Accounts**.
2. Click **+ Create Service Account**.
3. Name it (e.g., `gemini-flash-user`), then click **Create and Continue**.
4. In the role dropdown, select **Vertex AI User** (`roles/aiplatform.user`).
5. Click **Continue**, then **Done**.
6. On the Service Accounts list, click on the three dots next to the created service account > **Manage keys**.
7. Click **Add Key** > **Create new key** > Select **JSON** > Click **Create**.
8. A `.json` file will download to your computer.

---

### Step 4: Add the Key to Your Project
1. Move or copy the downloaded `.json` key into `d:\Clone\` and name it `service_account.json`.
2. Create a `.env` file in `d:\Clone\` (or copy `.env.example` to `.env`):
   ```env
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=d:\Clone\service_account.json
   ```

---

### Step 5: Test Connection
Once configured, test the connection by running:
```powershell
python d:\Clone\analyze_video_vertex.py
```
