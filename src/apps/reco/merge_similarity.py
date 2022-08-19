import sys

sys.path.append('../')

import gflags
from combine.merge_similarity import MergeSimilaryityFile

Flags = gflags.FLAGS

gflags.DEFINE_string('input_path1', '../../data/collaborative/out.txt', '文件1')
gflags.DEFINE_string('input_path2', '../../data/collaborative/out2.txt', '文件2')
gflags.DEFINE_string('out_path', '../../data/collaborative/out3.txt', '输出文件路径')
gflags.DEFINE_float('rate1', 0.7, '文件1权重')
gflags.DEFINE_float('rate2', 0.3, '文件2权重')

if __name__ == '__main__':
    gflags.FLAGS(sys.argv)
    input_path1 = Flags.input_path1
    input_path2 = Flags.input_path2
    out_path = Flags.out_path
    rate1 = Flags.rate1
    rate2 = Flags.rate2
    fileOperation = MergeSimilaryityFile(input_path1, input_path2, out_path, rate1, rate2)
    fileOperation.merge()
