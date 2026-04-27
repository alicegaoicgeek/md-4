# Module 17：AutoResearch — 从"会做事"到"自己越做越好"

副标题：五层自学习技术栈 — 让Agent系统记住成功、理解失败、自主进化

角色：A(男声主持人) + B(女声专家)

---

## A段 痛点：你的Agent系统患了失忆症 [A]

你用前面几集搭了一条完整的R2流水线。版本控制管代码，七层架构拆解复杂度，Skills封装领域经验，Sub-agents分工协作，编排层把它们串成流水线。架构优雅，流程完整。

然后你开始验证第一个IP。

某系列L2 Cache控制器，8-way set-associative，ECC可选，两万行RTL。r2-cov跑起来，从53%覆盖率开始爬。你发现L2 Cache驱逐需要8个不同地址映射到同一set才能触发way全填满。你手动调整策略，换了三次方向，48小时后覆盖率闭合到100%。

不错。下一个IP。

第二版——同系列Cache控制器，不同参数化。way数不一样，替换策略从LRU变成了PLRU，ECC路径在单socket配置下不激活。你打开新会话，Agent用默认的"你好，有什么可以帮你"迎接你——48小时的经验全部消失了。L2 Cache驱逐需要8路fill sequence——它不记得。APB断言需要2周期margin——它不记得。团队用PLRU不是LRU——它不记得。你得从头说起。

第5个IP。同架构系列。还是48小时。

你的剪贴板里存了三段"项目上下文"——每次新会话都得粘贴一遍。10M token的对话历史里可能有你需要的信息，但session_search的关键词匹配找不到，MEMORY.md里agent没记。这不是AI助手，是需要你手动喂记忆的工具。

"31个IP不需要从零做31次"。Module 11教你设计Skill——成功策略固化复用。Module 13教你编排——Learning Loop让覆盖率缺口自动匹配策略。但HOW？谁写Skills？谁更新Memory？谁判断什么有效什么无效？

答案是——你。手动。每次。

Module 3给了你版本控制。Module 11给了你Skills做经验封装。Module 12给了你Sub-agents做分工协作。Module 13给了你编排做流程串联。但没人回答一个问题：这些容器里的内容——Memory里该写什么、Skills该怎么进化、什么策略有效什么策略无效——谁来维护？

这就是autoresearch要解决的问题。

这一集揭示五层自学习技术栈——把前面搭建的系统，从你操作的工具，变成自己运转的系统。不是教你搭架子，是教架子里填什么、怎么让填的东西自己变好。

---

## B段 五层自学习技术栈总览 [B]

这一集讲五件事。不是五个功能——五个层。每层解决自学习问题的一个环节。缺任何一层，系统就退化回"你手动操作的工具"。

先看全景。

| 层 | 名称 | 解决什么 | 一句话 |
|----|------|---------|--------|
| L1 | 动态System Prompt | Agent此刻该看到什么 | 运行时组装的上下文操作系统 |
| L2 | 四层记忆架构 | Agent跨会话该记住什么 | 四种信息、四种存储、四种生命周期 |
| L3 | Skills系统 | Agent知道怎么做 | 活的、自更新的过程记忆 |
| L4 | Learning Loop | Agent何时、如何学习 | 异步后台复盘——连接L2和L3的写入机制 |
| L5 | Self-Evolution | Agent怎么可量化地变好 | 读执行trace的反思式进化搜索 |

五层的关系不是并列的——是递进的。

L1到L3是知识基础设施——Agent知道什么、看到什么、会做什么。Module 3的progress.txt是L2最原始的形式。Module 11的Skills是L3，但手写的、静态的。Module 4的七层架构是脚手架——这一集往里填活的、会进化的内容。

L4是反思机制——Agent何时学习。Learning Loop不是一个功能，是连接L2（记忆）和L3（技能）的写入管道。没有L4，L2和L3就只有你手动往里写。

L5是优化引擎——Agent怎么可测量地变好。Learning Loop能增加知识（写Memory、创建Skill），但不能告诉你"新版Skill比旧版好吗？"L5用进化搜索回答这个问题。

为什么R2需要这五层？

