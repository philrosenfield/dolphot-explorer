# DOLPHOT Explorer

This is a bokeh app made to run on a heroku server: [https://dolphot-explorer.herokuapp.com/dolphot-explorer](https://dolphot-explorer.herokuapp.com/dolphot-explorer)

# Run locally
    bokeh serve --show dolphot-explorer.py
## Use your own FITS binary table
   serve --show dolphot-explorer.py --args [path to fits file]

# Deploy on a heroku
- Start by following directions [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)
- After [creating the app on the Heroku servers](https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app) (```heroku create```) edit the name of the app in the ```Procfile``` from
      --allow-websocket-origin=dolphot-explorer.herokuapp.com
  to

      --allow-websocket-origin=[name of your app].herokuapp.com
- ```$ pipenv install``` will create the needed Pipfile.lock
- commit and push your changes
  ```
    $ git add [files]
    $ git commit -m [message]
    $ git push heroku master
  ```
- Your app should deploy on [name of your app].herokuapp.com
