# Welcome to espnffscraper 👋
![Version](https://img.shields.io/badge/version-1.3.0-blue.svg?cacheSeconds=2592000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

> Fantasy Football scraper for ESPN leagues using ESPN APIs and generating some statistics for detailed analysis of your league

### 🏠 [Homepage](https://github.com/cdpeca/espnffscraper)

## Install
With `Git`:
```bash
git clone https://github.com/cdpeca/espnffscraper.git
cd espnffscraper
pip install -r requirements.txt
```

## Usage

To utilize the program you will need your **league_id** and **year**. If you are using on private leagues you will also need two more parameters; your **swid** and **espn_s2**. To find your **swid** and **espn_s2** check out this [discussion](https://github.com/cwendt94/espn-api/discussions/150), from the creator of [espn-api](https://github.com/cwendt94/espn-api). A portion of this program is based on [espn-api](https://github.com/cwendt94/espn-api) (mostly the initial API URL constructor as it's absolutely wonderfully built). I would recommend to use credentials with your **swid** and **espn_s2** so it will work properly on both public and private leagues.

If you will only run locally on your system update the required settings in `./settings/settings.py`

If you want to collaborate, contribute, share or host this in GitHub update the `./settings/settings_local.py` module instead. The `settings.py` will read the `settings_local.py` and override the variables. The `settings_local.py` will be excluded from version control and git.

You __must__ set the following settings/variables in order for this program to function...

```
league_id, year, league_open_to_public, swid (if private league), espn_s2 (if private league)
```

Once required settings are configured execute the program as follows in your local shell/terminal.

```bash
python3 espnffscraper.py
```

As of now this will extract your league information and make all the league data available for you to access, analyze and manipulate how you want. Currently it will generate a couple of interesting statstical analysis plots...

* Win/Loss Margins for League by Regular and Playoff Seasons
* Lucky/Unlucky Wins and Losses for each team
* _Relative Resuls_ to show how teams would have performed if they played every team every single week
    * This is useful to compare vs actual record to determine if someone is lucky based on the timing of their matchups

It will also save the plots to high-resolution image files in a /plots folder which you can share with your league members to aid in trash-talking. :-)

## Debugging

If you want to do some debugging it is very simple;  just execute as follows...

```bash
python3 espnffscraper.py --debug
```

This will output all of the dataframes as they are generated to the console so you can compare the data to what you see in your charts.
If you want to save `--debug` info to a file instead of outputting to the console, just pipe it into a file with one additional argument...

```bash
python3 espnffscraper.py --debug > <yourfilename>
```


## 🤝 Contributing

Contributions, issues and feature requests are welcome!

Feel free to check [issues page](https://github.com/cdpeca/espnffscraper/issues).

If you want to run in a virtual environment you can you use your prefereed virtual environment module, however the base repostiory provides __Poetry__ configurations with the included `pyproject.toml` and `poetry.lock` files. To use just run
```bash
poetry install
```
after you have cloned the repository. You can run the program in this virtaul environment by executing
```bash
poetry run python3 espnffscraper.py
```
The `--debug` will work as usual in the virtual environment as well.

## Show your support

Give a ⭐️ if this project helped you!


***
_This README tempale was initially generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_