r2-cov的覆盖率分析之所以越来越准，是因为每个IP的成功策略通过L4写入L3，通过L5优化，通过L2记住。r2-tdd的断言质量之所以跨IP提升，是因为断言模板在L3里进化。c2rtl的收敛之所以越来越快，是因为L2记住了哪些转换路径有效。topgen的架构生成之所以参数化越来越灵活，是因为L1在验证AXI IP时自动加载AXI协议知识，验证APB时自动切换。

这不是概念。是上层所有模块的共同底座。

接下来，从L1开始，逐层深入。

---

## C段 L1+L2深潜：动态Prompt与记忆架构 [A+B]

### C.1 14层动态System Prompt [A]

大多数Agent的system prompt是一段静态文本——你写完，它就固定了。不同用户看到同一段话，不同项目看到同一段话，工具可不可用都看到同一段话。

Hermes不是这样。

Hermes的system prompt是运行时组装的。不是一段prompt，是一组动态层。14层。每一层根据当前会话的状态决定是否注入、注入什么内容。

走一遍这14层。

第一层，SOUL.md——Agent的长期人格。不是写死在代码里的角色设定，是用户可编辑的文件，存在`~/.hermes/SOUL.md`。你想让Agent更直接、更有判断力、能指出你的问题，改这个文件就行。人格可配置、可迁移、可演化。

第二层，工具行为指南。这是一条铁律——工具存在，才注入对应规则。memory工具可用，才告诉Agent怎么保存记忆。session_search可用，才告诉Agent怎么查历史。工具不存在？对应规则也不存在。

为什么这条铁律重要？因为如果prompt里提到不存在的工具，模型就会幻觉调用。它自信地说"让我搜索一下"，然后卡住——因为浏览器工具在这个部署环境里根本不存在。工具与prompt的一致性，不是nice-to-have，是防幻觉的基础设施。

第三到第五层是环境适配——订阅状态、工具强制规则、用户传入的system message。

第六到第八层是核心上下文——Memory快照、User Profile、外部memory provider注入。

第九层是Skills索引。Agent在这一层看到所有已安装技能的摘要列表——name、description、category。这是Module 11讲的progressive disclosure的Level 0入口——约3k tokens，Agent根据这个列表判断是否需要加载完整Skill。

第十到第十四层是运行时信息——项目上下文文件、会话元信息（时间/SessionID/模型/provider）、provider身份修正、环境提示（不同操作系统适配）、平台提示（命令行/即时通讯等多端适配）。

还有一个隐藏层——临时指令层。不存入缓存，不写入会话数据库，每次调用临时拼接到system prompt后面。用途是临时影响Agent行为，又不破坏缓存前缀。

R2的14层包含芯片专属上下文——DUT架构描述、EDA工具可用性、团队代码风格规范。r2-cov跑AXI IP时，第十层自动加载AXI协议知识——burst类型、read模式、outstanding transactions。跑APB IP时，自动换成APB协议知识——transfer类型、wait states、error response。不需要你手动切换，14层动态组装自动适配。这是Module 4"渐进披露"的具体实现。

### C.2 四层记忆架构 [B]

A段讲了痛点——48小时经验消失，新会话从零开始。根因不是Agent不记东西，是你以为记忆是录音机——录下一切、随时调取。但Hermes的记忆是笔记本——Agent自己决定记什么。

而且不是一个笔记本——是四个，每个有不同的规则。

**Layer 1: Prompt Memory（热层）**。两个小文件——MEMORY.md约800 tokens存长期事实，USER.md约500 tokens存用户画像。加起来约1,300 tokens。会话开始时做冻结快照注入system prompt——同一会话内不刷新。为什么故意这么小？因为要保护缓存前缀（system prompt不变的部分可以被缓存复用）。system prompt越稳定，API调用越便宜、越快。写入是即时持久化到磁盘的，但要下次新会话才会进入system prompt。

限制很明确：1,300 token的预算，超限了工具直接返回错误，Agent必须自己整合或删除旧条目才能写入新的。这意味着Agent得做取舍——什么值得占这1,300 token的位置。

**Layer 2: Session Archive（冷层）**。全部命令行和消息会话存本地数据库。通过session_search工具按需查询。基于关键词匹配加模型摘要。不占system prompt空间，需要时才查。

但关键词匹配有天然缺陷。你说"认证服务"，存的是"authentication microservice uses cache for session tokens"——断链。换个说法就查不到。没有实体识别——"Alice"和"我的同事Alice from engineering"是两个世界。

