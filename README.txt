!!! WARNING !!!

0. You are responsible for running this script or editing it. If your account gets banned because of this script or any modifications you made to it. Your're at fault.
1. You can only run one version of this script at a time (like how you can only play one game at a time using Steam)

-----

~ Prerequisites ~
- Python ver. 3.12.4 (or any ver that'll work with psutil)
- pip install psutil
- appid and process_name NEED to be set in the config file otherwise the script wont run

-----

~ About Steam API Link Script ~
: "steam_api_link.py" the script you run

This script is meant to sync play time from a different / incompatible version of a game (the one you're playing or want to play) to your owned Steam account's version of the game.

Meaning your time will be tracked on Steam even though it wouldn't normally be.

This is for games / versions of games cant be ran through Steam whatsoever but still has a version ON the Steam platform. whether thats the latest version or a remastered blah blah blah.

For example; running this script with "Steam_config.json" set to Final Fantasy XIV Online's appid and correct process_name, will allow Steam to think
you're running the game and start tracking time.

But, this does not actually run the game that you own on Steam. Just makes Steam and your Friends think you are playing.

    Note 1: This script doesn't start working with the SteamWorks API until it finds the process_name running.
    Note 2: This script stops running when it initially finds the game running BUT can no longer find the game running. -
    Meaning you opened the game. The script found the game running and initializes the API. BUT, then, (after some play time hopefully) you either closed the game or it crashed -
    so the script notices that and closes.

This was originally meant to be used as a way to play non-steam games with Steam Overlay API but it doesn't work unless baked into the game

-----

~ About Steam Config Json File ~
: "steam_config.json"

1. "appid" must be from a OWNED and a INSTALLED game from your library, it also cannot be a generated appid for a non-steam game. (it does not work otherwise)
    Note: The reason it must be owned and installed is its technically "running the game", if it tries while its uninstalled it'll install it or if not bought, bring you to a store page -
    or who knows, maybe an error. i don't have a full idea here
    
    you can search for a game here to get a appid (https://steamdb.info/)
        OR
    right click the game in your Steam Library and click on "Properties", then click on "Updates" and near the bottom will be this > App ID: XXXXXXXX

2. "process_name" is the full name of the final ran executable-file OR the executable-file you're using (or a launcher is using) to actually play the game. No Launcher Files. 
    for ex.: "ffxiv_dx11.exe", "Terraria.exe", "witcher3.exe"

3. (optional) You can set the executable to the full-filepath of what external game / launcher you want to play / use
    Note 1: This will be ran first before everything else
    Note 2: This does not need to be set in the config file.
    ex.: "B:\\SteamLibrary\\Steamapps\\common\\FFXIV\\boot\\ffxivboot.exe" (this starts the FFXIV launcher, which sadly is required)