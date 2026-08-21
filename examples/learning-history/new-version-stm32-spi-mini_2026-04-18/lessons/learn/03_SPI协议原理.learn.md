# 03 SPI 协议原理：为什么 SPI 用 4 根线换速度？

**建议用时**：12 分钟  
**学完你能做什么**：看懂 SPI 事务边界和 Mode 选择

---

## 1. 先猜一下

同样是 STM32 连接外设，I2C 只要 `SCL` + `SDA` 两根线，SPI 却要 `SCK`、`MOSI`、`MISO`、`CS` 四根线。

> 先别看解释，想 30 秒：SPI 多花两根线，到底买回了什么？

---

## 2. 一句话心智模型

**SPI 是“主机打拍子，两条单向数据线同时对传，再用 CS 圈住这一整句话”。**

I2C 像一条大家轮流说话的共享窄路，所以要地址、ACK、开漏上拉来避免冲突。SPI 像主机给每个从机点名：`CS` 拉低后，`SCK` 每跳一次，`MOSI` 发出 1 位，`MISO` 同时收回 1 位。它省掉了地址和 ACK，换来速度，但也把“有没有连对、数据对不对”的责任交给应用层。

---

## 3. 最小机制

只讲 3 件事：

1. **`CS/NSS` 决定这句话说给谁听**：低电平开始事务，高电平结束事务；中途拉高，从机通常会丢弃当前命令。
2. **`SCK` 是主机独占的节拍器**：从机不能像 I2C 那样拉住时钟等一等，所有字节都跟着主机时钟走。
3. **`MOSI` 和 `MISO` 同时移位**：所谓全双工，本质是主从两个移位寄存器首尾相连；你想读，也必须发占位字节来提供时钟。

---

## 4. 看一个最小例子

下面是读 W25Q32 Flash 的 JEDEC ID。它不是为了背代码，而是为了看清 SPI 的 3 个动作：`CS` 圈事务、`0x9F` 发命令、`0xFF` 换回数据。

```c
uint8_t tx[4] = {0x9F, 0xFF, 0xFF, 0xFF};
uint8_t rx[4] = {0};

HAL_GPIO_WritePin(FLASH_CS_GPIO_Port, FLASH_CS_Pin, GPIO_PIN_RESET);
HAL_SPI_TransmitReceive(&hspi1, tx, rx, sizeof(tx), 100);
HAL_GPIO_WritePin(FLASH_CS_GPIO_Port, FLASH_CS_Pin, GPIO_PIN_SET);

uint32_t jedec_id = ((uint32_t)rx[1] << 16) | (rx[2] << 8) | rx[3];
```

**三个关键锚点**：

| 锚点 | 为什么重要 | 写错会怎样 |
|------|------------|------------|
| `CS LOW -> SPI -> CS HIGH` | 从机用这一段低电平判断“一次完整事务” | 中途拉高会把命令拆断，从机重新等待新命令 |
| `0x9F` | W25Q32 的“读 JEDEC ID”命令 | 命令错了，后面读到的字节没有意义 |
| `0xFF` dummy bytes | 读数据也要主机继续发时钟 | 只发命令不继续移位，就没有 MISO 数据回来 |

---

## 5. 血的教训

常见错法：把“发命令”和“读数据”拆成两个 CS 事务。

```c
uint8_t cmd = 0x9F;
uint8_t id[3] = {0};

HAL_GPIO_WritePin(FLASH_CS_GPIO_Port, FLASH_CS_Pin, GPIO_PIN_RESET);
HAL_SPI_Transmit(&hspi1, &cmd, 1, 100);
HAL_GPIO_WritePin(FLASH_CS_GPIO_Port, FLASH_CS_Pin, GPIO_PIN_SET);

HAL_GPIO_WritePin(FLASH_CS_GPIO_Port, FLASH_CS_Pin, GPIO_PIN_RESET);
HAL_SPI_Receive(&hspi1, id, 3, 100);
HAL_GPIO_WritePin(FLASH_CS_GPIO_Port, FLASH_CS_Pin, GPIO_PIN_SET);
```

为什么错：第一次 `CS` 拉高后，W25Q32 认为“读 ID 事务结束了”；第二次 `CS` 拉低时，你没有再发 `0x9F`，它不会凭空知道你还想读 ID。

正确想法：**命令、地址、数据属于同一个 SPI 事务时，就必须被同一段 CS 低电平包住。**

---

## 6. 你来做

### 小题 1：补一步

如果你已经发出 `0x9F`，还想读回 3 个 ID 字节，为什么 `tx` 数组里还要放 3 个 `0xFF`？

**我的答案**：

（在这里写）

### 小题 2：换个场景

某个 SPI 传感器手册写着支持 `SPI Mode 3`。在 CubeMX 里你应该把 `Clock Polarity` 和 `Clock Phase` 分别配成什么？一句话说明判断依据。

**我的答案**：

（在这里写）

---

## 7. 80 字复述

不用术语堆砌，用自己的话说明：

> SPI 为什么要用 `CS`、`SCK`、`MOSI`、`MISO` 四根线？

**我的复述**：

（在这里写）

---

## 想继续深入？

- 看完整原理：`../deep/03_SPI协议原理.md`
- 做练习包：`../practice/03_SPI协议原理.practice.md`
- 生成互动页：参考 `../ai-source/06.0_图片显示原理.ai.md` 的 AI-source 写法
