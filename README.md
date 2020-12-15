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

You will need your **league** id and **year**. For private leagues you will also need two more parameters; your **swid** and **espn_s2** or **username** and **password**. To find your **swid** and **espn_s2** check out this [discussion](https://github.com/cwendt94/espn-api/discussions/150)! I would suggest to still login with your credentials even if your leage is public so that you will be ale to use the recent activity feature (not yet implemented).

```sh
python3 espnffscraper.py
```

As of now this will extract your league information and make available for you to access as you want. Currently it will generate a couple charts:
- Win/Loss Margins for League by Regular and Playoff Seasons
- Lucky/Unlucky Wins and Losses for each team




## 🤝 Contributing

Contributions, issues and feature requests are welcome!

Feel free to check [issues page](https://github.com/cdpeca/espnffscraper/issues). 



## Show your support

Give a ⭐️ if this project helped you!


***
_This README tempale was initially generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_