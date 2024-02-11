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
0 8 * * * docker run --rm tiktok-data
```

# Debug

Check the command ran:

```bash
grep tiktok /var/log/syslog
```

Check container logs:

```bash
docker ps
docker logs {container-id}
```
