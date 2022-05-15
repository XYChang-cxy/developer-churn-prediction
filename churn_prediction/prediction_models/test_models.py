from churn_prediction.prediction_models.train_svm import trainSVM,gridSearchForSVM
from churn_prediction.prediction_models.train_rf import trainRF,gridSearchForRF
from churn_prediction.prediction_models.train_xgboost import trainXGBoost,gridSearchForXGBoost
from churn_prediction.prediction_models.train_adaboost import trainMyAdaBoost,trainAdaBoost,gridSearchForAdaBoost


# precision偏小，表明loyaler被判定为churner的较多
# recall偏小，表明churner被判定为loyaler的较多

if __name__ == '__main__':
    balanced_data_dir = r'F:\MOOSE_cxy\developer_churn_prediction\churn_prediction\data_preprocess\data\repo_2\part_all\balanced_data'
    period_length = 120
    overlap_ratio = 0.0
    data_type_count = 12

    # trainSVM(balanced_data_dir, period_length, overlap_ratio, data_type_count)
    # trainRF(balanced_data_dir,period_length,overlap_ratio,data_type_count)
    # trainXGBoost(balanced_data_dir,period_length,overlap_ratio,data_type_count)
    # trainMyAdaBoost(balanced_data_dir,period_length,overlap_ratio,data_type_count,num_boost_round=100)
    # trainAdaBoost(balanced_data_dir,period_length,overlap_ratio,data_type_count)

    # scoring: accuracy、precision、recall、f1、f1_micro、f1_macro、roc_auc
    # gridSearchForSVM(balanced_data_dir, period_length, overlap_ratio, data_type_count,scoring='precision')
    # gridSearchForRF(balanced_data_dir, period_length, overlap_ratio, data_type_count,scoring='roc_auc')
    # gridSearchForAdaBoost(balanced_data_dir, period_length, overlap_ratio, data_type_count,scoring='f1_micro')

    period_length=30
    gridSearchForXGBoost(balanced_data_dir, period_length, overlap_ratio, data_type_count,scoring='f1_micro')