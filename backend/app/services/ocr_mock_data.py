"""
OCR模拟数据

存放各学科的模拟OCR文本数据，供mock模式使用
"""

from typing import Dict, List


# 数学学科模拟文本
MATH_MOCK_TEXTS: List[str] = [
    """计算下列各题：
1. 25 + 36 × 2 = 
2. 125 × 8 - 500 = 
3. (48 + 52) ÷ 10 = 
4. 360 ÷ 9 + 45 = 
5. 78 - 15 × 4 = """,

    """解方程：
1. 3x + 5 = 20
   解：3x = 20 - 5
       3x = 15
       x = 5
2. 2(x - 3) = 14
   解：x - 3 = 7
       x = 10""",

    """应用题：
小明买了3支铅笔，每支2元，又买了5本笔记本，每本4元。
(1) 买铅笔花了多少钱？
    3 × 2 = 6（元）
(2) 买笔记本花了多少钱？
    5 × 4 = 20（元）
(3) 一共花了多少钱？
    6 + 20 = 26（元）""",

    """填空题：
1. 一个长方形的长是8厘米，宽是5厘米，周长是____厘米。
2. 1米 = ____厘米
3. 3小时 = ____分钟
4. 1千克 = ____克""",

    """判断题（对的打√，错的打×）：
1. 0除以任何数都得0。 (×)
2. 两位数乘两位数，积可能是三位数，也可能是四位数。 (√)
3. 边长是4厘米的正方形，周长和面积相等。 (×)
4. 闰年有366天。 (√)""",

    """简便计算：
1. 125 × 32 × 25
   = 125 × 8 × 4 × 25
   = (125 × 8) × (4 × 25)
   = 1000 × 100
   = 100000
2. 99 × 56 + 56
   = (99 + 1) × 56
   = 100 × 56
   = 5600"""
]


# 语文学科模拟文本
CHINESE_MOCK_TEXTS: List[str] = [
    """《春》
盼望着，盼望着，东风来了，春天的脚步近了。
一切都像刚睡醒的样子，欣欣然张开了眼。山朗润起来了，水涨起来了，太阳的脸红起来了。
小草偷偷地从土里钻出来，嫩嫩的，绿绿的。园子里，田野里，瞧去，一大片一大片满是的。""",

    """古诗默写：
《静夜思》
李白
床前明月光，
疑是地上霜。
举头望明月，
低头思故乡。

《春晓》
孟浩然
春眠不觉晓，
处处闻啼鸟。
夜来风雨声，
花落知多少。""",

    """作文片段：
我的家乡
我的家乡是一个美丽的小村庄。村子前面有一条清澈的小河，河水哗哗地流着，像在唱着欢快的歌。
夏天的时候，我和小伙伴们常常在河边玩耍。我们在河里捉小鱼，在岸边捉蜻蜓，快乐极了。
我爱我的家乡，更爱家乡的小河。""",

    """词语解释：
1. 欣欣向荣：形容草木长得茂盛。比喻事业蓬勃发展。
2. 一丝不苟：形容做事十分认真、细致，一点儿也不马虎。
3. 坚持不懈：坚持到底，一点不松懈。
4. 画龙点睛：比喻作文或说话时在关键地方加上精辟的语句，使内容更加生动传神。""",

    """阅读理解：
《小猫钓鱼》
猫妈妈带着小猫去河边钓鱼。一只蜻蜓飞来了，小猫看见了，放下钓鱼竿，就去捉蜻蜓。蜻蜓飞走了，小猫空着手回到河边。一看，猫妈妈钓了一条大鱼。
小猫又拿起钓鱼竿钓鱼。一只蝴蝶飞来了，小猫又放下钓鱼竿，去捉蝴蝶。蝴蝶飞走了，小猫又空着手回到河边。一看，猫妈妈又钓了一条大鱼。
问题：小猫为什么钓不到鱼？""",

    """成语填空：
1. 画（蛇）添足
2. 守（株）待兔
3. （井）底之蛙
4. 亡羊补（牢）
5. （刻）舟求剑
6. 掩耳盗（铃）"""
]


