if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://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@github.com/sittpaing123/IUBOT.git /IUBOT
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /IUBOT
fi
cd /IUBOT
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
