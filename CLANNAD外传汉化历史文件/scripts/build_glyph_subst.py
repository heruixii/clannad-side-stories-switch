# -*- coding: utf-8 -*-
"""build_glyph_subst.py —— CLANNAD Side Stories 字形替换构建器（v39）

原理：游戏字库 FONT.PAK 每个字体面只有 7188 个字形，字符集为日文 JIS X 0208；
简体专用字没有字形，实机渲染为空白。本脚本在不改变 SCRIPT.PAK 长度、
不改容器结构的前提下，把每个「字库没有的字符」等长替换成字库里有、
语义/形体尽量等价的字符。

用法：
    python build_glyph_subst.py --input SCRIPT.PAK --output SCRIPT.PAK.v39
    python build_glyph_subst.py --input SCRIPT.PAK --check        # 只体检，不写文件

依赖：opencc-python-reimplemented（pip install opencc-python-reimplemented）
"""
import argparse, collections, hashlib
from pathlib import Path

try:
    import opencc
except ImportError:  # 没有 opencc 时退化为「手工表 + 兜底」，仍可运行
    opencc = None

MANUAL = {
'—': '―', '‘': '『', '’': '』', '“': '「', '”': '」', '…': '…', '上': '上', '下': '下', '业': '業', '东': '東', '丢': '失', '两': '両', '为': '為', '么': '麼', '乐': '楽', '习': '習', '书': '書', '买': '買', '些': '等', '亲': '親', '们': '等', '价': '価', '份': '分', '仿': '似', '伙': '輩', '传': '伝', '伤': '傷', '你': '汝', '使': '使', '俩': '二', '俺': '我', '值': '値', '做': '作', '偷': '盗', '傻': '愚', '关': '関', '兴': '興', '写': '書', '击': '撃', '刚': '剛', '别': '別', '前': '前', '剧': '劇', '劝': '勧', '办': '弁', '动': '動', '单': '単', '历': '歴', '厉': '烈', '发': '発', '变': '変', '另': '別', '叨': '、', '叫': '叫', '右': '右', '后': '後', '吓': '脅', '吗': '？', '吧': '、', '听': '聴', '吱': '、', '吵': '騒', '吼': '叫', '呃': '、', '呆': '呆', '呗': '、', '员': '員', '呜': '、', '呢': '？', '呵': '、', '咋': '怎', '咔': '、', '咕': '、', '咖': '珈', '咚': '、', '咦': '、', '咱': '我', '哄': '慰', '哇': '、', '响': '響', '哎': '、', '哟': '、', '哦': '、', '哪': '那', '哼': '、', '唉': '、', '唠': '、', '啊': '、', '啡': '琲', '啥': '何', '啦': '、', '啪': '、', '喂': '、', '喊': '叫', '喔': '、', '喝': '飲', '喲': '、', '嗒': '、', '嗨': '、', '嗯': '、', '嘁': '、', '嘈': '騒', '嘎': '、', '嘛': '、', '嘟': '、', '嘻': '、', '嘿': '、', '噗': '、', '噜': '、', '噢': '、', '嚎': '叫', '嚷': '叫', '囊': '袋', '团': '団', '园': '園', '围': '囲', '图': '図', '圆': '円', '场': '場', '圾': '芥', '块': '塊', '垃': '芥', '垫': '敷', '处': '処', '备': '備', '外': '外', '够': '足', '头': '頭', '夸': '褒', '奶': '乳', '她': '他', '妈': '母', '娱': '娯', '它': '其', '实': '実', '宫': '宮', '宽': '寛', '对': '對', '岁': '歳', '左': '左', '师': '師', '带': '帯', '帮': '助', '应': '応', '庞': '巨', '开': '開', '弄': '弄', '张': '張', '强': '強', '录': '録', '怕': '恐', '总': '総', '恶': '悪', '您': '汝', '惊': '驚', '愣': '呆', '慌': '慌', '憋': '耐', '懂': '解', '懵': '呆', '户': '戸', '扔': '投', '扛': '担', '扭': '捩', '扯': '引', '把': '把', '抱': '抱', '拉': '引', '拎': '提', '拖': '曳', '拧': '捩', '拼': '争', '拽': '引', '挡': '防', '挪': '移', '捏': '握', '捡': '拾', '换': '換', '掏': '取', '推': '押', '掰': '折', '握': '握', '揭': '暴', '搂': '抱', '搐': '痙', '搞': '弄', '摁': '押', '摇': '揺', '摔': '倒', '摸': '触', '撑': '支', '撞': '衝', '支': '支', '旁': '傍', '时': '時', '晚': '晩', '替': '代', '条': '条', '查': '調', '样': '樣', '根': '根', '桌': '机', '欢': '歓', '步': '歩', '每': '毎', '氧': '酸', '沉': '沈', '泽': '沢', '渐': '漸', '渲': '演', '渴': '渇', '满': '満', '炫': '耀', '点': '点', '烦': '煩', '爱': '愛', '爸': '父', '牵': '引', '现': '現', '甩': '振', '电': '電', '盯': '見', '眯': '閉', '睁': '開', '睡': '眠', '睬': '顧', '瞅': '見', '瞧': '見', '瞪': '見', '确': '確', '碰': '当', '碳': '炭', '离': '離', '种': '種', '篮': '籃', '类': '類', '糕': '餅', '紧': '緊', '红': '紅', '约': '約', '级': '級', '线': '線', '练': '練', '终': '終', '经': '経', '结': '結', '给': '給', '绝': '絶', '继': '継', '续': '続', '缘': '縁', '罗': '羅', '胜': '勝', '胳': '腕', '脏': '汚', '脑': '脳', '脖': '首', '脸': '顔', '节': '節', '茬': '、', '虽': '雖', '见': '見', '视': '視', '觉': '覚', '认': '認', '让': '譲', '讪': '嘲', '记': '記', '许': '許', '论': '論', '识': '識', '诉': '訴', '试': '試', '话': '話', '该': '該', '语': '語', '说': '説', '请': '請', '读': '読', '课': '課', '谁': '誰', '谈': '談', '谎': '嘘', '谢': '謝', '赶': '追', '趟': '度', '趴': '伏', '跑': '走', '跟': '共', '踢': '蹴', '踩': '踏', '蹭': '擦', '躲': '避', '躺': '臥', '车': '車', '转': '転', '轻': '軽', '较': '較', '辆': '両', '边': '辺', '过': '過', '运': '運', '还': '還', '这': '這', '进': '進', '远': '遠', '连': '連', '选': '選', '逛': '歩', '酗': '酔', '酱': '醤', '醒': '醒', '里': '裡', '钟': '鐘', '钱': '銭', '错': '錯', '长': '長', '门': '門', '问': '問', '闲': '暇', '间': '間', '阂': '隔', '队': '隊', '难': '難', '顾': '顧', '题': '題', '风': '風', '飞': '飛', '饭': '飯', '饮': '飲', '饱': '飽', '饿': '餓', '马': '馬', '骂': '罵', '骗': '欺', '黑': '黒', '－': '-', '～': '〜'
}