**Layer 3: Skills（过程记忆）**。Module 11的焦点。但这里要强调一个认知升级——Skills也是记忆。Memory记事实（"L2C用PLRU替换策略"），Skills记方法（"怎么闭合L2C覆盖率"）。事实性记忆和过程性记忆，分开存、分开访问、分开进化。

**Layer 4: External Provider（可选扩展层）**。可插拔的外部记忆后端。7个provider可选，每个解决内置系统的不同限制。

重点说Hindsight——在行业记忆基准测试中，10M token规模排名第一，64.1%。第二名40.6%。超出23.5个百分点。一千万token——直接塞进上下文物理上不可能，必须靠结构化检索。G段会深入展开。

内置系统有五个明确限制。第一，prompt memory空间太小，1,300 token存不了多少。第二，session search只做关键词匹配，不懂语义。第三，没有实体识别，同一个人不同称呼被当成两个实体。第四，上下文压缩前有一次记忆刷写机会，但刷写时Agent没觉得值得记的事实就永远丢了——不可逆。第五，短会话可能什么都不记，完全依赖Agent判断。

这五个限制不是bug——是设计权衡。小、透明、本地、可检查。但如果你要做31个IP的大规模验证，这些限制就会成为瓶颈。这就是为什么需要L4 Learning Loop来系统性写入，需要L5 External Provider来突破检索能力。

R2怎么用这四层？L1等价于progress.txt——Agent此刻该知道的事实。L2等价于版本历史——历史可查但不常驻。L3等价于VeriSmart的24个验证Skill——scb_gen、seq_gen、cov_gen。L4将是Hindsight的验证知识图谱——entities是寄存器、接口、协议类型、覆盖率策略，relationships是"CTRL.mode控制DMA通道"、"ncel2c500用PLRU替换策略"。

---

## D段 L3深潜：Skills作为活文档 [B]

Module 11讲了五种Skill设计模式——Tool Wrapper、Generator、Reviewer、Orchestrator、Diagnostic。讲了三个核心Skill——scb_gen、seq_gen、cov_gen。这些都是**设计**Skill。

但有一个问题Module 11没有回答：Skill写完之后呢？

你的代码评审Skill用了三个月没动过。项目变了、标准变了、Agent的评审越来越不对路——但你不知道怎么改能变好，改了也没法量化验证。

你的部署Skill还是三个月前的版本。CI流水线已经改了，加了一个lint检查步骤。Agent按旧Skill执行，跳过了新增的lint，部署的代码没过检查。Skill的Pitfalls段也没提到这个变更。

Skill是静态文档。SKILL.md写了When to Use、Procedure、Pitfalls、Verification四段，但没有机制感知外部变更。世界变了，Skill不知道。

这一段不重讲Module 11的设计模式。讲的是Skill作为活文档——怎么被发现、怎么被加载、怎么保持鲜活。

**发现机制：三级渐进加载。**

Level 0：skills_list()。返回所有已安装Skill的摘要——name、description、category。约3k tokens。始终在system prompt第九层可见。Agent在这一层做匹配判断——当前任务需要哪个Skill？

Level 1：skill_view(name)。Agent判断需要某Skill后，调用此方法加载完整内容和元数据。Token消耗按Skill大小。

Level 2：skill_view(name, path)。加载Skill引用的特定参考文件——配置模板、示例代码、DUT架构描述。按需最小化。

Progressive disclosure省了token，但也意味着description就是唯一的匹配入口。描述不精确，Agent就无法在Level 0判断是否需要加载——写得差的Skill，等于没装。

**条件激活：自动显示和隐藏。**

四个字段控制Skill的可见性。

备选降级——当某工具集可用时隐藏此Skill，不可用时自动显示。典型案例：免费搜索Skill配了备选降级规则。你有付费搜索接口，付费工具可用，免费搜索隐藏。接口没配？免费搜索自动出现作为替代。

前置依赖——当某工具集不可用时隐藏此Skill。

平台适配——不兼容平台上自动隐藏。某平台专属的通讯Skill，其他平台上看不到。

但条件激活是主动声明的——不声明任何条件字段的Skill默认始终可见。如果你有付费搜索也有自定义搜索Skill，但自定义Skill没配备选降级规则，Agent就看到两个搜索入口，行为不一致。技能冲突的根源不是系统缺能力，是Skill作者没用这些字段。

