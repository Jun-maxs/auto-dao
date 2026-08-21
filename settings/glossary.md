# 术语表 (Glossary)

> `concept_tag` ↔ 中文关键词 ↔ 术语定义 三者的权威映射源。
> **1:1:1 原则**：每个 `concept_tag` 唯一对应一个中文关键词与一条术语定义，严格对齐。
> 设计依据：`docs/plans/2026-04-18-thinking-module-and-concept-graph-design.md` §四、§附录 B。

---

## 列定义

| 列 | 含义 | 格式示例 |
|---|------|---------|
| **concept_tag** | 机器可读 slug；lesson 元信息 / `learner_model.concept_mastery` / prereq-map 均以它为键 | `stm32-eeprom-page-wrap` |
| **中文关键词** | 学习者可见的自然语言短词；思考模块中以反引号包裹使用 | `卷绕机制` |
| **英文** | 英文标准名或学科通用英文表达 | `page wrap` |
| **定义** | 一句话术语解释（避免长段落，详细讲解放 lesson 正文） | `EEPROM 超出页大小时数据覆盖页首` |
| **首次出现** | 主题名 · Lesson 编号；跨主题重复以最早一次为准 | `STM32 · Lesson 3` |

> `concept_tag` 命名格式为 `{topic}-{concept-name}`，全小写、连字符分隔；规范见 `.claude/skills/learning-engine/SKILL.md §4.1 第 6 步`。
> 历史遗留条目若暂无 `concept_tag`，允许填 `—`（与 §九 Q7 决策一致：不强制回填旧 session）。

---

## 数学 (Mathematics)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| — | 函数 | Function | 描述输入与输出之间的对应关系 | 一元函数微分学 |
| — | 导数 | Derivative | 描述函数在某点的瞬时变化率 | 一元函数微分学 |

---

## 心理学 (Psychology)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|

---

## 哲学 (Philosophy)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|

---

## 计算机科学 / 嵌入式 (Computer Science / Embedded)

### I2C 协议（来自 STM32 通信总线专题 · Lesson 02.0）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| i2c-bus-basics | I2C 总线 | I2C (Inter-Integrated Circuit) | Philips 开发的两线制串行总线，多主多从、引脚少、可扩展 | STM32 · Lesson 02.0 |
| i2c-sda-scl | SDA / SCL | SDA / SCL | I2C 的双向数据线 / 主机产生的时钟线 | STM32 · Lesson 02.0 |
| i2c-open-drain-pullup | 开漏+上拉 | open-drain + pull-up | 设备只能下拉/悬空 + 外部上拉电阻；实现线与逻辑，防电气冲突 | STM32 · Lesson 02.0 |
| i2c-master-slave | 主从架构 | master/slave | 任一时刻一个主机控制 SCL，从机响应地址匹配的请求 | STM32 · Lesson 02.0 |
| i2c-7bit-address | 7 位地址 | 7-bit address | I2C 标准设备地址宽度；左移 1 位后拼 R/W 组成 8 位地址字节 | STM32 · Lesson 02.0 |
| i2c-rw-bit | R/W 读写位 | R/W bit | I2C 地址字节的最低位；0 = 写、1 = 读 | STM32 · Lesson 02.0 |
| i2c-start-stop-signal | 起始/停止信号 | Start / Stop condition | SCL 高期间 SDA 跳变（起始=高→低、停止=低→高）；数据流中不可能出现 | STM32 · Lesson 02.0 |
| i2c-ack-nack | ACK / NACK | ACK / NACK | 第 9 时钟接收端控制 SDA；低 = ACK（继续传）、高 = NACK（结束传） | STM32 · Lesson 02.0 |
| i2c-data-validity | 数据有效性 | data validity | SCL 高期间 SDA 必须稳定；SCL 低时允许切换 | STM32 · Lesson 02.0 |
| i2c-transfer-modes | 三种传输模式 | transfer modes | 标准 100 kbit/s、快速 400 kbit/s、高速 3.4 Mbit/s | STM32 · Lesson 02.0 |
| i2c-compound-rw | 复合读写 | combined format (repeated start) | `S` + `Sr` 两次起始信号——先写寄存器地址（设指针）、`Sr` 不释放总线直接读/写内容；`Sr` 保证事务原子性 | STM32 · Lesson 02.0 |
| i2c-repeated-start | 复始信号 `Sr` | Repeated Start (Sr) | 与 START 电气时序相同的第二次起始信号，但**不释放总线**；是复合读写原子性的物理基础（NXP UM10204 规范） | STM32 · Lesson 02.0 |

