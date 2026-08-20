# questcraft-offline-account-creator-EN
 Used for creating offline accounts in QuestCraft, providing offline accounts for players with no account
 ![main](/qcofa.png) [简体中文](README_ZH.md)
 
## Suitable For Quest, Pico, YVR，QIYU
[![Meat](https://custom-icon-badges.demolab.com/badge/Meta-0078D6.svg?logo=meta&logoColor=white
)](https://www.meta.com/)
[![Pico](https://custom-icon-badges.demolab.com/badge/Pico-000000.svg?logo=pico&logoColor=black
)](https://www.picoxr.com/)
[![YVR](https://custom-icon-badges.demolab.com/badge/玩出梦想-000000.svg?logo=yvr&https%3A%2F%2Fraw.githubusercontent.com%2Fxxx%2Fyvr-logo.svg&logoColor=white)](https://www.pfdm.cn/index)
[![QIYU](https://custom-icon-badges.demolab.com/badge/QIYU-28a745.svg?logo=QIYU&logoColor=white)](https://dev-qiyu.iqiyi.com/)

* [x] Quest 2/3/3s
* [x] Pico 3/4/4pro
* [x] YVR 1/2/PFD MR
* [x] QIYU Dream/700/MIX/Pro

Theoretically any Android device can use this method

## How to achieve it
The implementation principle involves modifying the Android directory the DemoMode account from the `/data/user/0/com.qcxr.qcxr/files/accounts` file. Root access is required. For Quest 2/3 rooting, see: https://github.com/Lumince/singularity (last incremental for Singularity to work: 52222680028100150, Jul 26th, 2026 build date). The username can be anything, but the UUID may require a specific value. Change the DemoMode value to false.
Modified content:
```bash
"isDemoMode": false,
"username": ""
"uuid": ""
```
After making these changes, it will function as an offline account, Additionally, the file in `storage/emulated/0/Android/data/com.qcxr.qcxr/files/launcher.conf`  needs to be modified so that the account information can be properly displayed:
```bash
{
"acceptedLegal": true,
"setDevMods": false,
"setCustomRAM": false,
"customRAMValue": "2048",
"lastSelectedInstance": 0,
"lastSelectedAccount": 0,
"accounts": [
{
"username": "34646",
"uuid": "6ef82f9f-e9b8-0440-56a9-6fdf5666b0d3"
}
]
}
```
In this way you have successfully added an account However please note that if you’ve previously installed the game version, you don’t need to be connected to the internet The account will only take effect when you start the game with the internet disconnected If you’re reconnected to the internet the account won’t function

# How to use it
Download the first released graphical configuration interface. After downloading and installing it, you can customize and edit various options related to the demo account, including the demo mode switch. All the generated files will be in the directory `/storage/emulated/0/Android/data/cn.qcofa.com/files/`
All JSON files in the questcraft_accounts folder are here.
The `launcher.conf` file in the files root directory is also here. I’ve updated it to enable support for multiple accounts

## How to import
Use the injection file provider of the mt file manager to convert your existing installed qc into a function of the injection file provider.
For details, please refer to this project.
[https://github.com/L-JINBIN/MTDataFilesProvider]

Place the json file you just generated and the launcher.conf file in their respective directories

XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.json import
```bash
/data/user/0/com.qcxr.qcxr/files/accounts
```

launcher.conf import
```bash
/storage/emulated/0/Android/data/com.qcxr.qcxr/files/
```

If you installed any version of Minecraft before this, you can simply start the game with the network disconnected (reconnect the network if you want to play online or on a server).
If you have never installed any version before, please install the version while connected to the internet first

