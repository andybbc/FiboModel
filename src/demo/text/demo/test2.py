"""
重新封装了XGBoost的Rank方法
https://www.jianshu.com/p/9caef967ec0a
跑通
"""


import numpy as np
from sklearn.utils import check_X_y, check_array
from xgboost_test_package import DMatrix, train
from xgboost_test_package import XGBModel
from xgboost_test_package.sklearn import _objective_decorator
from scipy import sparse


class XGBRanker(XGBModel):
    __doc__ = """Implementation of sklearn API for XGBoost Ranking
           """ + '\n'.join(XGBModel.__doc__.split('\n')[2:])

    def __init__(self, max_depth=3, learning_rate=0.1, n_estimators=100,
                 silent=True, objective="rank:pairwise", booster='gbtree',
                 n_jobs=-1, nthread=None, gamma=0, min_child_weight=1, max_delta_step=0,
                 subsample=1, colsample_bytree=1, colsample_bylevel=1,
                 reg_alpha=0, reg_lambda=1, scale_pos_weight=1,
                 base_score=0.5, random_state=0, seed=None, missing=None, **kwargs):

        super(XGBRanker, self).__init__(max_depth, learning_rate,
                                        n_estimators, silent, objective, booster,
                                        n_jobs, nthread, gamma, min_child_weight, max_delta_step,
                                        subsample, colsample_bytree, colsample_bylevel,
                                        reg_alpha, reg_lambda, scale_pos_weight,
                                        base_score, random_state, seed, missing)

    def _preprare_data_in_groups(self, X, y=None, sample_weights=None):
        """
        Takes the first column of the feature Matrix X given and
        transforms the data into groups accordingly.
        Parameters
        ----------
        X : (2d-array like) Feature matrix with the first column the group label
        y : (optional, 1d-array like) target values
        sample_weights : (optional, 1d-array like) sample weights
        Returns
        -------
        sizes: (1d-array) group sizes
        X_features : (2d-array) features sorted per group
        y : (None or 1d-array) Target sorted per group
        sample_weights: (None or 1d-array) sample weights sorted per group
        """
        if sparse.issparse(X):
            group_labels = X.getcol(0).toarray()[:, 0]
        else:
            group_labels = X[:, 0]

        group_indices = group_labels.argsort()

        group_labels = group_labels[group_indices]
        _, sizes = np.unique(group_labels, return_counts=True)
        X_sorted = X[group_indices]
        X_features = X_sorted[:, 1:]

        if y is not None:
            y = y[group_indices]

        if sample_weights is not None:
            sample_weights = sample_weights[group_indices]

        return sizes, X_sorted, X_features, y, sample_weights

    def fit(self, X, y, sample_weight=None, eval_set=None, eval_metric=None,
            early_stopping_rounds=None, verbose=True, xgb_model=None):
        """
        Fit the gradient boosting model
        Parameters
        ----------
        X : array_like
            Feature matrix with the first feature containing a group indicator
        y : array_like
            Labels
        sample_weight : array_like
            instance weights
        eval_set : list, optional
            A list of (X, y) tuple pairs to use as a validation set for
            early-stopping
        eval_metric : str, callable, optional
            If a str, should be a built-in evaluation metric to use. See
            doc/parameter.md. If callable, a custom evaluation metric. The call
            signature is func(y_predicted, y_true) where y_true will be a
            DMatrix object such that you may need to call the get_label
            method. It must return a str, value pair where the str is a name
            for the evaluation and value is the value of the evaluation
            function. This objective is always minimized.
        early_stopping_rounds : int
            Activates early stopping. Validation error needs to decrease at
            least every <early_stopping_rounds> round(s) to continue training.
            Requires at least one item in evals.  If there's more than one,
            will use the last. Returns the model from the last iteration
            (not the best one). If early stopping occurs, the model will
            have three additional fields: bst.best_score, bst.best_iteration
            and bst.best_ntree_limit.
            (Use bst.best_ntree_limit to get the correct value if num_parallel_tree
            and/or num_class appears in the parameters)
        verbose : bool
            If `verbose` and an evaluation set is used, writes the evaluation
            metric measured on the validation set to stderr.
        xgb_model : str
            file name of stored xgb model or 'Booster' instance Xgb model to be
            loaded before training (allows training continuation).
        """

        X, y = check_X_y(X, y, accept_sparse=False, y_numeric=True)

        sizes, _, X_features, y, _ = self._preprare_data_in_groups(X, y)

        params = self.get_xgb_params()

        if callable(self.objective):
            obj = _objective_decorator(self.objective)
            # Dummy, Not used when custom objective is given
            params["objective"] = "binary:logistic"
        else:
            obj = None

        evals_result = {}
        feval = eval_metric if callable(eval_metric) else None
        if eval_metric is not None:
            if callable(eval_metric):
                eval_metric = None
            else:
                params.update({'eval_metric': eval_metric})

        if sample_weight is not None:
            train_dmatrix = DMatrix(X_features, label=y, weight=sample_weight,
                                    missing=self.missing)
        else:
            train_dmatrix = DMatrix(X_features, label=y,
                                    missing=self.missing)

        train_dmatrix.set_group(sizes)

        self._Booster = train(params, train_dmatrix,
                              self.n_estimators,
                              early_stopping_rounds=early_stopping_rounds,
                              evals_result=evals_result, obj=obj, feval=feval,
                              verbose_eval=verbose, xgb_model=xgb_model)

        if evals_result:
            for val in evals_result.items():
                evals_result_key = list(val[1].keys())[0]
                evals_result[val[0]][evals_result_key] = val[1][evals_result_key]
            self.evals_result = evals_result

        if early_stopping_rounds is not None:
            self.best_score = self._Booster.best_score
            self.best_iteration = self._Booster.best_iteration
            self.best_ntree_limit = self._Booster.best_ntree_limit

        return self

    def predict(self, X, output_margin=False, ntree_limit=0):
        sizes, _, X_features, _, _ = self._preprare_data_in_groups(X)

        test_dmatrix = DMatrix(X_features, missing=self.missing)
        test_dmatrix.set_group(sizes)
        rank_values = self.get_booster().predict(test_dmatrix,
                                                 output_margin=output_margin,
                                                 ntree_limit=ntree_limit)
        return rank_values


