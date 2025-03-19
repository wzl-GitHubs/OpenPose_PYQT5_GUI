@echo off
:: call activate D:\ProgramData\Anaconda3\envs\tf1.14
call activate D:\ProgramData\Anaconda3\envs\tf1.14
e:
:: cd \openpose_test\lightweight_openpose-master\tets_eval
cd .
python app.py
cmd  /k