### I2C HAL 抽象 & 外设实战（来自 STM32 通信总线专题 · Lesson 02.1）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| i2c-hal-api-abstraction | HAL I2C 抽象 | HAL I2C Abstraction | STM32 HAL 层对 I2C 外设的统一封装；`MX_I2C1_Init` + `hi2c1` + `HAL_I2C_*` API | STM32 · Lesson 02.1 |
| hal-i2c-handle | HAL I2C 句柄 | HAL I2C Handle | `I2C_HandleTypeDef hi2c1`，所有 HAL I2C API 的第 1 个参数；封装硬件寄存器 + DMA + 错误码 | STM32 · Lesson 02.1 |
| hal-i2c-mem-write-read | `HAL_I2C_Mem_Write/Read` | HAL I2C Memory Read/Write | 带寄存器地址的读写 API；`Mem_Read` 内置复合读写（`S` + `Sr`），对应 02.0 §3.8 | STM32 · Lesson 02.1 |
| hal-i2c-master-transmit-receive | `HAL_I2C_Master_Transmit/Receive` | HAL I2C Master Transmit/Receive | 纯字节流读写 API，无寄存器地址概念；适合 OLED 刷屏、AHT20 命令等 | STM32 · Lesson 02.1 |
| i2c-7bit-vs-8bit-address-in-hal | HAL 的 8 位地址约定 | 8-bit DevAddress Convention | HAL 的 `DevAddress` 要求已左移 1 位的 8 位字节；HAL **不代做移位**，`I2C_7BIT_ADD_WRITE/READ` 宏只调整 bit[0] | STM32 · Lesson 02.1 |
| i2c-api-selection-tree | I2C API 三分类决策 | I2C API Selection (3-class) | 按通信语义分类选 API：A 类存储空间 → `Mem_*`；B 类命令序列 → `Master_Transmit`；C 类数据流 → `Master_Receive` | STM32 · Lesson 02.1 |
| eeprom-page-write-boundary | EEPROM 页边界 | EEPROM Page Write Boundary | AT24C02 页大小 = 8 字节；单次写入跨页会**回卷**到本页起始覆盖原数据，HAL 不保护 | STM32 · Lesson 02.1 |
| eeprom-write-cycle-delay | EEPROM 写周期延迟 | EEPROM Write Cycle Delay (Twr) | AT24C02 擦写周期 ≈ 5 ms；期间芯片对任何 I2C 命令 NACK，代码须 `HAL_Delay(5)` | STM32 · Lesson 02.1 |
| oled-control-byte-co-dc | OLED 控制字节 | OLED Control Byte (Co / DC#) | SSD1306 特有协议加层；`0x00` = 后续命令流、`0x40` = 后续显存数据流 | STM32 · Lesson 02.1 |
| aht20-trigger-measure-command | AHT20 触发测量命令 | AHT20 Trigger Measure Command | 3 字节固定序列 `0xAC 0x33 0x00`，启动一次温湿度 ADC 采样 | STM32 · Lesson 02.1 |
| aht20-status-busy-bit | AHT20 busy 状态位 | AHT20 Status Busy Bit | 状态字节 bit[7]：1 = 仍在测量、0 = 完成可读；不轮询直接读得到旧数据 | STM32 · Lesson 02.1 |
| aht20-single-transaction-7byte | AHT20 单事务 7 字节读 | AHT20 Single-Transaction 7-Byte Read | 一次 `Master_Receive` 读 7 字节 = 状态(1) + 数据(5) + CRC(1)；比两次独立读高效且一并取 CRC | STM32 · Lesson 02.1 |
| crc8-aht20 | CRC-8 (AHT20) | CRC-8 Polynomial 0x31 | 多项式 `x^8+x^5+x^4+1`（0x31），初值 0xFF；AHT20 用它校验 6 字节测量数据 | STM32 · Lesson 02.1 |
| apb1-clock-i2c-lower-bound | APB1 时钟 I2C 下限 | APB1 Clock I2C Lower Bound | RM0008 §26.3.3：I2C 100 kHz 要求 APB1 ≥ 2 MHz、400 kHz 要求 ≥ 4 MHz；低于下限会静默失败 | STM32 · Lesson 02.1 |
| i2c-logic-analyzer-verification | 逻辑分析仪验证 | Logic Analyzer Verification | 用 Saleae Logic 等工具抓 SDA/SCL 波形，把 HAL 调用与实际时序对齐，排查 I2C 问题首选手段 | STM32 · Lesson 02.1 |

### SPI 协议（来自 STM32 通信总线专题 · Lesson 03.0）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| spi-bus-basics | SPI 总线 | SPI (Serial Peripheral Interface) | Motorola 推出的同步全双工串行总线；主从架构 + 硬片选 + 推挽驱动；以速度见长 | STM32 · Lesson 03.0 |
| spi-4wire-physical | 4 线物理层 | 4-wire Physical Layer | `SCK` + `MOSI` + `MISO` + `NSS` 四根线；每多 1 从机再加 1 根 NSS | STM32 · Lesson 03.0 |
| spi-push-pull-driver | 推挽驱动 | Push-Pull Driver | MOS 管硬驱动 0/1，边沿陡，高速下不受 RC 电路拖慢；与 I2C 开漏上拉成镜像对照 | STM32 · Lesson 03.0 |
| spi-full-duplex-shift-register | 全双工移位寄存器对传 | Full-Duplex Shift-Register Exchange | 主从各一个 8 位移位寄存器，通过 MOSI/MISO 首尾相连成 16 位环；每个 SCK 沿收发同时发生 | STM32 · Lesson 03.0 |
| spi-sck-master-generated | SCK 主机独占时钟 | Master-Generated SCK | SCK 只能由主机产生，从机不能时钟拉伸（推挽物理决定） | STM32 · Lesson 03.0 |
| spi-cpol-cpha-modes | CPOL/CPHA 四模式 | CPOL/CPHA 4 Modes | CPOL（空闲电平 0/1）+ CPHA（采样沿位置 0/1），2×2=Mode 0/1/2/3；70% 外设是 Mode 0 | STM32 · Lesson 03.0 |
| spi-nss-hw-vs-sw | NSS 硬/软片选 | NSS Hardware vs Software | 硬件 NSS 只能 1 根；**99% 项目用 `NSS_SOFT` + 普通 GPIO**，多从机零成本扩展 | STM32 · Lesson 03.0 |
| spi-multi-slave-topology | 多从机拓扑 | Multi-Slave Topology | 星型（独立 CS，推荐）vs 菊花链（共享 CS，罕见） | STM32 · Lesson 03.0 |
| spi-data-bit-width | 数据位宽 8/16 | Data Bit Width 8/16 | STM32 SPI 支持 8 或 16 位为一次移位单位；通用外设用 8 位 | STM32 · Lesson 03.0 |
| spi-stm32f103-baudrate | STM32F103 SPI 速率上限 | STM32F103 SPI Baudrate Ceiling | SPI1 最高 36Mb/s（APB2/2）、SPI2/3 最高 18Mb/s（APB1/2）；实战常用 18Mbit/s 折中 | STM32 · Lesson 03.0 |
| spi-no-ack-design | 无 ACK 设计 | No-ACK Design | SPI 取消了 I2C 的 ACK 机制以提速；错了没反馈，数据正确性由应用层自保（读 ID / 回读 / CRC） | STM32 · Lesson 03.0 |

### SPI HAL 抽象 & W25Q32 Flash 实战（来自 STM32 通信总线专题 · Lesson 03.1）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| spi-hal-api-abstraction | HAL SPI 抽象 | HAL SPI Abstraction | STM32 HAL 层对 SPI 外设的统一封装；`MX_SPI1_Init` + `hspi1` + `HAL_SPI_*` API | STM32 · Lesson 03.1 |
| hal-spi-handle | HAL SPI 句柄 | HAL SPI Handle | `SPI_HandleTypeDef hspi1`，所有 HAL SPI API 的第 1 参数；封装硬件寄存器 + DMA + 错误码 | STM32 · Lesson 03.1 |
| hal-spi-transmit-receive-trio | `HAL_SPI_Transmit/Receive/TransmitReceive` | HAL SPI Transmit/Receive/TransmitReceive Trio | 3 个数据传输 API；底层都是 TransmitReceive，Transmit/Receive 是"阉割视图"——前者丢 MISO、后者 MOSI 填 0xFF | STM32 · Lesson 03.1 |
| spi-cs-software-control | CS 软控骨架 | CS Software Control Skeleton | `CS_LOW → SPI API × N → CS_HIGH` 通用事务模板；CS 必须包裹整个事务 | STM32 · Lesson 03.1 |
| w25q32-jedec-id-handshake | W25Q32 JEDEC ID 握手 | W25Q32 JEDEC ID Handshake | 开机读 `0x9F` 验证 = `0xEF4016` 确认芯片型号；无 ACK 设计下唯一连通性校验 | STM32 · Lesson 03.1 |
| w25q32-page-program | W25Q32 页写 | W25Q32 Page Program | `0x02` + 3B 地址 + ≤256B 数据，全部在一个 CS 事务里 | STM32 · Lesson 03.1 |
| w25q32-write-enable-latch | W25Q32 写使能锁存 | W25Q32 Write Enable Latch (WEL) | WEL 位每次写/擦后硬件自动清零，需先发 `0x06` 重置；芯片厂家的防误写设计 | STM32 · Lesson 03.1 |
| w25q32-busy-polling | W25Q32 BUSY 轮询 | W25Q32 BUSY Polling | 读 `0x05` 的 bit[0]，等它清零确认操作完成；不能用 `HAL_Delay` 代替 | STM32 · Lesson 03.1 |
| w25q32-sector-erase | W25Q32 扇区擦除 | W25Q32 Sector Erase (4KB) | `0x20` + 3B 地址，擦除 4KB 扇区回到 `0xFF`；典型 ~45ms | STM32 · Lesson 03.1 |
| w25q32-page-boundary-wrap | W25Q32 页边界卷绕 | W25Q32 Page Boundary Wrap | 单次 Page Program 跨页会回卷到本页开头覆盖原数据；硬件约束 | STM32 · Lesson 03.1 |
| w25q32-erase-before-write-rule | 写前必擦三原则 | Erase-Before-Write Triple Rule | Flash 物理只能 1→0，所以 (1) 写前擦；(2) 写后等 BUSY；(3) 单次页写不能跨页 | STM32 · Lesson 03.1 |

### CAN 总线协议（来自 STM32 通信总线专题 · Lesson 04.0）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| can-broadcast-network | CAN 广播网络 | CAN Broadcast Network | 对等总线型结构，无主从，基于 "ID 主题 + 硬件过滤" 的订阅模型 | STM32 · Lesson 04.0 |
| can-differential-signal | CAN 差分信号 | CAN Differential Signal | CAN_H/CAN_L 两线反向摆动；接收端做减法消除共模噪声 | STM32 · Lesson 04.0 |
| can-dominant-recessive | 显性/隐性电平 | CAN Dominant/Recessive | 显性=0=2V 压差=强驱动；隐性=1=0V 压差=浮空 | STM32 · Lesson 04.0 |
| can-wired-and-inverse | 线与反向版 | Wired-AND Inverse | 任一节点发显性→总线显性（反于 I2C 的低电平压倒高电平） | STM32 · Lesson 04.0 |
| can-id-arbitration | CAN ID 仲裁 | CAN ID Arbitration | 按 ID 逐位比对，小 ID 先赢；非破坏性 0 冲突 | STM32 · Lesson 04.0 |
| can-frame-structure | CAN 标准帧结构 | CAN Standard Frame Structure | SOF+ID+RTR+IDE+r0+DLC+Data+CRC+ACK+EOF | STM32 · Lesson 04.0 |
| can-dlc-8byte-limit | CAN 8 字节数据上限 | CAN 8-Byte DLC Limit | 单帧数据 ≤8B；保证短帧高优先级抢占总线 | STM32 · Lesson 04.0 |
| can-bit-timing-segments | CAN 位定时四段 | CAN Bit Timing Segments | SS+PropSeg+PS1+PS2，每位再同步保证多节点无时钟线同步 | STM32 · Lesson 04.0 |
| can-sample-point | CAN 采样点 75-87.5% | CAN Sample Point 75-87.5% | Bosch 推荐区间，兼顾双向容错 | STM32 · Lesson 04.0 |
| can-terminating-resistor-120 | CAN 120Ω 终端电阻 | CAN 120Ω Termination | 总线两端横跨 CAN_H/L，吸收反射 | STM32 · Lesson 04.0 |
| can-error-detection-layers | CAN 五层错误检测 | CAN 5-Layer Error Detection | 位监测+位填充+CRC+帧格式+ACK | STM32 · Lesson 04.0 |
| can-node-state-machine | CAN 节点错误状态机 | CAN Node Error State Machine | Active/Passive/Bus Off 三态；坏节点自动下线 | STM32 · Lesson 04.0 |

### CAN HAL 抽象 & bxCAN 实战（来自 STM32 通信总线专题 · Lesson 04.1）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| hal-can-api-trio | HAL_CAN 三件套 | HAL CAN API Trio | Start + AddTxMessage + GetRxMessage 三个核心 API | STM32 · Lesson 04.1 |
| bxcan-filter-bank | bxCAN 过滤器组 | bxCAN Filter Bank | STM32F103 有 14 个 filter bank，可配多种模式 | STM32 · Lesson 04.1 |
| bxcan-filter-left-shift-5 | 过滤器 ID 左移 5 位 | Filter ID Left-Shift 5 | 标准 ID 在 bxCAN 寄存器 bit[31:21]，需 `id << 5` | STM32 · Lesson 04.1 |
| bxcan-filter-mask-vs-list | 掩码模式 vs 列表模式 | Mask vs List Filter Mode | 前者匹配区间，后者匹配多个精确 ID | STM32 · Lesson 04.1 |
| bxcan-three-tx-mailboxes | 3 个发送邮箱 | Three TX Mailboxes | bxCAN 允许 3 帧并行排队，硬件按 ID 优先级调度 | STM32 · Lesson 04.1 |
| bxcan-two-rx-fifos | 2 个接收 FIFO | Two RX FIFOs | 每个 FIFO 3 级深度，可配不同 NVIC 优先级 | STM32 · Lesson 04.1 |
| can-rx-interrupt-callback | CAN 接收中断回调 | CAN RX Interrupt Callback | `HAL_CAN_RxFifo0MsgPendingCallback`，中断禁阻塞 | STM32 · Lesson 04.1 |
| can-bus-off-recovery | Bus Off 自恢复 | CAN Bus Off Recovery | 软件检测 BOF → Stop → Start → 重激活中断 | STM32 · Lesson 04.1 |
| can-two-board-ping-pong | 两板 CAN 互 ping | Two-Board CAN Ping-Pong | A 板发 ID_A + 订阅 ID_B，B 板反过来 | STM32 · Lesson 04.1 |
| can-tx-mailbox-priority | CAN 发送邮箱优先级 | CAN TX Mailbox Priority | `TransmitFifoPriority` DISABLE=按 ID, ENABLE=按 FIFO | STM32 · Lesson 04.1 |

### RS485 协议 + Modbus RTU（来自 STM32 通信总线专题 · Lesson 05.0）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| rs485-uart-plus-differential | RS485 = UART + 差分 | RS485 = UART + Differential | UART 数据格式 + 差分电平 + 总线拓扑 | STM32 · Lesson 05.0 |
| rs485-a-b-differential-pair | RS485 A/B 差分对 | RS485 A/B Differential Pair | 对称差分电平（±2V），0 和 1 无强弱 | STM32 · Lesson 05.0 |
| rs485-half-duplex-physical | RS485 半双工物理层 | RS485 Half-Duplex Physical | 共用一对线，一次只能一方发 | STM32 · Lesson 05.0 |
| rs485-no-arbitration | RS485 无仲裁 | RS485 No Arbitration | 差分对称 → 无显性压倒隐性 → 同发即短路 | STM32 · Lesson 05.0 |
| rs485-master-slave-protocol | RS485 主从协议 | RS485 Master-Slave Protocol | 软件协调的必然结果；主机问+从机答 | STM32 · Lesson 05.0 |
| max485-transceiver | MAX485 收发器 | MAX485 Transceiver | TTL ↔ 差分转换 IC；R/RE/DE/D 四引脚 | STM32 · Lesson 05.0 |
| max485-de-re-combined-gpio | MAX485 DE/RE 合并 GPIO | MAX485 DE/RE Combined GPIO | 因电平反向可短接，用一个 GPIO 切收发 | STM32 · Lesson 05.0 |
| modbus-rtu-frame | Modbus RTU 帧 | Modbus RTU Frame | 从机地址+功能码+数据+CRC-16 的标准帧 | STM32 · Lesson 05.0 |
| modbus-rtu-crc16 | Modbus CRC-16 | Modbus CRC-16 | 多项式 0xA001，初值 0xFFFF，低字节先发 | STM32 · Lesson 05.0 |
| rs485-120ohm-termination | RS485 120Ω 终端电阻 | RS485 120Ω Termination | 两端各一个横跨 A/B，吸收反射 | STM32 · Lesson 05.0 |
| rs485-vs-can-vs-i2c-vs-spi | 四大总线横向对比 | Four-Bus Horizontal Comparison | I2C/SPI/CAN/RS485 在电气+仲裁+距离+应用的对比 | STM32 · Lesson 05.0 |

### RS485 代码 + Modbus 主机实战（来自 STM32 通信总线专题 · Lesson 05.1）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| rs485-dir-gpio-control | RS485_DIR GPIO 控制 | RS485 DIR GPIO Control | 一个 GPIO 同时控 MAX485 DE+RE，默认 LOW | STM32 · Lesson 05.1 |
| rs485-tc-flag-wait | TC 标志等待 | TC Flag Wait | `UART_FLAG_TC` 置位才算字节真正送完 | STM32 · Lesson 05.1 |
| rs485-tail-byte-loss-bug | RS485 末尾字节丢失 bug | RS485 Tail-Byte Loss Bug | 漏等 TC 切 DIR → 最后字节被截断 | STM32 · Lesson 05.1 |
| uart-dma-idle-interrupt | UART DMA+IDLE 中断 | UART DMA+IDLE Interrupt | DMA 环形接收 + IDLE 触发帧边界；不定长接收工业标准 | STM32 · Lesson 05.1 |
| modbus-master-read-registers | Modbus 主机读寄存器 | Modbus Master Read Registers | 构造+发+等响应+CRC+解析五步事务 | STM32 · Lesson 05.1 |
| modbus-crc16-lookup-table | Modbus CRC-16 查表法 | Modbus CRC-16 Lookup Table | 512 字节查表换 10× 速度 | STM32 · Lesson 05.1 |
| rs485-tx-rx-skeleton | RS485 收发骨架 | RS485 TX/RX Skeleton | `DIR↑ → Transmit → TC wait → DIR↓` 通用模板 | STM32 · Lesson 05.1 |
| modbus-response-timeout | Modbus 响应超时 | Modbus Response Timeout | 典型 300ms 覆盖帧传输+从机处理+余量 | STM32 · Lesson 05.1 |
| rs485-debugging-checklist | RS485 调试清单 | RS485 Debugging Checklist | DIR 默认/接线/终端/地址冲突/超时五项 | STM32 · Lesson 05.1 |
| four-bus-selection-decision-tree | 四大总线选型决策树 | Four-Bus Selection Decision Tree | 板内/板间 × 速度/成本/仲裁 → I2C/SPI/CAN/RS485 | STM32 · Lesson 05.1 |

> 本节随课程生成逐步补录（Q5 决策：模板与 glossary 同步改造）。设计示范见 `docs/plans/2026-04-18-thinking-module-and-concept-graph-design.md` §附录 B。

---

## 使用说明

1. **按学科/主题分类维护**：新增学科时追加二级标题节，表头固定为 5 列；不要改列顺序。
2. **1:1:1 对齐**：
   - 每个 `concept_tag` 只对应一条中文关键词与一条定义
   - 跨主题同义术语应合并为同一条目，"首次出现"列填最早一次
3. **`concept_tag` 命名规范**：
   - 格式 `{topic}-{concept-name}`，全小写、连字符分隔
   - 示例：`stm32-gpio-mode`、`c-pointer-arithmetic`、`transformer-self-attention`、`adlerian-separation-of-tasks`
   - `topic` 建议取自 `roadmap_status.md` 的主题 slug 或主流学科英文简称
4. **"首次出现"格式**：`{主题名} · Lesson {N}`；若主题名较长可用缩写（如 `STM32-HAL · L3`）。
5. **新增术语的流程**（对应阶段 B 开始后的日常操作）：
   1. AI 在 `lesson-template.md` 元信息写入 `concept_tags: [...]`
   2. 同步将每个 tag 加入本表（或更新"首次出现"）
   3. 思考模块（L1）预生成关键词索引时，从本表反查中文关键词
6. **迁移策略**（与设计文档 §九 Q5 / Q7 决策一致）：
   - 旧 session 保持现状，不强制回填历史 lesson 的 concept_tag
   - 历史条目允许 `concept_tag` 列填 `—`，新增条目必须写全
7. **校验**（人工）：每季度 review 一次，查找：
   - 同一 `concept_tag` 在多行出现（违反 1:1:1）
   - `concept_tag` 命名不符格式（大写字母、下划线、空格等）
   - "首次出现"指向已不存在的 session
