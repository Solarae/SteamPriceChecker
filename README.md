# Steam Price Checker

A CL program used to check the current and historically lowest retail price of a Steam game. Users can also set a price threshold for games such that they will be notified via email when the game's price falls below the given threshold.

## Getting Started

### Prerequisites

- requests
- tabulate

### Usage

To check the current and historically lowest price of a game, and setup an alarm system, run the following
```bash
python3 price_checker.py
```

Setup a CRON job using the following script to receive notifications
```bash
python3 notification.py
```

## Learn More

To learn how to setup a CRON job on Mac/Linux use the following resource:

- [Schedule Python Scripts on Mac/Linux](https://www.youtube.com/watch?v=5bTkiV_Aadc) 

## Contact

Email: [ronnie.chen.rc@gmail.com](ronnie.chen.rc@gmail.com)

Project Link: [https://github.com/Solarae/SteamPriceChecker](https://github.com/Solarae/SteamPriceChecker)
