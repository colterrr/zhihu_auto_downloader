# 知乎文章自动下载器

### 想法来源

之前在用这个[知乎文章下载器项目（by chenluda）](https://github.com/chenluda/zhihu-download)，但是我想下载的文章太多了懒得一个一个复制url而且还要从手机复制到电脑里，就自己写了个自动下载的版本

### 针对用户

- 喜欢把游览记录当作收藏夹的小朋友
- 喜欢文章只看一半，结果后来遇到“你好像来到了知识不存在的荒原”的小朋友
- 想下载的文章太多了的小朋友

### 使用

1. 电脑上：pip install mitmproxy
2. 电脑上：运行launch.bat
3. 手机上：下载mitmproxy证书
4. 手机上：配置代理（端口8080，或自行修改启动脚本launch.bat）
   - 或者使用成熟代理工具如shadowrocket（强烈建议）
   - 或者配置手机http代理（有时候抓不到包)
5. 在手机上游览知乎文章的时候程序会自动下载你看的文章到/download

### 注意事项

1. 要在历史记录里打开文章才能下载，在主页打开文章有概率响应截取不全

### 增加功能（服务器设备不在身边，检查是否下载成功）
运行check.py
访问[your server ip]:8001，查看全部下载内容和最近下载内容

### 附：mitmproxy证书下载（ios）

1. 在safari游览器中访问[http://mitm.it/](http://mitm.it/)进行证书安装

   ![img](readme_img/a3.png)
2. 设置证书的信任：设置 -> 通用-> VPN与设备管理 ->  mitmproxy，点击进行安装

   ![img](readme_img/a4.png)
   安装成功

   ![img](readme_img/a5.png)
3. 证书的信任开关在：通用 -> 关于本机 -> 下拉到 证书信任设置 -> 找到mitmproxy

   ![img](readme_img/a6.png)
4. 完成这些后mitmproxy工具就可以获取你的手机http请求进行处理了

### 附：手机网络http代理配置流程（ios）

1. 手机、电脑连同一wifi
2. 获取计算机ip（终端输入ipconfig）
3. 打开iphone设置 - wifi - i按钮

   ![img](readme_img/a1.png)
4. 找到里面http代理一栏，选择“手动”(使用完记得改回关闭)，并输入第2步获得的电脑ip和脚本端口号（脚本里设为8080）到“服务器”和“端口”，记得点“存储”保存
   ![img](readme_img/a2.png)