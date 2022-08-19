package xgboost2Pmml.product;

import org.dmg.pmml.FieldName;
import org.dmg.pmml.PMML;
import org.dmg.pmml.tree.TreeModel;
import org.jpmml.evaluator.*;

import java.io.*;
import java.util.*;

public class PMMLPredictionOne {

    public static PMML pmml;
    public static Evaluator evaluator;
    static List<InputField> inputFields;

    public static void main(String[] args) throws Exception {


        String  pathxml="E:\\gitdir\\projects\\untitled\\src\\main\\java\\xgboost2Pmml\\product\\data\\xgb_model.pkl_3_pipeline";
        beforeDo(pathxml);

        String arrStr = "[[26,32,344,1,1,1570,3475,1021 ]]";

        String[] arr = arrStr.replace("[","").replace("]","").replace(" ","").split(",");

        Map<String, Integer>  map=new HashMap<>();
//        map.put("1", 14);
//        map.put("2", 15);
//        map.put("3", 203);
//        map.put("4", 1);
//        map.put("5", 1);
//        map.put("6", 1000);
//        map.put("7", 2788);
//        map.put("8", 13);
//        map.put("9", 853);

//        map.put("1", 16);
//        map.put("2", 15);
//        map.put("3", 60);
//        map.put("4", 1);
//        map.put("5", 4);
//        map.put("6", 714);
//        map.put("7", 3085);
//        map.put("9", 4029);

        for(int i =0;i<arr.length;i++){
            map.put(String.valueOf(i+1), Integer.valueOf(arr[i]));
        }
        double res = predictLrHeart(map, pathxml);
        System.out.println(res);

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
            Object rawValue = irismap.get(Integer.valueOf(inputFieldName.getValue()));
            FieldValue inputFieldValue = inputField.prepare(rawValue);
            arguments.put(inputFieldName, inputFieldValue);
        }

        Map<FieldName, ?> results = evaluator.evaluate(arguments);
        List<TargetField> targetFields = evaluator.getTargetFields();
        TargetField targetField1 = targetFields.get(0);
        ProbabilityDistribution res = (ProbabilityDistribution)results.get(targetField1.getName());
        return res.getProbability("1");
    }

    public static double predictLrHeart(Map<String, Integer> irismap,String  pathxml)throws Exception {

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
            ProbabilityDistribution res = (ProbabilityDistribution)results.get(targetField1.getName());
            return res.getProbability("1");
        }
    }
}
