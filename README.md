# README

> Code for 2023华为软件精英挑战赛初赛

## Method

> 关于题目的思路

### V1

V1的目的在于熟悉代码，实现最基本的方法，即每个BOT从1~3号WORKBENCH中选择一个最能盈利的，不断重复购买。

要想实现上述要求，大致需要：
1. 初始化时读取地图的信息，确定所有BOT和WORKBENCH的坐标（但后续似乎用不到该功能，每一帧的输入包括了坐标信息，因此也可以忽略初始化阶段直接从每一帧的输入读取？）
2. 在不考虑碰撞损耗但考虑时间损耗的前提下，计算每个BOT最能盈利的WORKBENCH（即考虑初始利润和时间损耗）
3. 规划BOT的路线，同时在行进的过程中计算碰撞损耗

### v2

V2的目的在于实现基本的路径规划，目前需要实现H圈和贪心算法。

要想实现上述要求，大致需要：
1. 初始化时构造每个工作台所指向的下一个工作台，从而形成路径规划
2. 根据工作台的指向实现运动，并尽可能减少碰撞和卡墙情况
3. 根据一定的策略优化所得到的H圈，例如贪心算法等

### v3

解决死锁问题，并根据地图进行参数优化

## Tips

> 一些需要注意的事情

### 编译
- 参赛选手的源码打包脚本为 CodeCraft_zip.sh
  `sudo sh CodeCraft_zip.sh main.py`

- 执行机系统环境：
  - 操作系统版本：基于 x86 的 ubuntu 18.04
  - CPU：2 核可用 CPU
  - 内存：3.8 GB 可用内存
- 系统支持python3.7.3版本，请在该版本下进行源码开发
- 除numpy外，不允许引用其他第三方库
- 参赛选手提交的源码会在系统上直接运行，因此请保证main.py在一级目录下，不可修改该文件名称
- 压缩包中不能带有任何运行时调用的文件，包括可执行程序、动态库、数据表。平台在运行选手程序之前会清理所有文件，只保留最终程序,故运行时对
压缩包中的文件调用均会失败
- 上传源码压缩包中所包含的目录不得含有以下合法字符集以外的任何字符；目录名合法的命名字符集：英文大写字母”A-Z”、英文小写字母”a-z”、数
字”0-9”、 英文短横线“-”、 英文下划线”_”、英文加号”+”
- 上传到源码压缩包中所包含的文件名不得含有以下合法字符集以外的任何字符，且“.”符号不得连续出现；
文件名合法的命名字符集：英文大写字母”A-Z”、英文小写字母”a-z”、数字”0-9”、 英文短横线“-”、英文下划线”_”、英文点”.” 、英文加
号”+”
- 选手程序的编译运行均在linux下，选手提交前可尝试在linux平台下编译成功，以免造成编译失败
- 经过编译后的选手程序（python的程序文件）没有写权限，选手提交代码前应去掉写操作，否则会造成运行失败

### Git Workflow

#### 新建分支

1. 克隆远程仓库 `git clone https://github.com/MOr1s2/HW-Preliminary.git`
2. 创建新的分支 `git branch <branchname>`
3. 切换到新的分支 `git checkout <branchname>`
4. 将新的分支推送到远程 `git push origin <branchname>`

#### 同步主分支与个人分支

1. 切换到个人分支 `git checkout <branchname>`
2. 同步主分支 `git pull origin main`

#### 提交代码

1. 查看代码修改情况 `git status`
2. 选择需要提交的代码 `git add <filename>`
3. 对本次提交进行描述 `git commit -m 'Add/Update/Delete xxx and rename xxx to xx'`
4. 提交到远程分支 `git push origin <branchname>`
5. 切换到主分支 `git checkout main`
6. 更新主分支 `git pull origin main`
7. 合并到主分支 `git merge <branchname>`
8. 提交到远程主分支 `git push`