**生命周期问题：静态文档 vs 活文档。**

Module 11教你设计Skill。但世界变了谁更新？CI改了谁通知Skill？新IP引入了之前没见过的覆盖率模式，谁创建新Skill？

R2的24个Skill遵循SKILL.md格式——When to Use、Procedure、Pitfalls、Verification。当IP需要库里没有的新类型Scoreboard时，系统需要创建新Skill。AXI专用Skill在验证APB IP时通过条件激活自动隐藏。

但创建、更新、进化——这些动作不是Skill系统自己能完成的。静态文档是Module 11。活的、自更新的文档——需要Learning Loop。

---

## E段 L4深潜：Learning Loop [A]

### E.1 Review Agent机制

Module 11留了一个问题：谁写Skill？谁更新Memory？答案不是你——是Learning Loop。

Learning Loop不是模型训练。不是强化学习。不是人类反馈对齐。不是梯度下降。它更像一个后台复盘系统——一个工程化的外部记忆维护机制。

机制是这样的。

第一步，主Agent完成用户任务，正常返回回复。用户看到回复，继续工作。到这里为止，跟普通Agent一样。

第二步，系统检查是否达到复盘阈值。注意——memory和skill有各自独立的触发阈值。不是每次对话都触发。

第三步，如果达到阈值，后台分裂出一个临时Review Agent。

这个Review Agent本身就是Module 12讲的Sub-agent——分裂、隔离、临时。它回顾刚才的对话，做两个判断：有内容值得保存到Memory吗？有内容值得创建或更新Skill吗？

第四步，如果有价值内容，Review Agent写入Memory或Skills文件。

三个关键属性。

**异步**——不阻塞主回复。用户看到Agent回复的时候，Review Agent在后台默默工作。不增加用户等待时间。

**透明**——Review Agent的内部对话不发给用户。用户不知道复盘在发生。不会收到"我正在保存记忆"这样的消息。

**独立阈值**——memory复盘和skill复盘分别触发。Agent可能判断"这次对话里有值得记的事实，但没有值得创建的Skill"，或者反过来。

反模式要避免两种。每次对话都触发——记忆污染，垃圾信息淹没有价值的内容。触发太少——经验丢失，回到A段的痛点。阈值是质量门控，不是开关。

### E.2 四类信息与更新路径

Learning Loop的真正力量不在于Review Agent本身——在于它连接了L2（记忆）和L3（技能）。

四类长期信息，四条更新路径。

| 信息类型 | 存储位置 | 注入方式 | Learning Loop怎么写 |
|---------|---------|---------|-------------------|
| 长期事实 | MEMORY.md | system prompt快照 | Review Agent判断值得记→写入 |
| 用户画像 | USER.md | system prompt快照 | Review Agent提取用户偏好→写入 |
| 历史对话 | SessionDB | session_search实时查 | 自动存储，不需要Loop |
| 可复用方法 | Skills | 按需加载 | Review Agent判断值得固化→创建/更新 |

Memory记事实——"L2C way-fill需要8个地址映射到同一set"。Skills记方法——"闭合L2C覆盖率的策略：先触发all-way fill，再用eviction+snoop组合攻击corner case"。事实进Memory，方法进Skills。

Learning Loop是写入这两层的机制。没有它，L2和L3就是空容器——或者只有你手动往里填的内容。

R2怎么用Learning Loop？

r2-cov成功闭合L2 Cache覆盖率后，Review Agent做两件事。第一，写Memory："L2C way-fill需要8个地址映射到同一set，PLRU替换策略下eviction顺序与LRU不同，ECC路径在单socket配置下不激活"。第二，创建或更新Skill：cache IP的覆盖率缺口策略——先确定性填满所有way，再用地址碰撞触发eviction，再用snoop请求在eviction中间制造coherence corner case。

下次遇到类似cache IP，这个策略直接可用。不需要你粘贴上下文，不需要你重新解释48小时的经验。

> [素材：S6 Error-Driven Context Refinement — 来源：魏依承《从第一性原理思考 Agentic Engineering》]
> 软件工程界把这个机制公式化为Error-Driven Context Refinement：犯错→诊断根因→检索现有知识→创建或更新Rule/Skill→预防复发。Review Agent的写入逻辑与这个公式完全同构——每次IP闭合后的经验沉淀，就是这个公式的生产级实现。

