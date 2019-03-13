# OS-simulator

![](http://ww1.sinaimg.cn/large/006giLD5ly1g11any1rpgg31fw0mn1kx.gif)

使用 PyQt5 实现的操作系统**模拟**软件，具有操作系统的基本功能：**进程管理、内存管理、文件管理、设备管理**

允许创建、删除、修改和保存伪指令程序文件，手动控制程序的提交和执行

图形界面展示**多道程序并发执行**的过程，可视化系统内存动态分配情况，实时统计并显示系统当前运行状态信息

内存管理上仿照虚拟内存的工作机制进行按需调页分配和管理，其中页面置换采用 LRU 算法

长期调度采用 FCFS 算法，短期调度采用基于时间片的动态优先级调度算法，结合 aging scheduling 实现

## 主要模块

![](http://ww1.sinaimg.cn/large/006giLD5gy1g11c688n82j30v00lx0uf.jpg)

- ### pcb.py

  进程控制模块，是整个系统的核心数据结构之一，集合所有的进程信息，包括：

  - `self.name`: 进程别名，来自于作业名
  - `self.pid`: 进程的PID，每个进程唯一
  - `self.prioroty` : 进程优先权值，与具体的作业调度算法和进程调度算法有关 
  - `self.status` :  进程状态，有 "new"，"ready"，"running"， "suspended"（waiting），"terminated"
  - `self.address` : 进程内存地址，使用该对象实例的内存地址来模拟表示
  - `self.age` : 进程年龄，与具体的进程调度算法有关
  - `self.pc` : 程序计数器，即接着要运行的指令地址
  - `self.codes` : 程序伪指令，与 code.py 有关，是一个列表，包含所有将要执行的伪指令对象
  - `self.page_table` : 进程的页表，字典结构，页号 : 页表项，页表项的具体结构见 memory.py
  - `self.references` : 访问内存次数
  - `self.page_faults` : 缺页次数，缺页率 = 缺页次数 / 访问内存次数
  - `self.required_memory` : 进程占用的内存大小
  - `self.io_type` : IO 类型，有 "read file"，"write file"，"keyboard"，"printer"
  - `self.io_status` :  IO 状态，有 "complete", "running"

- ### pool.py

  一共有五个 pool，分别是 JobPool、TerminatedPool、SuspendPool 和 ReadyPool，以及一个未在图形界面上显示的 IOCompletedPool，这五个 pool 分别对应进程的不同状态，具体为：

  `JobPool` —— new；

  `ReadyPool` —— ready，running；

  `SuspendPool` —— waiting，IO状态为 running；

  `TerminatedPool` —— terminated；

  `IOCompletedPool` —— waiting，IO状态为 complete；

  由于模拟的是**单核CPU**，因此处于 running 的进程永远只有一个，不可能同时存在两个 running 的进程。因此为了图形界面的简洁，没有特意设计 `RunningPoo`，而是把处于 running 的进程显示在了 `ReadyPool` 中，可通过表格的 “状态” 列区分。为了更加显眼，特意把处于 running 的进程用蓝色标出。

  同样为了界面的简洁，把 IO 状态为 complete 和 running 的 waiting 进程都显示在了 `SuspendPool`  中，可通过表格的 “IO 状态” 列区分。这里可能有个令人费解的地方：waiting 进程 IO 结束后不应该进入 `ReadyPool`，成为 ready 进程吗？怎么还是 waiting 进程且特意用 IO “complete” 去标识呢？其实这只是 IO complete 的进程在进入 `ReadyPool` 之前的一个中间态罢了，长期调度算法优先考虑 IO complete 的进程而不是刚进入 `JobPool` 的作业。

- ### schedule.py

  `长期调度`（作业调度）和`短期调度`（进程调度）模块。长期调度采用 `FCFS 算法`，短期调度采用基于时间片的`动态优先级调度算法`，结合 `aging scheduling` 实现。两个调度算法均继承了 QThread。

  长期调度把作业由 `JobPool`  转入 `ReadyPool` 参与短期调度，即 new 进程转为 ready 进程。当 `IOCompletedPool` 中有进程时，优先把 `IOCompletedPool` 中的进程转入 `ReadyPool` 参与短期调度，即 IO complete 的 waiting 进程转为 ready 进程。

  短期调度在时间片（CPU_PROCESS_TIME）到来时，选择优先权值最小的进程分配 CPU ，即由 ready 进程转为 running 进程。分配到 CPU 的进程 age 变为 0，且优先权值 + PRIORITY_ADD_EACH_TERN；而其他 ready 进程 age + 1，优先权值 - AGING_TABLE[age ]。这些变量都可在 settings.py 中自定义。

- ### memory.py

  内存管理模块，仿照虚拟内存的工作机制进行按需调页分配和管理，其中页面置换采用 `LRU 算法`。

  `页表项（PTE）`是页表的主要数据结构，其中包含对应的帧页（frame），最近访问的时间（recent_access_time）以及有效位（valid_bit）

- ### code.py

  ![](http://ww1.sinaimg.cn/large/006giLD5gy1g11k1o5cd1j30sh0emwey.jpg)

  TimeThread 类模拟代码执行时长的计时器，继承了 QThread，使用 QTimer 进行计时。Code 作为一个抽象基类，派生了 IO、C、Q 三种类型的伪指令，而 IO 又派生出 P、K、R、W 四种伪指令。各个简单伪指令的详细解释如下表格所示：

  | 伪指令 | 功能     | 参数                                             |
  | ------ | -------- | ------------------------------------------------ |
  | C      | 算术运算 | arg1：执行时间；arg2：指令所处页号               |
  | Q      | 退出程序 | arg1：指令所处页号                               |
  | P      | 打印操作 | arg1：执行时间；arg2：指令所处页号               |
  | K      | 键盘输入 | arg1：执行时间；arg2：指令所处页号               |
  | R      | 读取文件 | arg1：文件名；arg2：执行时间；arg3：指令所处页号 |
  | W      | 写入文件 | arg1：文件名；arg2：执行时间；arg3：指令所处页号 |

- ### file.py

  文件管理模块，使用简单的单链表完成，允许创建、删除、修改和保存伪指令程序文件，手动控制程序的提交和执行

## 使用方式

```
git clone https://github.com/Hk4Fun/OS-simulator.git
cd OS-simulator
pip install pipenv
pipenv install
pipenv shell
python main.py
```