# 英语学科模拟文本
ENGLISH_MOCK_TEXTS: List[str] = [
    """Vocabulary:
1. apple - n. 苹果
2. book - n. 书
3. cat - n. 猫
4. dog - n. 狗
5. elephant - n. 大象

Sentences:
1. I have an apple.
2. This is my book.
3. The cat is cute.
4. I like dogs.
5. An elephant is big.""",

    """Complete the sentences:
1. My name ______ (be) Tom.
   Answer: is
2. She ______ (like) apples.
   Answer: likes
3. They ______ (go) to school every day.
   Answer: go
4. I ______ (have) a new bag.
   Answer: have
5. He ______ (play) football yesterday.
   Answer: played""",

    """Reading Comprehension:
My Family
There are four people in my family. They are my father, my mother, my sister and me. My father is a doctor. My mother is a teacher. My sister and I are students. I love my family.

Questions:
1. How many people are there in the family?
   Answer: Four.
2. What does the father do?
   Answer: He is a doctor.""",

    """Translation:
1. 早上好！ - Good morning!
2. 你好吗？ - How are you?
3. 我叫李明。 - My name is Li Ming.
4. 谢谢你！ - Thank you!
5. 再见！ - Goodbye!""",

    """Dialogue:
A: Hello! What's your name?
B: Hi! My name is Amy. What's your name?
A: I'm John. Nice to meet you!
B: Nice to meet you, too!
A: How old are you?
B: I'm ten years old. And you?
A: I'm eleven.""",

    """Write about your favorite animal:
My favorite animal is the panda. Pandas are black and white. They are very cute. They like eating bamboo. Pandas live in China. I love pandas very much."""
]


# 物理学科模拟文本
PHYSICS_MOCK_TEXTS: List[str] = [
    """计算题：
1. 一辆汽车以20m/s的速度匀速行驶，行驶了100秒，求汽车行驶的距离。
   解：s = vt = 20 × 100 = 2000m

2. 一个物体的质量是5kg，受到的重力是多少？（g=10N/kg）
   解：G = mg = 5 × 10 = 50N""",

    """填空题：
1. 力的单位是______，符号是______。
   答案：牛顿，N
2. 速度的单位是______，符号是______。
   答案：米每秒，m/s
3. 密度的计算公式是______。
   答案：ρ = m/V""",

    """实验报告：
测量小车的平均速度
实验目的：测量小车在斜面上运动的平均速度
实验器材：斜面、小车、刻度尺、秒表
实验步骤：
1. 用刻度尺测量斜面的长度s
2. 让小车从斜面顶端滑下，用秒表记录时间t
3. 计算平均速度v = s/t""",

    """概念题：
1. 什么是力？
   答：力是物体对物体的作用。
2. 什么是惯性？
   答：物体保持原来运动状态不变的性质叫惯性。
3. 牛顿第一定律的内容是什么？
   答：一切物体在没有受到力的作用时，总保持静止状态或匀速直线运动状态。""",

    """作图题：
画出下列物体所受重力的示意图：
1. 静止在水平地面上的小球
2. 沿斜面下滑的木块
（要求：标出重力的作用点和方向）""",

    """计算题：
一个铁块的质量是780g，体积是100cm³。
(1) 求铁块的密度。
    解：ρ = m/V = 780g/100cm³ = 7.8g/cm³
(2) 如果把这个铁块切成两半，每一半的密度是多少？
    答：密度不变，仍是7.8g/cm³，因为密度是物质的特性。"""
]


# 化学学科模拟文本
CHEMISTRY_MOCK_TEXTS: List[str] = [
    """化学方程式：
1. 铁在氧气中燃烧：
   3Fe + 2O₂ =点燃= Fe₃O₄
2. 碳在氧气中充分燃烧：
   C + O₂ =点燃= CO₂
3. 实验室制取氧气：
   2H₂O₂ =MnO₂= 2H₂O + O₂↑""",

    """填空题：
1. 水是由______元素和______元素组成的。
   答案：氢，氧
2. 空气中含量最多的气体是______。
   答案：氮气（N₂）
3. 分子是保持物质______的最小粒子。
   答案：化学性质""",

    """实验现象描述：
1. 镁条在空气中燃烧：发出耀眼的白光，放出热量，生成白色固体。
2. 铁丝在氧气中燃烧：剧烈燃烧，火星四射，放出热量，生成黑色固体。
3. 硫在氧气中燃烧：发出明亮的蓝紫色火焰，放出热量，生成有刺激性气味的气体。""",

    """计算题：
已知水的化学式是H₂O，求：
(1) 水的相对分子质量
    解：1×2 + 16 = 18
(2) 水中氢元素和氧元素的质量比
    解：(1×2) : 16 = 2 : 16 = 1 : 8
(3) 水中氢元素的质量分数
    解：(2/18) × 100% = 11.1%""",

    """物质分类：
单质：氧气(O₂)、氮气(N₂)、铁(Fe)、铜(Cu)
化合物：水(H₂O)、二氧化碳(CO₂)、氧化铁(Fe₂O₃)
混合物：空气、海水、石灰水""",

    """实验操作：
1. 酒精灯的使用：
   - 禁止向燃着的酒精灯里添加酒精
   - 禁止用酒精灯引燃另一只酒精灯
   - 熄灭时用灯帽盖灭，不可用嘴吹灭
2. 给试管里的液体加热：
   - 液体体积不超过试管容积的1/3
   - 试管夹夹在距试管口约1/3处"""
]


