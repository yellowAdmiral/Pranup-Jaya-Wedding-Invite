# RSVP replies into Google Sheets

The invite page sends each reply to a small Google Apps Script that lives inside your guest-list sheet.
The same script tells the page who a personal link belongs to, so guest names stay in the sheet and out of this public repository.

## Set up (about 10 minutes, once)

1. Upload `Wedding Guest List.xlsx` to Google Drive and open it with Google Sheets.
2. On the **Setup** tab, paste your site address into the yellow cell B3, for example `https://yellowadmiral.github.io/Pranup-Jaya-Wedding-Invite/`.
3. In the sheet choose **Extensions > Apps Script**. Delete the sample code, paste in all of `Code.gs`, and click **Save**.
4. Click **Deploy > New deployment**. Next to "Select type" pick **Web app**, then set:
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Click **Deploy** and approve the permissions. Google may say the app is unverified. Choose **Advanced**, then **Go to (project name)**. This is your own script.
6. Copy the **Web app URL**.
7. In `index.html`, find `var ENDPOINT = '';` and paste the URL between the quotes. Commit the change.
8. Wait a minute for GitHub Pages to update, then open the personal link from row 2 of the Guests tab and send a test reply. It should appear on the **Replies** tab and column H should change to Yes or No. Delete the test row on Replies and clear H afterwards.

## Everyday use

- Type each household into the Guests tab (name in B, seats in C). The personal link, message and WhatsApp link fill in by themselves.
- Replies appear on the Replies tab. A guest who replies twice replaces their earlier answer.
- To get an email on every reply, put your address in `NOTIFY_EMAIL` at the top of `Code.gs`, then redeploy.

## If you change the script later

Editing `Code.gs` does nothing for guests until you redeploy: **Deploy > Manage deployments > pencil icon > Version: New version > Deploy**. The Web app URL stays the same.

## Good to know

- The Web app URL is visible in the page source. Anyone who has it could submit a reply or check a code, so keep codes private to each guest.
- If the script cannot be reached, the form shows the old email draft so no reply is lost.
