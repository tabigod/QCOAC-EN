# questcraft-Offline-account-creator 
  (本软件为AI生成，这里所有的代码可公开使用可二次开发)
用于在QuestCraft中创建离线账号，为那些没有马内购买正版的玩家提供离线账号的工具
 ![](/qcofa.png)

## 适用于 Quest, Pico, YVR，QIYU
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

理论上任何安卓设备都可以使用这种方法

## 如何实现
实现原理是修改 Android 目录中的 DemoMode 账户，从 [/data/user/0/com.qcxr.qcxr/files/accounts] 获取此文件（需要 Android root 权限）用户名可以是任意名称，但 UUID 可能需要特定值，将 DemoMode 改为 false 修改内容：
```bash
"isDemoMode": false,
"username": ""
"uuid": ""
```
完成这些更改后，该账户将作为离线账户使用。此外，[storage/emulated/0/Android/data/com.qcxr.qcxr/files/launcher.conf]中的文件需要修改，以便正确显示账户信息：
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
这样你就成功添加了账户。但请注意，如果你之前安装了游戏版本，则不需要连接互联网。账户只有在断开网络启动游戏时才会生效，如果你重新连接网络，账户将无法使用
# 如何使用它
下载首个发布的图形配置界面。下载并安装后，你可以自定义和编辑与演示账户相关的各种选项，包括演示模式切换。所有生成的文件都会在这个目录里。 /storage/emulated/0/Android/data/cn.qcofa.com/files/ questcraft_accounts文件夹里的所有JSON文件都在这里。 文件根目录里的launcher.conf文件也在这里。我已经更新了，启用了多个账户的支持
# 如何导入？
请使用 MT 文件管理器中的注入文件提供程序，将您已安装好的 QC 模块转换为注入文件提供程序的一个功能。有关详细信息，请参考此项目：[https://github.com/L-JINBIN/MTDataFilesProvider]

将您刚刚生成的 json 文件和 launcher.conf 文件放入各自的目录中

XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.json 导入
```bash
/data/user/0/com.qcxr.qcxr/files/accounts
```

launcher.conf 导入
```bash
/storage/emulated/0/Android/data/com.qcxr.qcxr/files/
```

如果你之前已经安装过任何版本，那么可以直接在断开网络连接的情况下启动游戏（如果你想在线或联机玩耍，之后可以重新连接网络）。如果你从未安装过任何版本，请先连接到互联网，然后再安装相应版本的游戏

