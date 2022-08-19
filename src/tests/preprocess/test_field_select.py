from preprocess.field_select import FieldSelect

if __name__ == '__main__':
    dic_config = {
        "logger": 1,
        "origin_path": "../../../data/xgb_lr_demo_new/new_no_request_id/new_sample.csv",
        "split_cols_file_path": "../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_select_col.csv",
        "encode_file_path": "../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_encode.csv",
        "out_label_path": "../../../data/xgb_lr_demo_new/new_no_request_id/label.out",
        "out_label_detail_path": "../../../data/xgb_lr_demo_new/new_no_request_id/label_detail.json",
        "out_one_hot_encoder_path": "../../../data/xgb_lr_demo_new/new_no_request_id/one_hot_encode.out",
        "file_separator": ",",
        "train_file_path": "../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_train.csv",
        "vali_file_path": "../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_vali.csv",
        "test_file_path": "../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_test.csv",
        "need_label_encode_cols_num": 3,
        "select_cols": [0, 1, 11, 12, 13]
    }
    fp = FieldSelect(dic_config)

    # fp.split_train_cols()
    fp.label_encode_data()
    fp.split_data()
    # fp.split_predict_cols()
