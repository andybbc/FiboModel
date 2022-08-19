package xgboost2Pmml.demo;

import org.dmg.pmml.FieldName;
import org.dmg.pmml.PMML;
import org.dmg.pmml.tree.TreeModel;
import org.jpmml.evaluator.*;

import java.io.*;
import java.util.*;
import java.util.List;

/**
 * @description:
 * @author: malichun
 * @time: 2021/5/14/0014 16:42
 */
public class Classification {
    public static void main(String[] args) throws Exception {
        //模型路径
        String pathxml =  "E:\\gitdir\\projects\\untitled\\src\\main\\java\\xgboost2Pmml\\demo\\data\\xgboost.pmml";
        //传入模型特征数据
        Map<String, Double> map = new HashMap<String, Double>();
        map.put("x1", 5.1);
        map.put("x2", 3.5);
        map.put("x3", 0.4);
        map.put("x4", 0.2);
        //模型预测
        predictLrHeart(map, pathxml);
    }

    public static void predictLrHeart(Map<String, Double> irismap, String pathxml) throws Exception {
        PMML pmml;
        File file = new File(pathxml);
        InputStream inputStream = new FileInputStream(file);
        try (InputStream is = inputStream) {
            pmml = org.jpmml.model.PMMLUtil.unmarshal(is);

            ModelEvaluatorFactory modelEvaluatorFactory = ModelEvaluatorFactory.newInstance();
            ModelEvaluator<?> modelEvaluator = modelEvaluatorFactory.newModelEvaluator(pmml);
            Evaluator evaluator = (Evaluator) modelEvaluator;

            List<InputField> inputFields = evaluator.getInputFields();
            Map<FieldName, FieldValue> argements = new LinkedHashMap<>();
            for (InputField inputField : inputFields) {
                FieldName inputFieldName = inputField.getName();
                Object raeValue = irismap.get(inputFieldName.getValue());
                FieldValue inputFieldValue = inputField.prepare(raeValue);
                argements.put(inputFieldName, inputFieldValue);
            }
            Map<FieldName, ?> results = evaluator.evaluate(argements);
            List<TargetField> targetFields = evaluator.getTargetFields();
            for (TargetField targetField : targetFields) {
                FieldName targetFieldName = targetField.getName();
                Object targetFieldValue = results.get(targetFieldName);
//                System.out.println("target: " + targetFieldName.getValue());
                System.out.println(targetFieldValue);
            }
        }
    }
}
