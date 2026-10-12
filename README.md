# Pranup & Jaya's Wedding

A single-page wedding invitation: lighthouse reveal, event details and an RSVP form.
Plain HTML, CSS and JavaScript, so it runs on GitHub Pages with no build step.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The whole site |
| `hero.mp4` | The looping background video (add it, see below) |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |
| `tools/make-video.sh` | Compresses your recording into `hero.mp4` |

The page works without `hero.mp4`. It shows a dusk scene behind the details until the video is added.

## Put it online

1. Create a repository on GitHub. Free accounts need it to be **public** for Pages.
2. Upload everything in this folder to the repository root, including `.nojekyll`.
3. Open **Settings > Pages**. Under **Build and deployment**, choose **Deploy from a branch**, pick `main` and `/ (root)`, then Save.
4. After a minute or two the site is at `https://YOUR-USERNAME.github.io/REPO-NAME/`.

## Add the video

Run `./tools/make-video.sh your-recording.mov` (needs ffmpeg), or send the recording to Claude to do it.
Keep `hero.mp4` under about 10 MB so it loads quickly on phones. GitHub rejects files over 100 MB.

## Things to know

- The page is hidden from search engines (`noindex` in `index.html`). Anyone with the link can still open it.
- The RSVP form builds an email. Nothing is sent from the page, and the reply address is the `RSVP_EMAIL` line near the bottom of `index.html`.
- The repository is public, so the address, venue and reply email in the source are public too.
- Still to fill in: the reception date, venue name and directions (dashed underlines on the page).
