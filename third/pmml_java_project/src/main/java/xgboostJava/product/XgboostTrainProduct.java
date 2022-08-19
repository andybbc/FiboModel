package xgboostJava.product;

import ml.dmlc.xgboost4j.java.Booster;
import ml.dmlc.xgboost4j.java.DMatrix;
import ml.dmlc.xgboost4j.java.XGBoost;
import ml.dmlc.xgboost4j.java.XGBoostError;

import java.util.HashMap;
import java.util.Map;

/**
 * @description: https://blog.csdn.net/qq_24834541/article/details/103797256
 * @author: malichun
 * @time: 2021/4/30/0030 13:58
 */
public class XgboostTrainProduct {
    private static DMatrix trainMat = null;
    private static DMatrix testMat = null;
    //传入参数
    public static void main(String [] args) throws XGBoostError {
//        String trainFile = args[0];
//        String testFile = args[1];
//        String outModelPath = args[2];

        String trainFile="E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\train.libsvm";
        String testFile ="E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\test.libsvm";
        String outModelPath="E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\out_test.bin";

        try {
//            trainMat = new DMatrix("/data/algorithm/test/train.txt");
            trainMat = new DMatrix(trainFile);
        } catch (XGBoostError xgBoostError) {
            xgBoostError.printStackTrace();
        }
        try {
//            testMat = new DMatrix("/data/algorithm/test/test.txt");
            testMat = new DMatrix(testFile);
        } catch (XGBoostError xgBoostError) {
            xgBoostError.printStackTrace();
        }

        Map<String, Object> params = new HashMap<String, Object>() {
            {
                put("learning_rate",0.1); //学习率，过大收敛不了，小了收敛慢,eta
                put("n_estimator",200);
                put("max_depth", 6);  //# 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
                put("scale_pos_weight",2.5); //# 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样本比例为1:10时，scale_pos_weight=10。
//                put("scale_pos_weight",4);
                put("min_child_weight",0.9); //# 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
                put("gamma",0.1); //# 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
                put("subsample",0.9); //# 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
//                put("colsample_bylevel",0.5);  //随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
                put("objective", "binary:logistic"); //# 二分类的问题,概率
                put("n_jobs",4); //# 并行线程数
                put("seed",27);
                put("nthread",-1);

                put("tree_method","exact"); // approx或者 exact

//                put("eval_metric", "logloss");
//                put("eta", 0.3);

            }
        };

        Map<String, DMatrix> watches = new HashMap<String, DMatrix>() {
            {
                put("train",trainMat);
                put("test", testMat);
            }
        };
        try {
            Booster booster = XGBoost.train(trainMat, params, 100, watches, null, null);
            booster.saveModel(outModelPath);
//            booster.saveModel("/data/algorithm/test/model.bin");


        } catch (XGBoostError xgBoostError) {
            xgBoostError.printStackTrace();
        }
    }


//    public static void main(String [] args) throws XGBoostError {
//
//        try {
////            trainMat = new DMatrix("/data/algorithm/test/train.txt");
//            trainMat = new DMatrix("E:\\gitdir\\projects\\untitled\\src\\main\\resources\\train.txt");
//        } catch (XGBoostError xgBoostError) {
//            xgBoostError.printStackTrace();
//        }
//        try {
////            testMat = new DMatrix("/data/algorithm/test/test.txt");
//            testMat = new DMatrix("E:\\gitdir\\projects\\untitled\\src\\main\\resources\\test.txt");
//        } catch (XGBoostError xgBoostError) {
//            xgBoostError.printStackTrace();
//        }
//
//        Map<String, Object> params = new HashMap<String, Object>() {
//            {
//                put("eta", 1.0);
//                put("max_depth", 3);
//                put("objective", "binary:logistic");
//                put("eval_metric", "logloss");
//            }
//        };
//
//        Map<String, DMatrix> watches = new HashMap<String, DMatrix>() {
//            {
//                put("train",trainMat);
//                put("test", testMat);
//            }
//        };
//        int nround = 10;
//        try {
//            Booster booster = XGBoost.train(trainMat, params, nround, watches, null, null);
//            booster.saveModel("E:\\gitdir\\projects\\untitled\\src\\main\\resources\\model.bin");
////            booster.saveModel("/data/algorithm/test/model.bin");
//
//
//        } catch (XGBoostError xgBoostError) {
//            xgBoostError.printStackTrace();
//        }
//    }
}
