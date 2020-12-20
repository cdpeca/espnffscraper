# Welcome to espnffscraper 👋
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

> Fantasy Football scraper for ESPN leagues using ESPN APIs and generating some statistics

### 🏠 [Homepage](https://github.com/cdpeca/espnffscraper)

## Install
With Git:
```
git clone https://github.com/cdpeca/espnffscraper.git
cd espnffscraper
python3 setup.py install
```

## Usage

To utilize the program you will need your **league_id** and **year**. If you are using on private leagues you will also need two more parameters; your **swid** and **espn_s2** or **username** and **password**. To find your **swid** and **espn_s2** check out this [discussion](https://github.com/cwendt94/espn-api/discussions/150), from the creator of [espn-api](https://github.com/cwendt94/espn-api). A portion of this program is based on [espn-api](https://github.com/cwendt94/espn-api) (mostly the initial API URL constructor as it's abolustely wonderfully built). I would recommend to use credentials with your **swid** and **espn_s2** so it will work properly on both public and private leagues. This would also enable being able to use activity functions (although I haven't implemented that yet as this is really for some statiscal analysis).

```sh
python3 espnffscraper.py
```

As of now this will extract your league information and make all the league data available for you to access, analyze and manipulate how you want. Currently it will generate a couple of interesting statstical analysis plots...

- Win/Loss Margins for League by Regular and Playoff Seasons
- Lucky/Unlucky Wins and Losses for each team

It will also save the plots to high-resolution image files in a /plots folder which you can share with your league members to aid in trash-talking. :-)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

Feel free to check [issues page](https://github.com/cdpeca/espnffscraper/issues). 



## Show your support

Give a ⭐️ if this project helped you!


***
_This README tempale was initially generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_