# 生物学科模拟文本
BIOLOGY_MOCK_TEXTS: List[str] = [
    """填空题：
1. 细胞是生物体结构和功能的______。
   答案：基本单位
2. 植物细胞特有的结构是______、______和______。
   答案：细胞壁、叶绿体、液泡
3. 绿色植物通过______作用制造有机物。
   答案：光合""",

    """识图题：
（植物细胞结构图）
1. 图中A是______，具有保护和支持作用。
   答案：细胞壁
2. 图中B是______，能控制物质进出。
   答案：细胞膜
3. 图中C是______，是遗传信息库。
   答案：细胞核""",

    """实验报告：
观察洋葱鳞片叶表皮细胞
实验目的：认识植物细胞的基本结构
实验步骤：
1. 擦：擦拭载玻片和盖玻片
2. 滴：在载玻片中央滴一滴清水
3. 撕：撕取洋葱鳞片叶内表皮
4. 展：将表皮展平在水滴中
5. 盖：盖上盖玻片
6. 染：用碘液染色
7. 观察：先用低倍镜观察""",

    """选择题：
1. 下列属于生物的是（C）
   A. 机器人  B. 钟乳石  C. 小草  D. 电脑
2. 光合作用的场所是（B）
   A. 线粒体  B. 叶绿体  C. 细胞核  D. 液泡
3. 细胞中的能量转换器是（A、B）
   A. 叶绿体  B. 线粒体""",

    """简答题：
1. 为什么大树底下好乘凉？
   答：因为植物进行蒸腾作用，水分蒸发时吸收热量，使周围温度降低。
2. 绿色植物在生物圈中的作用是什么？
   答：(1) 制造有机物；(2) 维持碳-氧平衡；(3) 促进水循环。""",

    """食物链：
草原生态系统中的食物链：
草 → 兔 → 狐
草 → 鼠 → 蛇 → 鹰
草 → 蝗虫 → 鸟 → 鹰

问题：
1. 这些食物链的起点都是什么？
   答：草（生产者）
2. 如果大量捕杀狐，兔的数量会怎样变化？
   答：先增加，后因食物不足而减少。"""
]


# 所有学科的模拟文本字典
MOCK_TEXTS: Dict[str, List[str]] = {
    "math": MATH_MOCK_TEXTS,
    "mathematics": MATH_MOCK_TEXTS,
    "chinese": CHINESE_MOCK_TEXTS,
    "english": ENGLISH_MOCK_TEXTS,
    "physics": PHYSICS_MOCK_TEXTS,
    "chemistry": CHEMISTRY_MOCK_TEXTS,
    "biology": BIOLOGY_MOCK_TEXTS,
}


def get_mock_text(subject: str, index: int = None) -> str:
    """
    获取指定学科的模拟文本
    
    Args:
        subject: 学科名称
        index: 文本索引，如果为None则随机选择
        
    Returns:
        模拟OCR文本
    """
    import random
    
    # 标准化学科名称
    subject_lower = subject.lower()
    
    # 获取该学科的文本列表
    texts = MOCK_TEXTS.get(subject_lower, CHINESE_MOCK_TEXTS)  # 默认返回语文
    
    if index is not None and 0 <= index < len(texts):
        return texts[index]
    else:
        return random.choice(texts)


def get_available_subjects() -> List[str]:
    """
    获取支持的学科列表
    
    Returns:
        学科名称列表
    """
    return list(MOCK_TEXTS.keys())
