# Auto git pull 


```bash
$ chmod +x /root/negar_actions/run_auto_pull.sh

# Step 3: Edit crontab to run the script every 30 seconds
$ (crontab -l 2>/dev/null; echo "* * * * * /root/negar_actions/run_auto_pull.sh") | crontab -
$ (crontab -l 2>/dev/null; echo "* * * * * sleep 30 && /root/negar_actions/run_auto_pull.sh") | crontab -

# To verify your crontab entry:
$ crontab -l

```
