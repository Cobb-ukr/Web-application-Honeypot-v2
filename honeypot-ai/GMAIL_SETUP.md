# Gmail SMTP Setup Guide

## Quick Setup (5 Minutes)

The honeypot email alerts now use **Gmail SMTP** instead of SMTP2GO, so you don't need to wait for domain verification!

---

## Step 1: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Sign in with `testcyber7274@gmail.com`
3. Under "How you sign in to Google", click **2-Step Verification**
4. Follow the prompts to enable it (you'll need your phone)

---

## Step 2: Generate App Password

1. After enabling 2FA, go back to [Security Settings](https://myaccount.google.com/security)
2. Scroll down to "How you sign in to Google"
3. Click **App passwords** (you might need to sign in again)
4. In the "Select app" dropdown, choose **Mail**
5. In the "Select device" dropdown, choose **Other (Custom name)**
6. Type: `Honeypot System`
7. Click **Generate**
8. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)
   - Remove the spaces when you paste it: `abcdefghijklmnop`

---

## Step 3: Create .env File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and paste your app password:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=testcyber7274@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop
   
   SENDER_EMAIL=testcyber7274@gmail.com
   SENDER_NAME=Honeypot Security System
   RECEIVER_EMAIL=ashishroyblr@gmail.com
   ```

---

## Step 4: Test Email

1. Restart your honeypot server:
   ```bash
   uvicorn backend.main:app --reload
   ```

2. Test the email:
   ```bash
   curl -X POST http://localhost:8000/api/admin/test_email
   ```

3. Check `ashishroyblr@gmail.com` inbox for the test alert!

---

## Troubleshooting

### "Authentication failed" error
- Make sure you're using the **App Password**, not your regular Gmail password
- Remove spaces from the app password
- Verify 2FA is enabled

### "Less secure app access" message
- You don't need to enable "less secure apps" when using App Passwords
- App Passwords are the secure way to authenticate

### Email not arriving
- Check spam folder in `ashishroyblr@gmail.com`
- Verify the receiver email is correct in `.env`
- Check server logs for error messages

---

## Security Notes

✅ **Safe to use**: App Passwords are designed for this purpose
✅ **Revocable**: You can revoke the app password anytime from Google Account settings
✅ **No spam issues**: Gmail-to-Gmail emails rarely go to spam
✅ **Free**: No cost, no verification needed

---

## What Happens Next

Once configured, the honeypot will automatically send an email to `ashishroyblr@gmail.com` whenever:
- A new attacker session is detected
- Someone accesses the honeypot terminal

The email includes:
- Attacker's IP address
- Session ID
- Timestamp
- User agent
- Professional HTML formatting
