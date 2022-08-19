package xgboostJava.demo2;

//standard packages
import java.util.HashMap;
import java.io.IOException;
import java.util.Arrays;
import java.io.File;

//xgboost
import ml.dmlc.xgboost4j.java.DMatrix;
import ml.dmlc.xgboost4j.java.XGBoost;
import ml.dmlc.xgboost4j.java.XGBoostError;
import ml.dmlc.xgboost4j.java.Booster;
//import ml.dmlc.xgboost4j.java.

public class XGBoostTest {

    public void print_prediction(float[][] prediction) {
        for (float[] testRow : prediction) {
            for (float elem : testRow) {
                System.out.print("|" + elem + "|");
            }
            System.out.println();
        }
    }

    public void save_model(Booster booster) {
        File path = new File("./model");
        if(!path.exists() ) {
            path.mkdirs();
        }
        try {
            String modelPath = "model/xgb.model";
            booster.saveModel(modelPath);
        } catch(XGBoostError  error){
            System.out.println(error.toString());
        }
    }

    public Booster load_model() throws XGBoostError {
        return XGBoost.loadModel("./model/xgb.model");
    }

    public void boost_from_prediction() throws IOException, XGBoostError {
        System.out.println("start running example to start from a initial prediction");

        DMatrix testMat = new DMatrix("data/agaricus.txt.test");
        Booster booster = load_model();
        if(booster == null)
        {
            DMatrix trainMat = new DMatrix("data/agaricus.txt.train");
            // specify parameters
            HashMap<String, Object> params = new HashMap<String, Object>();
            params.put("eta", 1.0);
            params.put("max_depth", 2);
            params.put("silent", 1);
            params.put("objective", "binary:logistic");

            // specify watchList
            HashMap<String, DMatrix> watches = new HashMap<String, DMatrix>();
            watches.put("train", trainMat);
            watches.put("test", testMat);

            // train xgboost for 1 round
            // Booster booster = XGBoost.train(trainMat, params, 1, watches,
            // null, null);
            // float[][] trainPred = booster.predict(trainMat, true);
            // float[][] testPred = booster.predict(testMat, true);

            // trainMat.setBaseMargin(trainPred);
            // testMat.setBaseMargin(testPred);
            // System.out.println("result of running from initial prediction");
            // print_prediction(testPred);

            // System.out.println("result of running from initial prediction");
            booster = XGBoost.train(trainMat, params, 2, watches, null, null);
        }

        System.out.println("result of running from initial prediction");
        float[][] pred = booster.predict(testMat);
        System.out.println("|" + pred[0][0] + "|");

        DMatrix data = new DMatrix("data/victor_test.test");
        float[][] ypredict = booster.predict(data);

        System.out.println("result of running from victor prediction");
        print_prediction(ypredict);
//        save_model(booster);
    }

    public void cross_validation() throws IOException, XGBoostError {
        System.out.println("Hello world");
        String workingDir = System.getProperty("user.dir");
        System.out.println("Current working directory : " + workingDir);

        DMatrix trainMat = new DMatrix("data/agaricus.txt.train");
        HashMap<String, Object> params = new HashMap<String, Object>();

        params.put("eta", 1.0);
        params.put("max_depth", 3);
        params.put("silent", 1);
        params.put("nthread", 6);
        params.put("objective", "binary:logistic");
        params.put("gamma", 1.0);
        params.put("eval_metric", "error");

        // do 5-fold cross validation
        int round = 2;
        int nfold = 5;
        // set additional eval_metrics
        String[] metrics = null;

        String[] evalHist = XGBoost.crossValidation(trainMat, params, round, nfold, metrics, null, null);
        // XGBoost.train(trainMat, params, round, nfold, null, null);
        Arrays.stream(evalHist).forEach(System.out::println);
    }

    public static void main(String[] args) throws IOException, XGBoostError {
        // TODO Auto-generated method stub
        XGBoostTest test = new XGBoostTest();
        test.boost_from_prediction();
    }
}