if __name__ == "__main__":
    # 例子和分组
    CASE_NUM = 20
    GROUPS_NUM = 4

    if CASE_NUM % GROUPS_NUM != 0:
        raise ValueError('Cases should be splittable into equal groups.')

    # Generate some sample data to illustrate ranking
    # 生成 [20, 4]的矩阵，样本的特征
    X_features = np.random.rand(CASE_NUM, 4)
    # [0, low) 区间，数组大小是 CASE_NUM，返回Int整型数，预测值
    y = np.random.randint(5, size=CASE_NUM)
    # 范围是从[0,4)，重复5次
    X_groups = np.arange(0, GROUPS_NUM).repeat(CASE_NUM/GROUPS_NUM)

    print("X="+str(X_features))
    print("y="+str(y))

    # Append the group labels as a first axis to the features matrix
    # this is how the algorithm can distinguish between the different
    # groups
    X = np.concatenate([X_groups[:, None], X_features], axis=1)


    # objective = rank:pairwise(default).
    # Although rank:ndcg is also available,  rank:ndcg(listwise) is much worse than pairwise.
    # So ojective is always rank:pairwise whatever you write.
    ranker = XGBRanker(n_estimators=150, learning_rate=0.1, subsample=0.9)


    ranker.fit(X, y, eval_metric=['ndcg', 'map@5-'])
    y_predict = ranker.predict(X)

    print("predict:"+str(y_predict))
    print("type(y_predict):"+str(type(y_predict)))