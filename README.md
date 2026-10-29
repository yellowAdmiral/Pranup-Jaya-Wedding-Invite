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
| `art/` | The watercolour lighthouse painting, in layers |
| `tools/paint-scene.py` | Paints the layers in `art/` (run it again after changing colours or shapes) |

The page opens on a watercolour painting of the same spot as the film: chalk cliff, banded lighthouse, golden grass. Pressing the button turns the beam towards the viewer and the light spreads like paint on wet paper, then clears to the video.

## Put it online

1. Create a repository on GitHub. Free accounts need it to be **public** for Pages.
2. Upload everything in this folder to the repository root, including `.nojekyll`.
3. Open **Settings > Pages**. Under **Build and deployment**, choose **Deploy from a branch**, pick `main` and `/ (root)`, then Save.
4. After a minute or two the site is at `https://YOUR-USERNAME.github.io/REPO-NAME/`.

## Add the video

Run `./tools/make-video.sh your-recording.mov` (needs ffmpeg), or send the recording to Claude to do it.
Keep `hero.mp4` under about 10 MB so it loads quickly on phones. GitHub rejects files over 100 MB.

## Add your story photos

The "Our story" prints sit to the left of the invitation on computers and become a swipeable row on phones.

1. Make a folder called `story` in the repository.
2. Add five portrait photos named `1.jpg` to `5.jpg`, in the order of the story. About 1000 px tall and under 300 KB each keeps phones fast.
3. Edit the years and captions in `index.html` (search for `[Year]`).

Until a photo is there, its frame shows a dusk-coloured card that says "Photo to come".

## Things to know

- The page is hidden from search engines (`noindex` in `index.html`). Anyone with the link can still open it.
- The RSVP form sends replies to a Google Sheet through a small Apps Script. Setup steps are in `apps-script/README.md`. Until the `ENDPOINT` line in `index.html` is filled in, or if the script cannot be reached, the form falls back to preparing an email to the `RSVP_EMAIL` address.
- Personal links end in `?g=CODE`. The page looks the code up in the sheet to greet the guest by first name.
- There are three versions, set by column I (Side) on the Guests tab: **Bride** shows the wedding in Darjeeling, **Groom** shows the reception in Gorubathan, **Both** shows both. The sheet adds `&s=bride` or `&s=groom` to the link, so the right version shows straight away. A link without a code works too, for example `?s=groom` to share in a group.
- Still to fill in for the versions: the parents' names in the opening line (search `index.html` for `[Jaya's parents]` and `[Pranup's parents]`), and the reception date, which also sets the groom's-side countdown (`RECEPTION` in `index.html`).
- The repository is public, so the address, venue and reply email in the source are public too.
- Still to fill in: the reception date, venue name and directions, and the story years (dashed underlines on the page).
- The countdown runs to 10 February 2027, 11:00 AM India time. After that it changes to a thank-you line.
- Arrival details typed into the RSVP form are saved at the start of the guest's note in the sheet, so the Apps Script needs no change.
