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

To utilize the program you will need your **league_id** and **year**. If you are using on private leagues you will also need two more parameters; your **swid** and **espn_s2** or **username** and **password**. To find your **swid** and **espn_s2** check out this [discussion](https://github.com/cwendt94/espn-api/discussions/150), from the creator of [espn-api](https://github.com/cwendt94/espn-api). A portion of this program is based on [espn-api](https://github.com/cwendt94/espn-api) (mostly the initial API URL constructor as it's abolustely wonderfully built). I would recommend to use credentials with your **swid** and **espn_s2** so it will work properly on both public and private leagues. This would also enable being able to use activity functions (although I haven't implemented that yet as this is really for some statiscal analysis).

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



## Show your support

Give a ⭐️ if this project helped you!


***
_This README tempale was initially generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_