coverage v4说的"Learning Loop——覆盖率缺口自动匹配策略"就是这个。策略不是硬编码的——Review Agent每做完一个IP就写更好的Skill。coverage v4在概念层介绍了这个能力，现在你看到了HOW。

---

## F段 L5深潜：反思式自进化 [B]

### F.1 Learning Loop解决不了的问题

E段的Learning Loop解决了"谁写Memory、谁创建Skill"。但它解决不了一个更深的问题——怎么知道写的是好是坏？

Learning Loop增加知识。它往Memory里写事实，往Skills里创建工作流。但它基于单次对话的判断。跑完10个IP，你可能有10个版本的覆盖率策略Skill——每个是某次对话后Review Agent写的。哪个最好？Learning Loop不告诉你。

积累但不优化。这是L4的天花板。

你的代码评审Skill用了三个月。项目变了，标准变了，Agent的评审越来越不对路。你知道Skill要改——但手动改完没法验证是变好了还是变差了。你能做的只有凭感觉改、凭感觉评估。

L5解决的就是这个问题：可量化的进化。

### F.2 反思式进化机制

反思式进化优化框架——开源，MIT许可证。

它的全称是"基因-帕累托提示词进化"。但名字不重要——重要的是它跟之前所有优化器的核心区别。

之前的优化器看到结果——成功或失败——然后调整。统计相关性。反思式进化读执行记录，理解**为什么**失败，然后提出定向改进。不是随机变异碰运气，是基于失败原因的反思式搜索。

六步优化循环。

第一步，选择优化目标。一个SKILL.md文件、一个工具描述、一段system prompt。

第二步，构建评估数据集。两个来源——从SessionDB挖掘真实对话历史，或者用强模型读Skill文本合成测试用例。15到30个样本。

第三步，包装为优化模块。Skill文本变成可优化签名——system prompt就是Skill内容，输入是任务描述，输出是执行结果。工作流可以包装为推理-行动链。

第四步，运行进化优化器。5到10次迭代。每次迭代读取执行记录，分析为什么失败，生成针对性变异，评估新版本。

第五步，评估对比。在保留测试集上对比原版和进化版。做统计显著性检查——不是"看起来好了"，是"统计上显著好了"。

第六步，部署。自动创建版本分支加代码审查。人类审核合并。可回滚。永不直接提交。

关键数据：不需要GPU。纯文本变异加API调用评估。每次优化$2到$10。最少3个样本就能启动。超越强化学习和之前所有同类优化器。

### F.3 五阶段进化管线与五道Guardrail

反思式进化能优化什么？不只是Skill。整个Agent的可优化表面分五层——按风险从低到高、价值从高到低排序。

**Phase 1——Skill Files。** 已实现。纯文本过程指令，最容易变异和评估。直接衡量——Agent按这个Skill做，任务完成了吗？这是第一阶段，因为最安全、最直接、最有价值。

**Phase 2——Tool Descriptions。** 计划中。工具schema的description字段。工具选择本质是分类问题——给定任务描述，选一个最匹配的工具。你让Agent搜代码，它每次都用grep而不是search_files。纠正了五次还是犯。问题不是Agent笨——是工具描述写得模糊，模型在边界情况分不清。反思式进化优化工具描述文本，用实际任务做评估，直到选对率最高。

**Phase 3——System Prompt Sections。** 计划中。参数化prompt_builder各section为可优化签名，离线优化后部署为新版本。有一个硬约束——不能破坏缓存前缀。只能离线优化，不能会话中途变更。

**Phase 4——Code Evolution。** 计划中。用达尔文式进化器（基于版本控制的代码有机体）进化工具实现代码。风险最高——代码改错直接crash。需要强测试套件做guardrail。

**Phase 5——Continuous Loop。** 自动化流水线无人值守运行。需要前四阶段全部验证通过。

阶段是顺序的——每个必须证明自己有效才能推进到下一个。如果某阶段没有产出有意义的改进，停下来重新评估。不盲目推进。

进化搜索是双刃剑。进化可能产出测试得分更高但实际有害的变体——缓存机制失效，API成本涨30%，行为微妙偏移。

