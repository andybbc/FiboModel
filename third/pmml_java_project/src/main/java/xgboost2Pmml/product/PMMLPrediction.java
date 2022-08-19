package xgboost2Pmml.product;

import java.io.*;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.dmg.pmml.FieldName;
import org.dmg.pmml.PMML;
import org.dmg.pmml.tree.TreeModel;
import org.jpmml.evaluator.*;

public class PMMLPrediction {

    public static PMML pmml;
    public static Evaluator evaluator;
    static List<InputField> inputFields;

    public static void main(String[] args) throws Exception {
//        String  pathxml="E:\\gitdir\\projects\\untitled\\src\\main\\java\\xgboost2Pmml\\product\\data\\xgboost.pmml";
//        Map<Integer, Integer>  map=new HashMap<>();
//        map.put(1, 14);
//        map.put(2, 17);
//        map.put(3, 339);
//        map.put(4, 2);
//        map.put(5, 5);
//        map.put(6, 404);
//        map.put(7, 2549);
//        map.put(8, 12);
//        map.put(9, 2650);
//        double res = predictLrHeart(map, pathxml);
//        System.out.println(res);

        beforeDo("E:\\gitdir\\learn_projects\\python_projects\\algorithm2\\src\\tests\\simple\\product\\data\\xgboost.pmml");
//        beforeDo("E:\\gitdir\\projects\\untitled\\src\\main\\java\\xgboost2Pmml\\product\\data\\xgb_model.pkl_3_pipeline");
        BufferedReader br = new BufferedReader(new FileReader(new File("E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\predict.txt")));
        BufferedWriter bw = new BufferedWriter(new FileWriter(new File("E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\predict_res.txt")));
        String line = null;
        while((line = br.readLine())!=null){
            String[] arr = line.split(",");
            Map<String, Integer>  map1=new HashMap<>();
            for(int i=1;i<=arr.length;i++){
                map1.put(String.valueOf(i),Integer.parseInt(arr[i-1]));
            }
            double res = predict(map1);
            bw.write(String.valueOf(res));
            bw.newLine();
            bw.flush();
        }

//        double res = predict(map);
//        System.out.println(res);
        bw.close();
        br.close();

    }

    public static void beforeDo(String  pathxml) throws Exception{
        pmml = org.jpmml.model.PMMLUtil.unmarshal(new FileInputStream(pathxml));
        ModelEvaluatorFactory modelEvaluatorFactory = ModelEvaluatorFactory
                .newInstance();
        ModelEvaluator<?> modelEvaluator = modelEvaluatorFactory
                .newModelEvaluator(pmml);
        evaluator = (Evaluator) modelEvaluator;
        inputFields = evaluator.getInputFields();

    }

    public static double predict(Map<String, Integer> irismap){
        // 过模型的原始特征，从画像中获取数据，作为模型输入
        Map<FieldName, FieldValue> arguments = new LinkedHashMap<>();
        for (InputField inputField : inputFields) {
            FieldName inputFieldName = inputField.getName();
            Object rawValue = irismap.get(inputFieldName.getValue());
            FieldValue inputFieldValue = inputField.prepare(rawValue);
            arguments.put(inputFieldName, inputFieldValue);
        }

        Map<FieldName, ?> results = evaluator.evaluate(arguments);
        List<TargetField> targetFields = evaluator.getTargetFields();
        TargetField targetField1 = targetFields.get(0);
        ProbabilityDistribution res = (org.jpmml.evaluator.ProbabilityDistribution)results.get(targetField1.getName());
        return res.getProbability("1");
    }

    public static double predictLrHeart(Map<Integer, Integer> irismap,String  pathxml)throws Exception {

        PMML pmml;
        // 模型导入
        File file = new File(pathxml);
        InputStream inputStream = new FileInputStream(file);
        try (InputStream is = inputStream) {
            pmml = org.jpmml.model.PMMLUtil.unmarshal(is);

            ModelEvaluatorFactory modelEvaluatorFactory = ModelEvaluatorFactory
                    .newInstance();
            ModelEvaluator<?> modelEvaluator = modelEvaluatorFactory
                    .newModelEvaluator(pmml);
            Evaluator evaluator = (Evaluator) modelEvaluator;

            List<InputField> inputFields = evaluator.getInputFields();
            // 过模型的原始特征，从画像中获取数据，作为模型输入
            Map<FieldName, FieldValue> arguments = new LinkedHashMap<>();
            for (InputField inputField : inputFields) {
                FieldName inputFieldName = inputField.getName();
                Object rawValue = irismap.get(Integer.valueOf(inputFieldName.getValue()));
                FieldValue inputFieldValue = inputField.prepare(rawValue);
                arguments.put(inputFieldName, inputFieldValue);
            }

            Map<FieldName, ?> results = evaluator.evaluate(arguments);
            List<TargetField> targetFields = evaluator.getTargetFields();
            TargetField targetField1 = targetFields.get(0);
            ProbabilityDistribution res = (org.jpmml.evaluator.ProbabilityDistribution)results.get(targetField1.getName());
            return res.getProbability("1");
        }
    }
}