def in_jis(ch: str) -> bool:
    """能否用 iso2022_jp 编码 = 是否落在 JIS X 0208 / JIS X 0201（日文字库基本都有）。"""
    try:
        ch.encode('iso2022_jp')
        return True
    except UnicodeEncodeError:
        return False

def is_cjk(cp: int) -> bool:
    return (0x4E00 <= cp <= 0x9FFF) or (0x3000 <= cp <= 0x303F) or (0xFF00 <= cp <= 0xFFEF)

def iter_runs(data: bytes):
    """遍历「u16 字符数 + UTF-16LE 正文」结构的文本段。"""
    n = len(data); i = 0
    while i < n - 6:
        ln = data[i] | (data[i + 1] << 8)
        if 1 <= ln <= 400:
            end = i + 2 + ln * 2
            if end + 2 <= n:
                try:
                    s = data[i + 2:end].decode('utf-16-le')
                except UnicodeDecodeError:
                    s = None
                if s and all(is_cjk(ord(c)) or 0x20 <= ord(c) <= 0x7E
                             or 0x3040 <= ord(c) <= 0x30FF or ord(c) in (9, 10, 13) for c in s):
                    if sum(1 for c in s if is_cjk(ord(c))) >= 2:
                        yield i, s
                        i = end
                        continue
        i += 1

def build_mapping(chars):
    cc = opencc.OpenCC('s2t') if opencc else None
    mapping, via = {}, collections.Counter()
    for ch in chars:
        t = MANUAL.get(ch)
        if t and in_jis(t):
            mapping[ch] = t; via['manual'] += 1; continue
        if cc:
            t2 = cc.convert(ch)
            if len(t2) == 1 and in_jis(t2):
                mapping[ch] = t2; via['s2t'] += 1; continue
        mapping[ch] = '・'; via['fallback'] += 1
    return mapping, via

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    src = Path(args.input)
    data = src.read_bytes()
    runs = list(iter_runs(data))
    chars = {c for _, s in runs for c in s if not in_jis(c)}
    mapping, via = build_mapping(chars)
    print(f'input      : {src} ({len(data):,} B)')
    print(f'text runs  : {len(runs)}')
    print(f'missing    : {len(chars)} unique chars')
    print(f'mapping    : manual {via["manual"]}, s2t {via["s2t"]}, fallback {via["fallback"]}')
    if args.check:
        return

    out = bytearray(data); changed = 0
    for start, s in runs:
        base = start + 2
        for k, ch in enumerate(s):
            rep = mapping.get(ch)
            if rep and rep != ch:
                v = ord(rep)
                out[base + k * 2] = v & 0xFF
                out[base + k * 2 + 1] = (v >> 8) & 0xFF
                changed += 1
    print(f'replaced   : {changed} chars')
    assert len(out) == len(data), 'length must not change'

    dst = Path(args.output or (src.with_suffix(src.suffix + '.v39')))
    dst.write_bytes(bytes(out))

    left = {c for _, s in iter_runs(bytes(out)) for c in s if not in_jis(c)}
    print(f'output     : {dst} ({len(out):,} B)')
    print(f'sha256     : {hashlib.sha256(bytes(out)).hexdigest()}')
    print(f'after      : {len(left)} missing chars' + ('  (OK)' if not left else '  ← 仍需补表'))

if __name__ == '__main__':
    main()