所以有五道Guardrail。

第一道，测试套件门控——自动化测试100%通过，不允许任何回归。

第二道，大小限制——Skill不超过15KB，工具描述不超过500字符。防止进化产出臃肿的版本。

第三道，缓存兼容性——不允许mid-conversation变更system prompt。只能离线优化后部署新版本。

第四道，语义保持——进化后的版本不能偏离原始目的。通过评估集中的边界case检测。

第五道，强制代码审查——所有变更走版本分支加审查流程，人类审核后合并。永不自动直接提交。

这不是"自动部署进化结果"。是"自动搜索加人工把关"。

R2怎么用？Phase 1直接应用于R2的24个验证Skill。跑完10个IP后，反思式进化优化cov_gen的Skill文本——产出更好的覆盖率策略。评估指标很具体：覆盖率闭合更快？手动干预更少？48小时能压到多少？它不猜——它读执行记录看为什么卡在某个覆盖率缺口上，然后改Skill的策略描述。

---

## G段 L5b深潜：Hindsight记忆突破 [A]

F段讲了反思式进化——让Skill可量化进化。但进化需要数据，数据需要记忆。如果记忆系统本身有瓶颈——关键词匹配断链、实体识别缺失、1,300 token预算限制——进化从哪来数据？

Hindsight填的就是这个缺口。

回顾C.2的痛点。内置记忆是agent-curated——Agent自己决定记什么。你提到的project name、同事名字、技术偏好，这些Agent不会主动记。session_search是关键词匹配——"认证服务"和"authentication microservice"断链。压缩前flush可能漏掉关键事实——不可逆丢失。

Hindsight的解法不是修补这些限制——是在上面叠加一层结构化提取。

两个钩子。

**Prefetch（响应前）**：每轮对话开始前，Hindsight从历史会话检索与当前消息相关的记忆——语义搜索加关键词匹配加实体图遍历加重排序。检索结果注入system prompt。模型看到用户消息之前，就已经拥有历史上下文。

你提过一次product launch deadline。一周后，新会话，完全不同的话题——Hermes已经知道了。你没重复自己，没粘贴上下文，是Prefetch自动召回的。

**Retain（响应后）**：每轮对话结束后，后台提取对话中的facts、entities、relationships。结构化存储。下一轮就可检索。

设计约束：当前轮说的内容，下一轮才可检索。不在当前轮可见。这是有意的——保持每次调用速度。

三种Memory Mode控制注入方式。

**hybrid（默认）**——自动注入加三个工具（hindsight_recall/retain/reflect）暴露给模型。Agent既被动接收上下文，也能主动搜索、保存、合成。

**context**——仅自动注入，不暴露任何工具。模型完全不知道记忆系统的存在，只是"自然地"拥有历史上下文。最简单、最透明。

**tools**——仅工具，不自动注入。模型必须主动调用hindsight_recall才能获取记忆。完全控制何时检索、检索什么。

两种Prefetch Method。

recall——语义搜索、关键词匹配、实体图遍历、重排序。快。

reflect——模型跨所有相关记忆合成连贯摘要。慢，但对复杂上下文更有用。这是记忆层最接近真正自我改进的机制——系统不只是检索，是跨记忆合成高阶洞察。

行业记忆基准测试。10M token规模——一千万token，直接塞进上下文物理上不可能。Hindsight 64.1%。第二名40.6%。超出23.5个百分点。这是唯一有公开测试结果的记忆方案。

部署灵活——本地模式和云模式用同一API。切换是配置文件的一个字段从"local"改为"cloud"，一行改动，无数据迁移。本地模式数据不出机器，内嵌数据库，首次启动需要一分钟初始化。云模式跨机器持久化，多实例共享。

R2怎么用Hindsight？

Hindsight为R2存储结构化验证知识图谱。不是文本chunk——是structured knowledge。

Entities：IP名（ncel2c500）、寄存器字段（CTRL.mode）、协议类型（AXI4、APB）、覆盖率策略（way-fill sequence）。

Relationships："ncel2c500用PLRU替换策略"、"AXI burst驱逐需要way-fill序列"、"ECC路径在单socket配置下不激活"、"CTRL.mode控制DMA通道选择"。

