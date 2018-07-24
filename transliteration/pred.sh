#export LD_LIBRARY_PATH=/usr/loca/cuda/lib64:/usrlocal/cuda/extras/lib64:/usr/local/cuda/extras/CUPTI/lib64

export MODEL_DIR=`realpath $1`
export DEV_SOURCES=`realpath $2`

export PRED_FILE=`realpath $3`
export MODEL_CKP=`realpath $4`

cd seq2seq

python -m bin.infer \
  --tasks "
    - class: DecodeText" \
  --model_dir $MODEL_DIR \
  --checkpoint_path $MODEL_CKP \
  --input_pipeline "
    class: ParallelTextInputPipeline
    params:
      source_files:
        - $DEV_SOURCES" \
  --batch_size 1024 > $PRED_FILE
cd ..