# Whisperer

### 有什么用？

作为一名心态良好的螺丝钉，每个礼拜在公司最重要的事情，当然是------写周报。毕竟很可能这是你跟Leader“维系感情”的唯一途径（好吧，其实实在是周报不知道写什么）。所以，写了这个CLI工具，可以辅助我们写出更加走心的周报，更好的面向Leader编程。

### 特性

* 自动创建并且打开一个md格式模板文件
* 提供commit关键数据（比如老子这周提交了多少多少个commit）
* 在末尾提供详细的commit表格
* 提供本周所贡献的代码行数

![](https://i.loli.net/2019/04/12/5cb0519cf149a.jpg)

### 使用方法

#### 1. 安装

```
pip install Whisperer
```

#### 2. 使用

```
wsp send leader@company.com
```

#### 3. 配置信息

这一步会交互式的提醒你输入一些必要的信息

#### 4. 发送

可能你需要再自己添加一些更加走心的内容，添加完毕之后在终端输入"YES",就可以发送成功了。

### 局限

* 目前只支持Gitlab
* 模板单一