新cache IP进入流水线——Prefetch自动检索所有cache相关验证知识。包括ncel2c500的87个排除原因——哪些覆盖点是物理不可达的、为什么不可达、怎么追溯到RTL设计。不需要你粘贴，不需要你告诉Agent去查。

coverage v4说的"Memory+版本控制——覆盖率只进不退"——Memory就是Hindsight的Retain钩子，版本控制保存每一步成果。每轮迭代跑完，覆盖率涨了就提交，Hindsight Retain自动提取成功策略。覆盖率退了就丢弃。成果永不丢失。

---

## H段 收束：从五层到R2飞轮 [A+B]

### [B] 五层recap

五层讲完了。用"不是X——是Y"收束每一层。

L1——不是静态prompt。是运行时组装的上下文操作系统。14层动态拼接，工具存在才注入规则，临时指令层不破坏缓存。

L2——不是一个记忆。四层——热层1,300 token快照、冷层本地数据库关键词搜索、过程层Skills按需加载、扩展层可插拔provider。不同持久性、不同访问模式、不同限制。

L3——不是文档库。活的、自更新的过程记忆。三级渐进披露省token，条件激活避冲突，四段式标准格式让Agent能理解。但静态文档不会自己变好——需要Learning Loop。

L4——不是模型训练。工程化的外部记忆维护系统。异步、透明、独立阈值。Review Agent是L2和L3的写入管道——没有它，知识容器是空的。

L5——不是随机变异。读执行trace理解为什么失败的反思式搜索。五道Guardrail防止进化出有害变体。自动搜索，人工把关。

### [A] R2飞轮

五层叠在一起，产生飞轮效应。

**第1个IP：冷启动。** 通用Skill，空Memory，Hindsight知识图谱没有验证历史。Agent从通用知识出发，覆盖率爬坡靠人类指导。48小时。Learning Loop在闭合后写Memory——"L2C way-fill需要8路fill sequence"、"PLRU替换策略下eviction顺序不同"。创建初始Skill——cache覆盖率策略v1。

**第5个IP：温启动。** Hindsight Prefetch自动召回cache相关验证知识。Skill部分匹配——同类cache但参数不同。Learning Loop在每个IP闭合后改进Skill。24小时。

**第15个IP：热启动。** 反思式进化优化过的Skill——Phase 1跑完10个IP的数据，进化出更好的策略描述。Hindsight知识图谱里有丰富的entities和relationships——15个cache IP的验证经验全部结构化存储。Agent不需要人类指导，Prefetch给它历史，Skill给它方法，Memory给它事实。8小时。

"31个IP不需要31次冷启动"不是愿望——是五层复合的数学结果。

每一层单独拿出来都有价值——14层dynamic prompt防幻觉、四层记忆分治存储、Skills渐进披露省token、Learning Loop自动写入、反思式进化可量化优化。但真正的力量在复合：Learning Loop（L4）往Memory（L2）和Skills（L3）里写入，反思式进化（L5）拿L4写入的数据做进化评估，Hindsight（L5b）让L2的检索突破关键词匹配的限制，进化后的Skills（L3）通过L1的dynamic prompt自动注入给Agent。

上层模块——r2-tdd的断言越写越准、r2-cov的覆盖率闭合越来越快、c2rtl的收敛越来越稳、specx的规格理解越来越深、topgen的架构生成越来越灵活、VeriSmart的24个验证资产越来越精准——不是五个独立的"越来越好"。是同一个五层自学习栈在不同验证问题上的投射。

### [B] 前向桥接

前面几集教你搭建。这一集教搭建的东西怎么学习。上层模块——r2-tdd、r2-cov、r2-c2rtl、specx、topgen——是这个自学习栈在具体芯片验证问题上的应用。每个上层模块的"越做越好"，底层都是这五层在工作。

### [A] 收束

Module 3说过一句话——"Skill是系统的永久升级——不退化、不遗忘。"

现在你知道了写这些Skill的机制——Learning Loop。
知道了测试它们、让它们变好的机制——反思式进化。
知道了让记忆突破关键词匹配的机制——Hindsight。
知道了把所有这些组装成运行时上下文的机制——14层Dynamic Prompt。

系统不只是记住。它反思。它进化。它越做越好。

这就是autoresearch——不是另一个功能模块，是让所有模块都能自学习的底层引擎。
