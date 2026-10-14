import os
import shutil
import tempfile

from flask import Flask, request, send_file, render_template_string, after_this_request
import yt_dlp

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video Downloader</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, sans-serif; margin: 0; min-height: 100vh;
         display: grid; place-items: center; background: #0f172a; color: #e2e8f0; }
  .card { width: min(92vw, 520px); background: #1e293b; padding: 28px;
          border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,.4); }
  h1 { margin: 0 0 18px; font-size: 1.4rem; }
  input[type=url] { width: 100%; box-sizing: border-box; padding: 14px;
          border-radius: 10px; border: 1px solid #334155; background: #0f172a;
          color: inherit; font-size: 1rem; }
  .row { display: flex; gap: 10px; margin-top: 12px; }
  select { flex: 0 0 120px; padding: 14px; border-radius: 10px; border: 1px solid #334155;
           background: #0f172a; color: inherit; font-size: 1rem; }
  button { flex: 1; padding: 14px; border: 0; border-radius: 10px; font-size: 1rem;
           font-weight: 600; background: #ef4444; color: #fff; cursor: pointer; }
  button:disabled { opacity: .6; cursor: wait; }
  #msg { margin-top: 14px; min-height: 1.2em; font-size: .9rem; color: #94a3b8; }
  .err { color: #fca5a5 !important; }
  small { display:block; margin-top: 16px; color:#64748b; }
</style>
</head>
<body>
  <div class="card">
    <h1>Video Downloader</h1>
    <form id="f">
      <input type="url" id="url" placeholder="YouTube link yahan paste karo" required>
      <div class="row">
        <select id="fmt">
          <option value="video">Video</option>
          <option value="audio">Audio</option>
        </select>
        <button id="btn" type="submit">Download</button>
      </div>
    </form>
    <div id="msg"></div>
    <small>Sirf wahi videos download karo jo tumhare apne hain ya jinki permission hai.</small>
  </div>

<script>
const f = document.getElementById('f');
const btn = document.getElementById('btn');
const msg = document.getElementById('msg');
const urlInput = document.getElementById('url');

// Link paste karte hi download shuru (one-click feel)
urlInput.addEventListener('paste', () => {
  setTimeout(() => { if (urlInput.checkValidity()) f.requestSubmit(); }, 50);
});

f.addEventListener('submit', async (e) => {
  e.preventDefault();
  btn.disabled = true;
  msg.className = '';
  msg.textContent = 'Download ho raha hai, thoda wait karo...';
  try {
    const q = new URLSearchParams({ url: urlInput.value.trim(), fmt: document.getElementById('fmt').value });
    const res = await fetch('/download?' + q);
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      throw new Error(j.error || 'Download fail ho gaya');
    }
    const cd = res.headers.get('Content-Disposition') || '';
    const m = /filename\\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(cd);
    const name = m ? decodeURIComponent(m[1]) : 'video';
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    msg.textContent = 'Ho gaya: ' + name;
  } catch (err) {
    msg.className = 'err';
    msg.textContent = err.message;
  } finally {
    btn.disabled = false;
  }
});
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/download")
def download():
    url = (request.args.get("url") or "").strip()
    fmt = request.args.get("fmt", "video")
    if not url.startswith(("http://", "https://")):
        return {"error": "Valid link daalo"}, 400

    tmpdir = tempfile.mkdtemp(prefix="ytdl_")

    @after_this_request
    def cleanup(response):
        shutil.rmtree(tmpdir, ignore_errors=True)
        return response

    # ffmpeg ki zaroorat na pade isliye single-file formats use kiye hain
    if fmt == "audio":
        fmt_str = "bestaudio[ext=m4a]/bestaudio"
    else:
        fmt_str = "best[ext=mp4]/best"

    opts = {
        "format": fmt_str,
        "outtmpl": os.path.join(tmpdir, "%(title).80s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": False,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        files = os.listdir(tmpdir)
        if not files:
            return {"error": "Koi file nahi bani"}, 500
        path = os.path.join(tmpdir, files[0])
        return send_file(path, as_attachment=True, download_name=files[0])
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return {"error": f"Download nahi ho paya: {str(e)[:200]}"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
