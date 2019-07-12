import math
import os
import time
import csv
import numpy as np

def run(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

def get_lines(filepath):
    with open(filepath) as file_object:
        lines=file_object.readlines()
        return lines

def get_psnr(mse):
    log10 = math.log10
    return round(10.0*log10(float(255*255)/float(mse)), 2)

def psnr_get(video_res, source_video, out_video):
    # get yuv and compare psnr
    source_yuv = source_video.split('.')[0] + '.yuv'
    if os.path.exists(source_yuv) :
        pass
    else:
        yuv_cmdline = 'ffmpeg -y -i {}  -c:v rawvideo -vsync 0 {}'.format(source_video, source_yuv)
        print(yuv_cmdline)
        run(yuv_cmdline)

    out_yuv = out_video.split('.')[0] + '.yuv'
    ffmpeg_yuv_cmd = 'ffmpeg -y -i {} -c:v rawvideo -vsync 0 {}'.format(out_video, out_yuv)
    print(ffmpeg_yuv_cmd)
    run(ffmpeg_yuv_cmd)
    psnr_cmd = r'ffmpeg -s {} -i {} -s {} -i {} -lavfi psnr="stats_file=psnr.log" -f null /dev/null'.format(video_res,source_yuv, video_res,out_yuv) 
    print(psnr_cmd)
    run(psnr_cmd)                        
    time.sleep(1)

    os.remove(out_yuv)
    psnr_log_csv_name = os.path.split(out_yuv)[0] + '/'+"psnr_" + os.path.split(source_yuv)[1].split('.')[0] +'-'+ os.path.split(out_yuv)[1].split('.')[0] + '.csv'
    print(psnr_log_csv_name)
    if os.path.exists(psnr_log_csv_name):
        os.remove(psnr_log_csv_name)
    # exit(-1)
    lines = get_lines('psnr.log')
    list1 = [line.rstrip(' \n') for line in lines]
    total_mse = []
    with open(psnr_log_csv_name,'a') as csvfile:
        csv_writer=csv.writer(csvfile,dialect='excel')
        index = list1[0]
        lis = index.split(' ')
        index2 = [i.split(':')[0] for i in lis]
        csv_writer.writerow(index2)
    with open(psnr_log_csv_name,'a') as csvfile:
        for i in list1:
            csv_writer=csv.writer(csvfile,dialect='excel')
            data = i.split(' ')
            data = [j.split(':')[1] for j in data]
            y_mse_data = data[2]
            total_mse.append(float(y_mse_data))
            csv_writer.writerow(data)
    average_mse = np.sum(total_mse) / len(total_mse)
    y_psnr = get_psnr(average_mse)
    os.remove('psnr.log')
    return y_psnr