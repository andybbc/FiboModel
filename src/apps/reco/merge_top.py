import sys
sys.path.append('../')

import gflags
from combine.merge_top import FileMerge

Flags = gflags.FLAGS

gflags.DEFINE_string('input_path', '../../data/collaborative/out_origin.txt', '被合并文件路径')
gflags.DEFINE_string('ref_path', '../../data/top/all_top.txt', 'topN文件路径')
gflags.DEFINE_string('out_path', '../../data/final/out_final.txt', '输出文件路径')

if __name__ == '__main__':
    gflags.FLAGS(sys.argv)
    input_path = Flags.input_path
    ref_path = Flags.ref_path
    out_path = Flags.out_path
    fileOperation = FileMerge(input_path, ref_path, out_path)
    fileOperation.merge()
