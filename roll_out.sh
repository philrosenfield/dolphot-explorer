git add .
git commit -m "simple flask"
git push heroku master
heroku ps:scale web=1
heroku open
heroku logs --tail
