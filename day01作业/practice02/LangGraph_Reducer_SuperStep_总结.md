# LangGraph：Reducer 与 Super-step 问题总结

## 1. 核心问题

在 LangGraph 中，如果多个节点处于**同一个 super-step**，并且这些节点同时更新同一个 State 字段，例如：

```python
class State(TypedDict):
    step: int
```

多个并行节点都返回：

```python
return {"step": state["step"] + 1}
```

就会出现类似错误：

```text
InvalidUpdateError:
At key 'step': Can receive only one value per step.
Use an Annotated key to handle multiple values.
```

### 最重要的一句话

> **同一个 super-step 中，普通 State 字段不能被多个节点同时更新。**

如果多个并行节点都需要更新同一个字段，就需要使用 **Reducer** 来定义这些更新应该如何合并。

---

## 2. 为什么会出现这个问题

例如图结构：

```text
       node_1
      /
START ── node_3
      \
       node_4
```

`node_1`、`node_3`、`node_4` 会在同一个 super-step 中并行执行。

如果它们都更新：

```python
{"step": ...}
```

那么 LangGraph 会同时收到多个 `step` 新值。

如果 `step` 只是普通字段：

```python
step: int
```

LangGraph 不知道应该保留哪一个值，因此报错。

---

## 3. 不使用 Reducer 的情况

State：

```python
class State(TypedDict):
    step: int
```

节点可以写：

```python
return {
    "step": state["step"] + 1
}
```

这里表示：

> 计算出 `step` 的新值，然后直接覆盖原来的值。

这种写法适合类似下面的**串行结构**：

```text
node_1 → node_2 → node_3
```

因为同一个 super-step 中只有一个节点更新 `step`。

---

## 4. 使用 Reducer 的情况

如果存在并行节点，可以定义：

```python
from typing import Annotated
from typing_extensions import TypedDict
import operator

class State(TypedDict):
    step: Annotated[int, operator.add]
```

这里：

```python
operator.add
```

就是 Reducer。

它表示：

> 多个节点对 `step` 的更新通过加法进行合并。

这时节点更适合返回：

```python
return {
    "step": 1
}
```

例如三个并行节点分别返回：

```text
node_1 → 1
node_3 → 1
node_4 → 1
```

Reducer 自动合并：

```text
0 + 1 + 1 + 1 = 3
```

所以第一轮执行完成后：

```python
step = 3
```

---

## 5. 为什么不能再写 `state["step"] + 1`

如果已经使用：

```python
step: Annotated[int, operator.add]
```

但是节点仍然写：

```python
return {
    "step": state["step"] + 1
}
```

就会发生**重复累计**。

例如当前：

```text
step = 3
```

节点返回：

```text
3 + 1 = 4
```

Reducer 又会执行：

```text
3 + 4 = 7
```

所以结果可能出现：

```text
0 → 3 → 7 → 15
```

这不是 LangGraph 算错了，而是因为：

```text
节点自己先做了一次累加
+
Reducer 又做了一次累加
```

---

## 6. 两种写法对比

| State 定义 | 节点返回 | 含义 |
|---|---|---|
| `step: int` | `{"step": state["step"] + 1}` | 节点计算完整新值，直接覆盖 |
| `step: Annotated[int, operator.add]` | `{"step": 1}` | 节点只提交增量，由 Reducer 累加 |

---

## 7. 最终记忆

可以直接记住下面三句话：

1. **同一个 super-step 中，普通 State 字段不能被多个节点同时更新。**
2. **如果多个并行节点要更新同一个字段，就需要 Reducer。**
3. **使用 `operator.add` Reducer 时，节点通常返回“增量”，不要再返回 `state["step"] + 1`。**

例如：

```python
class State(TypedDict):
    step: Annotated[int, operator.add]
```

节点写：

```python
return {"step": 1}
```

即可让 LangGraph 自动完成累加。
