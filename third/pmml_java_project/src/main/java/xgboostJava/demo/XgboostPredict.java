package xgboostJava.demo;
import ml.dmlc.xgboost4j.java.Booster;
import ml.dmlc.xgboost4j.java.DMatrix;
import ml.dmlc.xgboost4j.java.XGBoost;
import ml.dmlc.xgboost4j.java.XGBoostError;

/**
 * @description:
 * @author: malichun
 * @time: 2021/4/30/0030 16:31
 */
public class XgboostPredict {
    // 传入参数
    public static void main(String [] args) throws XGBoostError {

        float[] data = new float[]{14f,17f,339f,2f,1f,808f,4758f,12f,1295f};
        int nrow = 1;
        int ncol = 4;
        float missing = 0.0f;
        DMatrix dmat = new DMatrix(data, nrow, ncol, missing);
//        Booster booster = XGBoost.loadModel("src/main/resources/model.bin");
        Booster booster = XGBoost.loadModel("src/main/resources/out.pkl");
        float[][] predicts = booster.predict(dmat);
        for (float[] array : predicts) {
            for (float values : array) {
                System.out.print(values + " ");
            }
            System.out.println();
        }

    }
//
//   // 生产数据
//    public static void main(String [] args) throws XGBoostError {
//        float[] data = new float[]{14f,17f,339f,2f,1f,808f,4758f,12f,1295f};
//        int nrow = 1;
//        int ncol = 4;
//        float missing = 0.0f;
//        DMatrix dmat = new DMatrix(data, nrow, ncol, missing);
////        Booster booster = XGBoost.loadModel("src/main/resources/model.bin");
//        Booster booster = XGBoost.loadModel("src/main/resources/xgb_model.pkl_2");
//        float[][] predicts = booster.predict(dmat);
//        for (float[] array : predicts) {
//            for (float values : array) {
//                System.out.print(values + " ");
//            }
//            System.out.println();
//        }
//
//    }

    //demo
//    public static void main(String [] args) throws XGBoostError {
//        float[] data = new float[]{5.2f, 3.5f, 1.5f, 0.2f};
//        int nrow = 1;
//        int ncol = 4;
//        float missing = 0.0f;
//        DMatrix dmat = new DMatrix(data, nrow, ncol, missing);
//        Booster booster = XGBoost.loadModel("src/main/resources/model.bin");
//        float[][] predicts = booster.predict(dmat);
//        for (float[] array : predicts) {
//            for (float values : array) {
//                System.out.print(values + " ");
//            }
//            System.out.println();
//        }
//
//    }
}
