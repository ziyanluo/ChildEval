turn=$1          # 第一个参数是数值
shift              # 移除第一个参数
nums=("$@")       # 剩余的参数组成数组

data_dir=/root/work/data_inner/implicit_data_0828
#turn=5
input_data_dir=${data_dir}/gen_sft_implicit_data
output_data_dir=${data_dir}/evals/gen_eval_gen_sft_implicit_data
mkdir ${output_data_dir}
#nums=(0)
for num in "${nums[@]}";do
    echo 'num: '$num
    infile=${input_data_dir}/test_${num}.json
    outfile=${output_data_dir}/test_${num}.json
    echo 'outfile: '$outfile
    rm -rf $outfile
    python -u evaluate_accuracy_name.py --key gen_response --infile $infile --outfile $outfile --line_nums 0
done
