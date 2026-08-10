# LangGraph 私有状态传递

## 1. 什么是私有状态

LangGraph 中，并不是所有数据都必须定义在整个图的公共 State 中。

有些数据只需要在特定的几个节点之间传递，这种数据可以理解为 **私有状态（Private State）**。

例如：

```text
node_1
  │
  │ private_data
  ▼
node_2
  │
  │ a
  ▼
node_3
```

其中：

- `a`：整个图使用的公共状态
- `private_data`：只在 `node_1 → node_2` 之间传递的中间数据
- `node_3` 不需要，也看不到 `private_data`

注意：

> 这里的“私有”不是 Java 中 `private` 访问修饰符的意思，而是指局部节点之间使用的中间状态。

---

## 2. 核心代码

```python
from typing_extensions import TypedDict


# 整个图的公共状态
class OverallState(TypedDict):
    a: str


# node_1 产生的私有数据
class Node1Output(TypedDict):
    private_data: str


# node_2 需要读取的私有数据
class Node2Input(TypedDict):
    private_data: str


def node_1(state: OverallState) -> Node1Output:
    return {
        "private_data": "秘密中间数据"
    }


def node_2(state: Node2Input) -> OverallState:
    print(state["private_data"])

    return {
        "a": "处理完成"
    }


def node_3(state: OverallState) -> OverallState:
    # node_3 的输入 Schema 中没有 private_data
    print(state["a"])

    return {
        "a": "最终完成"
    }
```

---

## 3. 数据是怎么传递的

初始状态：

```python
{
    "a": "初始数据"
}
```

### node_1

输入类型：

```python
state: OverallState
```

所以 `node_1` 可以读取公共状态 `a`。

但是它返回：

```python
{
    "private_data": "秘密中间数据"
}
```

这个 `private_data` 是一个中间私有状态。

### node_2

`node_2` 定义为：

```python
def node_2(state: Node2Input)
```

而：

```python
class Node2Input(TypedDict):
    private_data: str
```

所以 `node_2` 可以获得 `node_1` 产生的 `private_data`。

然后 `node_2` 返回：

```python
{
    "a": "处理完成"
}
```

重新更新公共状态 `a`。

### node_3

`node_3` 定义为：

```python
def node_3(state: OverallState)
```

而 `OverallState` 中只有：

```python
a
```

因此 `node_3` 能读取公共状态 `a`，但不能通过自己的输入 State Schema 读取 `private_data`。

---

## 4. 最重要的理解

> **节点参数的 State Schema 决定这个节点能够读取哪些状态；节点输出 Schema 决定这个节点产生哪些状态。**

因此，可以通过给不同节点定义不同的 State Schema，让某些中间数据只在指定节点之间传递。

整体过程可以理解为：

```text
LangGraph 内部状态 / Channel
          │
          ▼
根据节点 Input Schema
筛选该节点能够读取的数据
          │
          ▼
       节点执行
          │
          ▼
节点返回新的状态更新
          │
          ▼
供后续需要这些字段的节点使用
```

---

## 5. 为什么需要私有状态

例如一个 Agent：

```text
用户问题
   │
   ▼
读取日志节点
   │
   │ raw_log
   ▼
分析日志节点
   │
   │ answer
   ▼
生成最终结果
```

`raw_log` 可能有几百行，只在：

```text
读取日志 → 分析日志
```

之间有用。

没有必要让后面的所有节点都读取它，也没有必要把它作为最终图输出。

所以可以把：

```python
raw_log
```

设计成私有状态。

---

## 一句话总结

> **公共 State 保存整个图关心的数据；私有 State 保存部分节点之间临时传递的中间数据。节点能看到哪些数据，主要由该节点声明的输入 State Schema 决定。**
