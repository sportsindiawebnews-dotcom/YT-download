# Video Downloader

Link paste karo, video ya audio download ho jayega.

## Laptop par chalane ke liye
```
pip install -r requirements.txt
python app.py
```
Phir browser mein http://localhost:5000 kholo.

## Online deploy (Render, free)
1. Ye folder GitHub repo mein push karo.
2. render.com par "New Web Service" -> repo select karo (render.yaml apne aap detect ho jayegi).
3. Deploy hone ke baad Render ka link open karo.

Note: Netlify par ye nahi chalega, kyunki Netlify par Python server nahi chalta.
Agar YouTube kabhi download block kare to `pip install -U yt-dlp` se update karo.

Sirf apne videos ya jinki permission ho unhi ko download karo.
