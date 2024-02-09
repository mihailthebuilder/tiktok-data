# Steps

Run `scp.sh` to copy chrome_profile directory.

Run `main.py` to copy files.

Run each bash file, can't get it to work.

Then SSH into server, do:

```bash
crontab -e
```

and add:

```bash
1 0 * * * docker run --rm tiktok-data
```
